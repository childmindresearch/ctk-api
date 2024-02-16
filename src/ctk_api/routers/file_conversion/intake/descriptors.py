"""Contains descriptors of the columns of the REDCap intake form."""
import enum

import pydantic


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

    he_him_his_his_himself = 1
    she_her_her_hers_herself = 2
    they_them_their_theirs_themselves = 3
    ze_zir_zir_zirs_zirself = 4
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


class PastDiagnosis(pydantic.BaseModel):
    """The model for the patient's past diagnosis."""

    diagnosis: str
    clinician: str
    age: str


class FamilyDiagnosis(pydantic.BaseModel):
    """The model for a family diagnosis."""

    name: str
    checkbox_abbreviation: str
    text_abbreviation: str


family_psychiatric_diagnoses = [
    FamilyDiagnosis(
        name="attention deficit hyperactivity disorder",
        checkbox_abbreviation="adhd",
        text_abbreviation="adhd",
    ),
    FamilyDiagnosis(
        name="alcohol abuse",
        checkbox_abbreviation="aa",
        text_abbreviation="aa",
    ),
    FamilyDiagnosis(
        name="autism",
        checkbox_abbreviation="autism",
        text_abbreviation="autism",
    ),
    FamilyDiagnosis(
        name="bipolar disorder",
        checkbox_abbreviation="bipolar",
        text_abbreviation="bipolar",
    ),
    FamilyDiagnosis(
        name="conduct disorder",
        checkbox_abbreviation="conduct",
        text_abbreviation="conduct",
    ),
    FamilyDiagnosis(
        name="depression",
        checkbox_abbreviation="depression",
        text_abbreviation="depression",
    ),
    FamilyDiagnosis(
        name="disruptive mood dysregulation disorder",
        checkbox_abbreviation="dmdd",
        text_abbreviation="dmdd",
    ),
    FamilyDiagnosis(
        name="eating disorders",
        checkbox_abbreviation="eating",
        text_abbreviation="eating",
    ),
    FamilyDiagnosis(
        name="enuresis/encopresis",
        checkbox_abbreviation="enuresis_encopresis",
        text_abbreviation="ee",
    ),
    FamilyDiagnosis(
        name="excoriation",
        checkbox_abbreviation="excoriation",
        text_abbreviation="exco",
    ),
    FamilyDiagnosis(
        name="gender dysphoria",
        checkbox_abbreviation="gender",
        text_abbreviation="gender",
    ),
    FamilyDiagnosis(
        name="generalized anxiety disorder",
        checkbox_abbreviation="gad",
        text_abbreviation="genanx",
    ),
    FamilyDiagnosis(
        name="intellectual disability",
        checkbox_abbreviation="intellectual",
        text_abbreviation="id",
    ),
    FamilyDiagnosis(
        name="language disorder",
        checkbox_abbreviation="language_disorder",
        text_abbreviation="ld",
    ),
    FamilyDiagnosis(
        name="OCD",
        checkbox_abbreviation="ocd",
        text_abbreviation="ocd",
    ),
    FamilyDiagnosis(
        name="oppositional defiant disorder",
        checkbox_abbreviation="odd",
        text_abbreviation="odd",
    ),
    FamilyDiagnosis(
        name="panic disorder",
        checkbox_abbreviation="panic",
        text_abbreviation="panic",
    ),
    FamilyDiagnosis(
        name="personality disorder",
        checkbox_abbreviation="personality",
        text_abbreviation="personality",
    ),
    FamilyDiagnosis(
        name="psychosis",
        checkbox_abbreviation="psychosis",
        text_abbreviation="psychosis",
    ),
    FamilyDiagnosis(
        name="PTSD",
        checkbox_abbreviation="ptsd",
        text_abbreviation="ptsd",
    ),
    FamilyDiagnosis(
        name="reactive attachment",
        checkbox_abbreviation="rad",
        text_abbreviation="rad",
    ),
    FamilyDiagnosis(
        name="selective mutism",
        checkbox_abbreviation="selective_mutism",
        text_abbreviation="selective",
    ),
    FamilyDiagnosis(
        name="separation anxiety",
        checkbox_abbreviation="separation_anx",
        text_abbreviation="sa",
    ),
    FamilyDiagnosis(
        name="social anxiety",
        checkbox_abbreviation="social_anx",
        text_abbreviation="social",
    ),
    FamilyDiagnosis(
        name="specific learning disorder, with impairment in mathematics",
        checkbox_abbreviation="sld_math",
        text_abbreviation="sldmath",
    ),
    FamilyDiagnosis(
        name="specific learning disorder, with impairment in reading",
        checkbox_abbreviation="sld_read",
        text_abbreviation="sldread",
    ),
    FamilyDiagnosis(
        name="specific learning disorder, with impairment in written expression",
        checkbox_abbreviation="sld_write",
        text_abbreviation="sldexp",
    ),
    FamilyDiagnosis(
        name="specific phobias",
        checkbox_abbreviation="phobias",
        text_abbreviation="spho",
    ),
    FamilyDiagnosis(
        name="substance abuse",
        checkbox_abbreviation="substance",
        text_abbreviation="suba",
    ),
    FamilyDiagnosis(
        name="suicide",
        checkbox_abbreviation="suicide",
        text_abbreviation="suicide",
    ),
    FamilyDiagnosis(
        name="tics/Tourette's",
        checkbox_abbreviation="tic_tourette",
        text_abbreviation="tt",
    ),
]


class FamilyPsychiatricHistory(pydantic.BaseModel):
    """The model for the patient's family psychiatric history."""

    diagnosis: str
    no_formal_diagnosis: bool
    family_members: list[str]

    @pydantic.validator("family_members", pre=True)
    def split_comma_separated_values(cls, value: str | list[str] | None) -> list[str]:  # noqa: N805
        """Splits comma separated values."""
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return value.split(",")
