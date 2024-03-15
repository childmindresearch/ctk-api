"""Contains the transformers for intake form conversion.

These transformers are used to create more complicated strings based on the
intake form data. It uses an abstract base class that enforces the creation of a
matches and transform method for each transformer. Each transformer should
be callable from the transform method alone, with the matches method being
used internally.
"""
import abc
import dataclasses
import enum
from typing import Generic, TypeVar

import fastapi
from fastapi import status

from ctk_api.routers.file_conversion.intake import descriptors, utils

T = TypeVar("T")


class ReplacementTags(str, enum.Enum):
    """These tags will be replaced with the actual values in the final report."""

    PREFERRED_NAME = "{{PREFERRED_NAME}}"
    REPORTING_GUARDIAN = "{{REPORTING_GUARDIAN}}"


class Transformer(Generic[T], abc.ABC):
    """Base class for transformers.

    Transformers are used to match and transform objects based on certain conditions.
    These are used to generalize the process of handling complicated cases for the
    parent intake form conversions.
    """

    def __init__(self, value: T, other: None | str = None) -> None:
        """Initializes the transformer.

        Args:
            value: The value to be transformed.
            other: Specifier for a freeform value.
        """
        self.base = value
        self.other = other

    def __str__(self) -> str:
        """Returns the transformed object.

        This is overwritten as accidentally printing the object, rather than the
        transformed object, is an easy mistake to make but should rarely, if ever, be
        done.
        """
        return self.transform()

    @abc.abstractmethod
    def transform(self) -> str:
        """Transforms the given object.

        Args:
            obj: The object to be transformed.

        Returns:
            T: The transformed object.
        """
        ...


class MultiTransformer(Transformer[list[T]]):
    """A transformer that can handle multiple values."""

    def __init__(self, value: list[T], other: None | str = None) -> None:
        """Initializes the multi transformer."""
        self.base = value
        self.other = other

    def __str__(self) -> str:
        """Returns the transformed object.

        This is overwritten as accidentally printing the object, rather than the
        transformed object, is an easy mistake to make but should rarely, if ever, be
        done.
        """
        return self.transform()

    @abc.abstractmethod
    def transform(self) -> str:
        """Transforms the given object.

        Args:
            obj: The object to be transformed.

        Returns:
            T: The transformed object.
        """
        ...


class Handedness(Transformer[descriptors.Handedness]):
    """The transformer for handedness."""

    def transform(self) -> str:
        """Transforms the handedness information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.Handedness.unknown:
            return ""
        return f"{self.base.name}-handed"


class IndividualizedEducationProgram(
    Transformer[descriptors.IndividualizedEducationProgram],
):
    """The transformer for individualized education programs."""

    def transform(self) -> str:
        """Transforms the individualized education program information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.IndividualizedEducationProgram.no:
            return "did not have an Individualized Education Program (IEP)"
        return "had an Individualized Education Program (IEP)"


class BirthComplications(
    MultiTransformer[descriptors.BirthComplications],
):
    """The transformer for birth complications."""

    def __init__(self, value: list[int], other: str | None = None) -> None:
        """Initializes the pregnancy symptoms transformer.

        Args:
            value: The birth complication enum values.
            other: Specifier for a freeform value.

        """
        super().__init__([descriptors.BirthComplications(val) for val in value], other)
        if (
            descriptors.BirthComplications.none_of_the_above in self.base
            and len(self.base) > 1
        ):
            raise fastapi.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Birth complications 'none of the above' cannot be combined with "
                    "other birth complications."
                ),
            )

    def transform(self) -> str:
        """Transforms the birth complications information to a string.

        Returns:
            str: The transformed object.
        """
        if descriptors.BirthComplications.none_of_the_above in self.base:
            return "no birth complications"

        names = []
        for val in self.base:
            if val == descriptors.BirthComplications.other_illnesses:
                if self.other is None:
                    raise fastapi.HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Other illness must have a value.",
                    )
                names.append(self.other)
            else:
                names.append(val.name.replace("_", " "))
        if len(names) == 1:
            return f"the following birth complication: {names[0]}"
        return "the following birth complications: " + utils.join_with_oxford_comma(
            names,
        )


class DurationOfPregnancy(Transformer[str]):
    """The transfomer for time of pregnancy."""

    def transform(self) -> str:
        """Transforms the time of pregnancy information to a string.

        Though most guardians answer with just a number, the field is a freeform string.
        This transformer attempts to wrangle the data into a consistent format of
        "X weeks", but will return to the quoted original string if it can't.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return "unspecified"
        try:
            duration_of_pregnancy = float(self.base)
        except ValueError:
            parts = self.base.split()
            if len(parts) == 2 and parts[0].isnumeric() and parts[1].lower() == "weeks":  # noqa: PLR2004
                # Common edge case: guardian writes "40 weeks".
                # This doesn't need additional quotes.
                return self.base.lower()
            return f'"{self.base}"'
        return f"{duration_of_pregnancy:g} weeks"


class BirthDelivery(Transformer[descriptors.BirthDelivery]):
    """The transformer for birth delivery."""

    def transform(self) -> str:
        """Transforms the birth delivery information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.BirthDelivery.unknown:
            return "an unknown type of delivery"
        if self.base == descriptors.BirthDelivery.vaginal:
            return "a vaginal delivery"
        return "a cesarean section"


class DeliveryLocation(Transformer[descriptors.DeliveryLocation]):
    """The transformer for birth location."""

    def transform(self) -> str:
        """Transforms the birth location information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.DeliveryLocation.other:
            if self.other is None:
                return "an unspecified location"
            return self.other

        if self.base == descriptors.DeliveryLocation.hospital:
            return "a hospital"
        return "home"


class Adaptability(Transformer[descriptors.Adaptability]):
    """The transformer for infant adaptability."""

    def transform(self) -> str:
        """Transforms the infant adaptability information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.Adaptability.difficult:
            return "a slow to warm up temperament"
        return "an adaptable temperament"


class GuardianMaritalStatus(Transformer[descriptors.GuardianMaritalStatus]):
    """The transformer for guardian marital status."""

    def transform(self) -> str:
        """Transforms the guardian marital status information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.GuardianMaritalStatus.domestic_partnership:
            return "The parents/guardians are in a domestic partnership"
        if self.base == descriptors.GuardianMaritalStatus.widowed:
            return "The parent/guardian is widowed"
        if self.base == descriptors.GuardianMaritalStatus.never_married:
            return "The parents/guardians were never married"
        return f"The parents/guardians are {self.base.name.replace('_', ' ')}"


class EarlyIntervention(Transformer[str]):
    """The transformer for early intervention."""

    def transform(self) -> str:
        """Transforms the early intervention information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return "did not receive Early Intervention (EI)"
        return f"received Early Intervention (EI) starting at {self.base}"


class CPSE(Transformer[str]):
    """The transformer for CPSE."""

    def transform(self) -> str:
        """Transforms the CPSE information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return (
                "did not receive Committee on Preschool Special Education (CPSE) "
                "services"
            )
        return (
            "received Committee on Preschool Special Education (CPSE) services "
            f'starting at "{self.base}"'
        )


class ClassroomType(Transformer[descriptors.ClassroomType]):
    """The transformer for classroom type."""

    def transform(self) -> str:
        """Transforms the classroom type information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.ClassroomType.other:
            if self.other is None:
                return "an unspecified classroom type"
            return self.other

        return self.base.name.replace("_", " ").replace("COLON", ":").strip()


@dataclasses.dataclass
class PastSchoolInterface:
    """Interface for past school class.

    Needed to prevent circular import from parsers.
    """

    name: str
    grades: str


class PastSchools(MultiTransformer[PastSchoolInterface]):
    """The transformer for past schools."""

    def transform(self) -> str:
        """Transforms the past schools information to a string.

        Returns:
            str: The transformed object.
        """
        if len(self.base) == 0:
            return "no prior history of schools"
        substrings = [f"{val.name} (grades: {val.grades})" for val in self.base]
        return "attended the following schools: " + utils.join_with_oxford_comma(
            substrings,
        )


class DevelopmentSkill(Transformer[str | int]):
    """The transformer for developmental skills."""

    def transform(self) -> str:
        """Transforms the developmental skills information to a string.

        Returns:
            str: The transformed object.
        """
        if isinstance(self.base, int) or self.base.isnumeric():
            return f"{self.other} at {self.base} months/years"
        if self.base.lower() == "not yet":
            return f"has not {self.other} yet"
        if self.base.lower() in ["normal", "late"]:
            return f"{self.other} at a {self.base.lower()} age"
        if self.base.lower() == "early":
            return f"{self.other} at an early age"
        return f"{self.other} at {self.base}"


class PastDiagnoses(MultiTransformer[descriptors.PastDiagnosis]):
    """The transformer for past diagnoses."""

    def transform(self, *, short: bool = True) -> str:
        """Transforms the past diagnoses information to a string.

        Args:
            short: Whether to use the short form of the string.

        Returns:
            str: The transformed object.
        """
        if len(self.base) == 0:
            return "with no prior history of psychiatric diagnoses"

        if short:
            return "with a prior history of " + utils.join_with_oxford_comma(
                [val.diagnosis for val in self.base],
            )

        return (
            "was diagnosed with the following psychiatric diagnoses: "
            + utils.join_with_oxford_comma(
                [
                    f"{val.diagnosis} at {val.age} by {val.clinician}"
                    for val in self.base
                ],
            )
        )


class HouseholdRelationship(Transformer[descriptors.HouseholdRelationship]):
    """The transformer for household members."""

    def transform(self) -> str:
        """Transforms the household member information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.HouseholdRelationship.other_relative:
            return self.other if self.other else "unspecified relationship"
        return self.base.name.replace("_", " ")


class ViolenceAndTrauma(Transformer[str]):
    """Transformer for the violence and trauma information."""

    def transform(self) -> str:
        """Transforms the violence and trauma information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return (
                "{{REPORTING_GUARDIAN}} denied any history of violence or trauma for "
                "{{PREFERRED_NAME}}."
            )
        return "{{REPORTING_GUARDIAN}} reported that " + f'"{self.base}".'


class AggressiveBehavior(Transformer[str]):
    """Transformer for the aggressive behavior information."""

    def transform(self) -> str:
        """Transforms the aggressive behavior information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return (
                "{{REPORTING_GUARDIAN}} denied any history of homicidality or "
                "severe physically aggressive behaviors towards others for "
                "{{PREFERRED_NAME}}."
            )
        return "{{REPORTING_GUARDIAN}} reported that " + f'"{self.base}".'


class ChildrenServices(Transformer[str]):
    """Transformer for the children services information."""

    def transform(self) -> str:
        """Transforms the children services information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return (
                "{{REPORTING_GUARDIAN}} denied any history of ACS involvement for "
                "{{PREFERRED_NAME}}."
            )
        return "{{REPORTING_GUARDIAN}} reported that " + f'"{self.base}".'


class SelfHarm(Transformer[str]):
    """Transformer for the self harm information."""

    def transform(self) -> str:
        """Transforms the self harm information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.base:
            return (
                "{{REPORTING_GUARDIAN}} denied any history of serious self-injurious"
                " harm or suicidal ideation for {{PREFERRED_NAME}}"
            )
        return "{{REPORTING_GUARDIAN}} reported that " + f'"{self.base}".'
