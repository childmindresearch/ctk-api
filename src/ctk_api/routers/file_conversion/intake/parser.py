"""Utilities for the file conversion router."""
import datetime
import math
from typing import Any

import polars as pl
import pytz

from ctk_api.routers.file_conversion.intake import descriptors, transformers


class IntakeInformation:
    """The extracts the intake information for a patient."""

    def __init__(
        self,
        patient_df: dict[str, Any],
        *,
        timezone: str = "US/Eastern",
    ) -> None:
        """Initializes the intake information.

        Args:
            patient_df: The patient dataframe.
            timezone: The timezone of the intake.
        """
        self.patient = Patient(patient_df)
        self.date_of_intake = datetime.datetime.strptime(
            patient_df["date"],
            "%m/%d/%y",
        ).replace(tzinfo=pytz.timezone(timezone))
        self.phone = patient_df["phone"]


class Patient:
    """The patient model."""

    def __init__(
        self,
        patient_df: dict[str, Any],
        timezone: str = "US/Eastern",
    ) -> None:
        """Initializes the patient.

        Args:
            patient_df: The patient dataframe.
            timezone: The timezone of the intake.
        """
        self.first_name = patient_df["firstname"]
        self.last_name = patient_df["lastname"]
        self.nickname = patient_df["othername"]
        self.age = math.floor(patient_df["age"])
        self.date_of_birth = datetime.datetime.strptime(
            patient_df["dob"],
            "%Y-%m-%d",
        ).replace(tzinfo=pytz.timezone(timezone))
        self._gender_enum = descriptors.Gender(patient_df["childgender"]).name
        self._gender_other = patient_df["childgender_other"]
        self._pronouns_enum = descriptors.Pronouns(patient_df["pronouns"]).name
        self._pronouns_other = patient_df["pronouns_other"]
        self.handedness = transformers.Handedness(patient_df["dominant_hand"])

        self.education = Education(patient_df)
        self.development = Development(patient_df)
        self.guardian = Guardian(patient_df)

    @property
    def full_name(self) -> str:
        """The full name of the patient."""
        if self.nickname:
            return f'{self.first_name} "{self.nickname}" {self.last_name}'
        return f"{self.first_name} {self.last_name}"

    @property
    def preferred_name(self) -> str:
        """The preferred name of the patient."""
        return self.nickname if self.nickname else self.first_name

    @property
    def gender(self) -> str:
        """The patient's gender."""
        if self._gender_enum == "other":
            return self._gender_other
        return self._gender_enum

    @property
    def pronouns(self) -> list[str]:
        """The patient's pronouns."""
        if self._pronouns_enum == "other":
            return self._pronouns_other.split("/")
        return self._pronouns_enum.split("_")


class Guardian:
    """The model for a parent or guardian."""

    def __init__(self, patient_df: pl.DataFrame) -> None:
        """Initializes the guardian.

        Args:
            patient_df: The patient dataframe.
        """
        self.first_name = patient_df["guardian_first_name"]
        self.last_name = patient_df["guardian_last_name"]

    @property
    def full_name(self) -> str:
        """The full name of the guardian."""
        return f"{self.first_name} {self.last_name}"


class Education:
    """The model for the patient's education."""

    def __init__(self, patient_df: dict[str, Any]) -> None:
        """Initializes the education.

        Args:
            patient_df: The patient dataframe.
        """
        self.years_of_education = patient_df["yrs_school"]
        self.school_name = patient_df["school"]
        self.grade = patient_df["grade"]
        self.individualized_educational_program = (
            transformers.IndividualizedEducationProgram(
                patient_df["iep"],
            )
        )
        self.school_type = descriptors.SchoolType(patient_df["schooltype"])


class Development:
    """The model for the patient's development history."""

    def __init__(self, patient_df: dict[str, Any]) -> None:
        """Initalizes the development history.

        Args:
            patient_df: The patient dataframe.
        """
        self.weeks_of_pregnancy = patient_df["txt_duration_preg_num"]
        self.delivery = transformers.BirthDelivery(patient_df["opt_delivery"])
        self.delivery_location = transformers.DeliveryLocation(
            patient_df["birth_location"],
            patient_df["birth_other"],
        )

        pregnancy_symptoms = [
            index
            for index in range(1, len(descriptors.BirthComplications) + 1)
            if patient_df[f"preg_symp___{index}"]
        ]
        self.birth_complications = transformers.BirthComplications(pregnancy_symptoms)
        self.premature_birth = bool(patient_df["premature"])
        self.premature_birth_specify = patient_df["premature_specify"]
        self.adaptability = transformers.Adaptability(patient_df["infanttemp_adapt"])
        self.soothing_difficulty = descriptors.SoothingDifficulty(
            patient_df["infanttemp1"],
        )
        self.early_intervention_age = transformers.EarlyIntervention(
            patient_df["ei_age"],
        )
        self.cpse_age = transformers.CPSE(patient_df["cpse_age"])
