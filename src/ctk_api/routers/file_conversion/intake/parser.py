"""Utilities for the file conversion router."""
import datetime
import math
from typing import Any

import pytz

from ctk_api.routers.file_conversion.intake import descriptors, transformers


class IntakeInformation:
    """The extracts the intake information for a patient."""

    def __init__(
        self,
        patient_data: dict[str, Any],
        *,
        timezone: str = "US/Eastern",
    ) -> None:
        """Initializes the intake information.

        Args:
            patient_data: The patient dataframe.
            timezone: The timezone of the intake.
        """
        self.patient = Patient(patient_data, timezone=timezone)
        self.phone = patient_data["phone"]


class Patient:
    """The patient model."""

    def __init__(
        self,
        patient_data: dict[str, Any],
        timezone: str = "US/Eastern",
    ) -> None:
        """Initializes the patient.

        Args:
            patient_data: The patient dataframe.
            timezone: The timezone of the intake.
        """
        self.first_name = patient_data["firstname"]
        self.last_name = patient_data["lastname"]
        self.nickname = patient_data["othername"]
        self.age = math.floor(patient_data["age"])
        self.date_of_birth = datetime.datetime.strptime(
            patient_data["dob"],
            "%Y-%m-%d",
        ).replace(tzinfo=pytz.timezone(timezone))
        self._gender_enum = descriptors.Gender(patient_data["childgender"]).name
        self._gender_other = patient_data["childgender_other"]
        self._pronouns_enum = descriptors.Pronouns(patient_data["pronouns"]).name
        self._pronouns_other = patient_data["pronouns_other"]
        self.handedness = transformers.Handedness(patient_data["dominant_hand"])

        self.referral = patient_data["referral2"]
        self.concerns = patient_data["concern_current"]
        self.concerns_start = str(patient_data["concerns_begin"])
        self.desired_outcome = patient_data["outcome2"]

        self.psychiatric_history = PsychiatricHistory(patient_data)

        self.languages = [
            Language(patient_data, identifier)
            for identifier in range(1, 3)
            if patient_data[f"child_language{identifier}"]
        ]
        self.language_spoken_best = descriptors.Language(
            patient_data["language_spoken"],
        ).name
        if self.language_spoken_best == "other":
            self.language_spoken_best = patient_data["language_spoken_other"]
        self.education = Education(patient_data)
        self.development = Development(patient_data)
        self.guardian = Guardian(patient_data)
        self.household = Household(patient_data)

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
        if self._pronouns_enum != "other":
            return self._pronouns_enum.split("_")

        pronouns = self._pronouns_other.split("/")
        defaults = [
            "he/she/they",
            "him/her/them",
            "his/her/their",
            "his/hers/theirs",
            "himself/herself/themselves",
        ]
        return pronouns + defaults[len(pronouns) :]

    @property
    def age_gender_label(self) -> str:
        """Converts the gender and age to an appropriate string."""
        child_age_cutoff = 15
        upper_age_cutoff = 18

        if self.age < child_age_cutoff:
            return (
                "girl"
                if "female" in self.gender
                else "boy"
                if "male" in self.gender
                else "child"
            )

        gender_string = (
            "woman"
            if "female" in self.gender
            else "man"
            if "male" in self.gender
            else "adult"
        )

        if self.age < upper_age_cutoff:
            return f"young {gender_string}"
        return gender_string


class Guardian:
    """The parser for a parent or guardian."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initializes the guardian.

        Args:
            patient_data: The patient dataframe.
        """
        self.first_name = patient_data["guardian_first_name"]
        self.last_name = patient_data["guardian_last_name"]
        relationship_id = patient_data["guardian_relationship___1"]
        if relationship_id == descriptors.GuardianRelationship.other.value:
            self.relationship = patient_data["other_relation"]
        else:
            self.relationship = descriptors.GuardianRelationship(
                relationship_id,
            ).name.replace("_", " ")

    @property
    def full_name(self) -> str:
        """The full name of the guardian."""
        return f"{self.first_name} {self.last_name}"


class Household:
    """The parser for household information."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initializes the household.

        Args:
            patient_data: The patient dataframe.
        """
        n_members = patient_data["residing_number"]
        self.members = [
            HouseholdMember(patient_data, i) for i in range(1, n_members + 1)
        ]
        self.guardian_marital_status = descriptors.GuardianMaritalStatus(
            patient_data["guardian_maritalstatus"],
        ).name
        self.city = patient_data["city"]

        self.state = descriptors.USState(int(patient_data["state"])).name
        self.languages = [
            descriptors.Language(identifier).name
            for identifier in range(1, 25)
            if patient_data[f"language___{identifier}"] == "1"
        ]
        if patient_data["language_other"]:
            self.languages.append(patient_data["language_other"])


class Language:
    """The parser for a language."""

    def __init__(self, patient_data: dict[str, Any], identifier: int) -> None:
        """Initializes the language.

        Args:
            patient_data: The patient dataframe.
            identifier: The id of the language.
        """
        self.name = patient_data[f"child_language{identifier}"]
        self.spoken_whole_life = patient_data[f"child_language{identifier}_spoken"]
        self.spoken_since_age = patient_data[f"child_language{identifier}_age"]
        self.setting = patient_data[f"child_language{identifier}_setting"]
        self.fluency = descriptors.LanguageFluency(
            patient_data[f"child_language{identifier}_fluency"],
        ).name


class HouseholdMember:
    """The parser for a household member."""

    def __init__(self, patient_data: dict[str, Any], identifier: int) -> None:
        """Initializes the household member.

        Args:
            patient_data: The patient dataframe.
            identifier: The id of the household member.
        """
        self.name = patient_data[f"peopleinhome{identifier}"]
        self.age = patient_data[f"peopleinhome{identifier}_age"]
        self.relationship = transformers.HouseholdRelationship(
            descriptors.HouseholdRelationship(
                patient_data[f"peopleinhome{identifier}_relation"],
            ),
            patient_data[f"peopleinhome{identifier}_relation_other"],
        ).transform()

        faulty_tag = 2  # Member 2's ID is missing in this field.
        if identifier != faulty_tag:
            self.relationship_quality = descriptors.RelationshipQuality(
                patient_data[f"peopleinhome{identifier}_relationship"],
            ).name
        else:
            self.relationship_quality = descriptors.RelationshipQuality(
                patient_data["peopleinhome_relationship"],
            ).name
        self.grade_occupation = patient_data[f"peopleinhome{identifier}_gradeocc"]


class Education:
    """The parser for the patient's education."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initializes the education.

        Args:
            patient_data: The patient dataframe.
        """
        self.years_of_education = patient_data["yrs_school"]
        self.school_name = patient_data["school"]
        self.grade = patient_data["grade"]
        self.individualized_educational_program = (
            transformers.IndividualizedEducationProgram(
                patient_data["iep"],
            )
        )
        self.school_type = descriptors.SchoolType(patient_data["schooltype"])
        self.past_schools = transformers.PastSchools(
            [
                transformers.PastSchoolInterface(
                    name=patient_data[f"pastschool{identifier}"],
                    grades=patient_data[f"pastschool{identifier}_grades"],
                )
                for identifier in range(1, 11)
                if patient_data[f"pastschool{identifier}"]
            ],
        )


class Development:
    """The parser for the patient's development history."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initalizes the development history.

        Args:
            patient_data: The patient dataframe.
        """
        self.weeks_of_pregnancy = patient_data["txt_duration_preg_num"]
        self.delivery = transformers.BirthDelivery(patient_data["opt_delivery"])
        self.delivery_location = transformers.DeliveryLocation(
            patient_data["birth_location"],
            patient_data["birth_other"],
        )

        pregnancy_symptoms = [
            index
            for index in range(1, len(descriptors.BirthComplications) + 1)
            if patient_data[f"preg_symp___{index}"] == "1"
        ]
        self.birth_complications = transformers.BirthComplications(pregnancy_symptoms)
        self.premature_birth = bool(patient_data["premature"])
        self.premature_birth_specify = patient_data["premature_specify"]
        self.adaptability = transformers.Adaptability(patient_data["infanttemp_adapt"])
        self.soothing_difficulty = descriptors.SoothingDifficulty(
            patient_data["infanttemp1"],
        )
        self.early_intervention_age = transformers.EarlyIntervention(
            patient_data["ei_age"],
        )
        self.cpse_age = transformers.CPSE(patient_data["cpse_age"])
        self.started_walking = transformers.DevelopmentSkill(
            patient_data["skill6"],
            other="started walking",
        )
        self.started_talking = transformers.DevelopmentSkill(
            patient_data["skill16"],
            other="started using meaningful words",
        )
        self.daytime_dryness = transformers.DevelopmentSkill(
            patient_data["skill12"],
            other="achieved daytime dryness",
        )
        self.nighttime_dryness = transformers.DevelopmentSkill(
            patient_data["skill13"],
            other="achieved nighttime dryness",
        )


class PsychiatricHistory:
    """The parser for the patient's psychiatric history."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initializes the psychiatric history.

        Args:
            patient_data: The patient dataframe.
        """
        past_diagnoses = [
            descriptors.PastDiagnosis(
                diagnosis=patient_data[f"pastdx_{index}"],
                clinician=patient_data[f"dx_name{index}"],
                date=str(patient_data[f"age_{index}"]),
            )
            for index in range(1, 11)
            if patient_data[f"pastdx_{index}"]
        ]
        self.past_diagnoses = transformers.PastDiagnoses(past_diagnoses)
        self.therapeutic_interventions = [
            TherapeuticInterventions(patient_data, identifier)
            for identifier in range(1, 11)
            if patient_data[
                f"txhx_{identifier}" if identifier != 2 else f"txhx{identifier}"  # noqa: PLR2004
            ]
        ]
        self.aggresive_behaviors = transformers.AggressiveBehavior(
            patient_data["agress_exp"],
        )
        self.children_services = transformers.ChildrenServices(
            patient_data["acs_exp"],
        )
        self.family_psychiatric_history = FamilyPyshicatricHistory(patient_data)
        self.violence_and_trauma = transformers.ViolenceAndTrauma(
            patient_data["violence_exp"],
        )
        self.self_harm = transformers.SelfHarm(patient_data["selfharm_exp"])


class FamilyPyshicatricHistory:
    """The parser for the patient's family's psychiatric history."""

    def __init__(self, patient_data: dict[str, Any]) -> None:
        """Initializes the psychiatric history.

        Args:
            patient_data: The patient dataframe.
        """
        self.is_father_history_known = bool(patient_data["biohx_dad_other"])
        self.is_mother_history_known = bool(patient_data["biohx_mom_other"])
        family_diagnoses = [
            descriptors.FamilyPsychiatricHistory(
                diagnosis=diagnosis.name,
                no_formal_diagnosis=patient_data[
                    f"{diagnosis.checkbox_abbreviation}___4"
                ]
                == "1",
                family_members=patient_data[f"{diagnosis.text_abbreviation}_text"],
            )
            for diagnosis in descriptors.family_psychiatric_diagnoses
        ]
        self.family_diagnoses = transformers.FamilyDiagnoses(family_diagnoses)


class TherapeuticInterventions:
    """The parser for the patient's therapeutic history."""

    def __init__(self, patient_data: dict[str, Any], identifier: int) -> None:
        """Initializes the therapeutic history.

        Args:
            patient_data: The patient dataframe.
            identifier: The id of the therapeutic history instance.
        """
        faulty_identifier = 2
        if identifier != faulty_identifier:
            self.therapist = patient_data[f"txhx_{identifier}"]
        else:
            self.therapist = patient_data[f"txhx{identifier}"]
        self.reason = patient_data[f"txhx{identifier}_reason"]
        self.start = patient_data[f"txhx{identifier}_start"]
        self.end = patient_data[f"txhx{identifier}_end"]
        self.frequency = patient_data[f"txhx{identifier}_freq"]
        self.effectiveness = patient_data[f"txhx{identifier}_effectiveness"]
        self.reason_ended = patient_data[f"txhx{identifier}_terminate"]
