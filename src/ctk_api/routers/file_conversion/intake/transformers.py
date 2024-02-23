"""Contains the transformers for intake form conversion.

These transformers are used to create more complicated strings based on the
intake form data. It uses an abstract base class that enforces the creation of a
matches and transform method for each transformer. Each transformer should
be callable from the transform method alone, with the matches method being
used internally.
"""
import abc
from typing import Generic, TypeVar

import fastapi
from fastapi import status

from ctk_api.routers.file_conversion.intake import descriptors, utils

T = TypeVar("T")


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


class Handedness(Transformer[descriptors.Handedness]):
    """The transformer for handedness."""

    def __init__(self, value: descriptors.Handedness) -> None:
        """Initializes the handedness transformer."""
        super().__init__(descriptors.Handedness(value))

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

    def __init__(self, value: descriptors.IndividualizedEducationProgram) -> None:
        """Initializes the individualized education program transformer."""
        super().__init__(descriptors.IndividualizedEducationProgram(value))

    def transform(self) -> str:
        """Transforms the individualized education program information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base == descriptors.IndividualizedEducationProgram.yes:
            return "did not have an Individualized Education Program (IEP)"
        return "had an Individualized Education Program (IEP)"


class BirthComplications(
    MultiTransformer[descriptors.BirthComplications],
):
    """The transformer for birth complications."""

    def __init__(self, value: list[int]) -> None:
        """Initializes the pregnancy symptoms transformer."""
        super().__init__([descriptors.BirthComplications(val) for val in value])
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

        names = [val.name.replace("_", " ") for val in self.base]
        if len(names) == 1:
            return f"the following birth complication: {names[0]}"
        return "the following birth complications:" + ", and".join(
            ", ".join(
                [", ".join(names[:-1]), names[-1]],
            ),
        )


class BirthDelivery(Transformer[descriptors.BirthDelivery]):
    """The transformer for birth delivery."""

    def __init__(self, value: descriptors.BirthDelivery) -> None:
        """Initializes the birth delivery transformer."""
        self.base = descriptors.BirthDelivery(value)

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

    def __init__(self, value: descriptors.DeliveryLocation, other: str) -> None:
        """Initializes the birth location transformer."""
        self.base = descriptors.DeliveryLocation(value)
        self.other = other

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

    def __init__(self, value: descriptors.Adaptability) -> None:
        """Initializes the infant adaptability transformer."""
        self.base = descriptors.Adaptability(value)

    def transform(self) -> str:
        """Transforms the infant adaptability information to a string.

        Returns:
            str: The transformed object.
        """
        if self.base != descriptors.Adaptability.difficult:
            return "a slow to warm up temperament"
        return "an adaptable temperament"


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
        if self.base:
            return (
                "did not receive Committee on Preschool Special Education (CPSE) "
                "services"
            )
        return (
            "received Committee on Preschool Special Education (CPSE) services "
            f"starting at {self.base}"
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
            return "has not {self.other}"
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
            return "no prior history of psychiatric diagnoses"

        if short:
            return "a prior history of " + utils.join_with_oxford_comma(
                [val.diagnosis for val in self.base],
            )

        return (
            "was diagnosed with the following psychiatric diagnoses: "
            + utils.join_with_oxford_comma(
                [
                    f"{val.diagnosis} at age {val.age} by {val.clinician}"
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


class FamilyDiagnoses(MultiTransformer[descriptors.FamilyPsychiatricHistory]):
    """The transformer for family diagnoses."""

    def transform(self) -> str:
        """Transforms the family diagnoses information to a string.

        Returns:
            str: The transformed object.
        """
        no_past_diagnosis = [val for val in self.base if val.no_formal_diagnosis]
        past_diagnosis = [val for val in self.base if not val.no_formal_diagnosis]

        text = ""
        if len(past_diagnosis) > 0:
            text += "The following history of psychiatric diagnoses was reported: "
            past_diagosis_texts = [
                self._past_diagnosis_text(val) for val in past_diagnosis
            ]
            text += utils.join_with_oxford_comma(past_diagosis_texts)
            text += ". "

        if len(no_past_diagnosis) > 0:
            no_diagnosis_names = [val.diagnosis for val in no_past_diagnosis]
            text += (
                "Family history of the following diagnoses was denied: "
                + utils.join_with_oxford_comma(no_diagnosis_names)
            )
        return text

    @staticmethod
    def _past_diagnosis_text(diagnosis: descriptors.FamilyPsychiatricHistory) -> str:
        """Transforms a family diagnosis to a string.

        Args:
            diagnosis: The family diagnosis.

        Returns:
            str: The transformed object.
        """
        if len(diagnosis.family_members) == 0:
            return (
                f"a formal diagnosis of {diagnosis.diagnosis}, "
                "without any specified family members"
            )

        verb = "has" if len(diagnosis.family_members) == 1 else "have"
        return (
            f"the {utils.join_with_oxford_comma(diagnosis.family_members)} "
            f"{verb} a formal diagnosis of {diagnosis.diagnosis}"
        )
