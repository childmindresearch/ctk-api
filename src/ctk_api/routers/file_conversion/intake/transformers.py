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

from ctk_api.routers.file_conversion.intake import descriptors

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
    def matches(self) -> bool:
        """Determines if the given object matches a certain condition.

        Args:
            obj: The object to be checked.

        Returns:
            bool: True if the object matches the condition, False otherwise.
        """
        ...

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

    def matches(self) -> bool:
        """Determines if handedness is known.

        Returns:
            bool: True if handedness is not unknown.
        """
        return self.base != descriptors.Handedness.unknown

    def transform(self) -> str:
        """Transforms the handedness information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
            return ""
        return f"{self.base.name}-handed"


class IndividualizedEducationProgram(
    Transformer[descriptors.IndividualizedEducationProgram],
):
    """The transformer for individualized education programs."""

    def __init__(self, value: descriptors.IndividualizedEducationProgram) -> None:
        """Initializes the individualized education program transformer."""
        super().__init__(descriptors.IndividualizedEducationProgram(value))

    def matches(self) -> bool:
        """Determines if the patient has an individualized education program.

        Returns:
            bool: True if the patient has an individualized education program.
        """
        return self.base == descriptors.IndividualizedEducationProgram.yes

    def transform(self) -> str:
        """Transforms the individualized education program information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
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

    def matches(self) -> bool:
        """Determines if the patient had birth complications.

        Returns:
            bool: True if the patient had birth complications.
        """
        return descriptors.BirthComplications.none_of_the_above not in self.base

    def transform(self) -> str:
        """Transforms the birth complications information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
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

    def matches(self) -> bool:
        """Determines if the patient's birth delivery is known.

        Returns:
            bool: True if the patient's birth delivery is not unknown.
        """
        return self.base != descriptors.BirthDelivery.unknown

    def transform(self) -> str:
        """Transforms the birth delivery information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
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

    def matches(self) -> bool:
        """Determines if the patient's birth location is known.

        Returns:
            bool: True if the patient's birth location is not unknown.
        """
        return self.base != descriptors.DeliveryLocation.other

    def transform(self) -> str:
        """Transforms the birth location information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
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

    def matches(self) -> bool:
        """Determines if the patient's adaptability is easy.

        Returns:
            bool: True if the patient's adaptability is easy.
        """
        return self.base == descriptors.Adaptability.easy

    def transform(self) -> str:
        """Transforms the infant adaptability information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
            return "a difficult temperament"
        return "an adaptable temperament"


class EarlyIntervention(Transformer[str]):
    """The transformer for early intervention."""

    def matches(self) -> bool:
        """Determines if the patient had early intervention.

        Returns:
            bool: True if the patient had early intervention.
        """
        return bool(self.base)

    def transform(self) -> str:
        """Transforms the early intervention information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
            return "did not receive Early Intervention (EI)"
        return f"received Early Intervention (EI) starting at {self.base}"


class CPSE(Transformer[str]):
    """The transformer for CPSE."""

    def matches(self) -> bool:
        """Determines if the patient had CPSE.

        Returns:
            bool: True if the patient had CPSE.
        """
        return bool(self.base)

    def transform(self) -> str:
        """Transforms the CPSE information to a string.

        Returns:
            str: The transformed object.
        """
        if not self.matches():
            return (
                "did not receive Committee on Preschool Special Education (CPSE) "
                "services"
            )
        return (
            "received Committee on Preschool Special Education (CPSE) services "
            f"starting at {self.base}"
        )
