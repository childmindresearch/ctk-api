"""Contains descriptors of the columns of the REDCap intake form."""
import enum


class Gender(enum.Enum):
    """The gender of the patient."""

    male = 1
    female = 2
    non_binary = 3
    transgender_male = 4
    transgender_female = 5
    other = 6


class Pronouns(enum.Enum):
    """The pronouns of the patient."""

    he_him_his = 1
    she_her_hers = 2
    they_them_theirs = 3
    ze_zir_zirs = 4
    other = 5


class Handedness(enum.Enum):
    """The dominant hand of the patient."""

    left = 1
    right = 2
    unknown = 3


class SchoolType(enum.Enum):
    """The type of school the patient attends."""

    boarding = 1
    home = 2
    parochial = 3
    private = 4
    public = 5
    special = 6
    vocational = 7
    charter = 8
    other = 9


class IndividualizedEducationProgram(enum.Enum):
    """The type of education program the patient is in."""

    no = 0
    yes = 1


class BirthDelivery(enum.Enum):
    """The type of delivery the patient had."""

    vaginal = 1
    cesarean = 2
    unknown = 3


class DeliveryLocation(enum.Enum):
    """The location of the patient's birth."""

    hospital = 1
    home = 2
    other = 3


class Adaptability(enum.Enum):
    """The adaptability of the patient during infancy."""

    easy = 1
    difficult = 2


class SoothingDifficulty(enum.Enum):
    """The difficulty of soothing the patient during infancy."""

    easy = 1
    difficult = 2


class BirthComplications(enum.Enum):
    """The birth complications experienced by the patient."""

    spotting_or_vaginal_bleeding = 1
    emotional_problems = 2
    threatened_miscarriage = 3
    diabetes = 4
    high_blood_pressure = 5
    pre_term_labor = 6
    kidney_disease = 7
    took_any_prescriptions = 8
    drug_use = 9
    alcohol_use = 10
    tobacco_use = 11
    swollen_ankles = 12
    placenta_previa = 13
    family_stress = 14
    rh_or_other_incompatibilities = 15
    flu_or_virus = 16
    accident_or_injury = 17
    bedrest = 18
    other_illnesses = 19
    none_of_the_above = 20
