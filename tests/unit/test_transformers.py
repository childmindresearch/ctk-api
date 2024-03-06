"""Tests for the textual output of intake transformers."""
import pytest

from ctk_api.routers.file_conversion.intake import descriptors, transformers


@pytest.mark.parametrize(
    ("iep", "expected"),
    [
        (
            descriptors.IndividualizedEducationProgram.yes,
            "had an Individualized Education Program (IEP)",
        ),
        (
            descriptors.IndividualizedEducationProgram.no,
            "did not have an Individualized Education Program (IEP)",
        ),
    ],
)
def test_individualized_education_program_transformer(
    iep: descriptors.IndividualizedEducationProgram,
    expected: str,
) -> None:
    """Test that the IEP transformer returns the expected strings."""
    transformer = transformers.IndividualizedEducationProgram(iep)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("value", "expected", "other"),
    [
        (
            [descriptors.BirthComplications.none_of_the_above],
            "no birth complications",
            None,
        ),
        (
            [descriptors.BirthComplications.spotting_or_vaginal_bleeding],
            "the following birth complication: spotting or vaginal bleeding",
            None,
        ),
        (
            [
                descriptors.BirthComplications.emotional_problems,
                descriptors.BirthComplications.diabetes,
            ],
            "the following birth complications: emotional problems and diabetes",
            None,
        ),
        (
            [descriptors.BirthComplications.other_illnesses],
            "the following birth complication: tester",
            "tester",
        ),
    ],
)
def test_birth_complications_transformer(
    value: list[int],
    expected: str,
    other: str | None,
) -> None:
    """Test that the BirthComplications transformer returns the expected strings."""
    transformer = transformers.BirthComplications(value, other)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            descriptors.BirthDelivery.unknown,
            "an unknown type of delivery",
        ),
        (
            descriptors.BirthDelivery.vaginal,
            "a vaginal delivery",
        ),
        (
            descriptors.BirthDelivery.cesarean,
            "a cesarean section",
        ),
    ],
)
def test_birth_delivery_transformer(
    value: descriptors.BirthDelivery,
    expected: str,
) -> None:
    """Test that the BirthDelivery transformer returns the expected strings."""
    transformer = transformers.BirthDelivery(value)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("value", "expected", "other"),
    [
        (
            descriptors.DeliveryLocation.other,
            "an unspecified location",
            None,
        ),
        (
            descriptors.DeliveryLocation.other,
            "test location",
            "test location",
        ),
        (
            descriptors.DeliveryLocation.hospital,
            "a hospital",
            None,
        ),
        (
            descriptors.DeliveryLocation.home,
            "home",
            None,
        ),
        (
            descriptors.DeliveryLocation.hospital,
            "a hospital",
            "should not appear",
        ),
    ],
)
def test_delivery_location_transformer(
    value: descriptors.DeliveryLocation,
    other: str | None,
    expected: str,
) -> None:
    """Test that the DeliveryLocation transformer returns the expected strings."""
    transformer = transformers.DeliveryLocation(value, other)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (
            descriptors.Adaptability.difficult,
            "a slow to warm up temperament",
        ),
        (
            descriptors.Adaptability.easy,
            "an adaptable temperament",
        ),
    ],
)
def test_adaptability_transformer(
    value: descriptors.Adaptability,
    expected: str,
) -> None:
    """Test that the Adaptability transformer returns the expected strings."""
    transformer = transformers.Adaptability(value)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            "did not receive Early Intervention (EI)",
        ),
        (
            "2022-01-01",
            "received Early Intervention (EI) starting at 2022-01-01",
        ),
    ],
)
def test_early_intervention_transformer(
    base: str,
    expected: str,
) -> None:
    """Test that the EarlyIntervention transformer returns the expected strings."""
    transformer = transformers.EarlyIntervention(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            "did not receive Committee on Preschool Special Education (CPSE) services",
        ),
        (
            "2022-01-01",
            (
                "received Committee on Preschool Special Education (CPSE) services "
                'starting at "2022-01-01"'
            ),
        ),
    ],
)
def test_cpse_transformer(
    base: str,
    expected: str,
) -> None:
    """Test that the CPSE transformer returns the expected strings."""
    transformer = transformers.CPSE(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ([], "no prior history of schools"),
        (
            [
                transformers.PastSchoolInterface(name="School A", grades="1-5"),
                transformers.PastSchoolInterface(name="School B", grades="6-8"),
            ],
            (
                "attended the following schools: School A (grades: 1-5) and School B "
                "(grades: 6-8)"
            ),
        ),
    ],
)
def test_past_schools_transformer(
    base: list[transformers.PastSchoolInterface],
    expected: str,
) -> None:
    """Test that the PastSchools transformer returns the expected strings."""
    transformer = transformers.PastSchools(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            12,
            "talked at 12 months/years",
        ),
        (
            "not yet",
            "has not talked yet",
        ),
        (
            "normal",
            "talked at a normal age",
        ),
        (
            "late",
            "talked at a late age",
        ),
        (
            "early",
            "talked at an early age",
        ),
        (
            "2022-01-01",
            "talked at 2022-01-01",
        ),
    ],
)
def test_development_skill_transformer(
    base: str | int,
    expected: str,
) -> None:
    """Test that the DevelopmentSkill transformer returns the expected strings."""
    other = "talked"
    transformer = transformers.DevelopmentSkill(base, other)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected", "short"),
    [
        ([], "no prior history of psychiatric diagnoses", False),
        (
            [
                descriptors.PastDiagnosis(
                    diagnosis="Anxiety",
                    date="2022-01-01",
                    clinician="Dr. Smith",
                ),
                descriptors.PastDiagnosis(
                    diagnosis="Depression",
                    date="2022-02-01",
                    clinician="Dr. Johnson",
                ),
            ],
            (
                "was diagnosed with the following psychiatric diagnoses: Anxiety on "
                "2022-01-01 by Dr. Smith and Depression on 2022-02-01 by Dr. Johnson"
            ),
            False,
        ),
        (
            [
                descriptors.PastDiagnosis(
                    diagnosis="Anxiety",
                    date="2022-01-01",
                    clinician="Dr. Smith",
                ),
                descriptors.PastDiagnosis(
                    diagnosis="Depression",
                    date="2022-02-01",
                    clinician="Dr. Johnson",
                ),
            ],
            ("a prior history of Anxiety and Depression"),
            True,
        ),
    ],
)
def test_past_diagnoses_transformer(
    base: list[descriptors.PastDiagnosis],
    expected: str,
    short: bool,
) -> None:
    """Test that the PastDiagnoses transformer returns the expected strings."""
    transformer = transformers.PastDiagnoses(base)

    actual = transformer.transform(short=short)

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected", "other"),
    [
        (
            descriptors.HouseholdRelationship.other_relative,
            "unspecified relationship",
            None,
        ),
        (
            descriptors.HouseholdRelationship.other_relative,
            "test relationship",
            "test relationship",
        ),
        (
            descriptors.HouseholdRelationship.brother,
            "brother",
            None,
        ),
    ],
)
def test_household_relationship_transformer(
    base: descriptors.HouseholdRelationship,
    expected: str,
    other: str | None,
) -> None:
    """Test that the HouseholdRelationship transformer returns the expected strings."""
    transformer = transformers.HouseholdRelationship(base, other)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        ([], ""),
        (
            [
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Anxiety",
                    family_members=["Mother", "Father"],
                    no_formal_diagnosis=False,
                ),
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Depression",
                    family_members=["Brother"],
                    no_formal_diagnosis=False,
                ),
            ],
            (
                "{{PREFERRED_NAME}}'s family history is significant for Anxiety ("
                "mother and father) and Depression (brother)."
            ),
        ),
        (
            [
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Anxiety",
                    family_members=[],
                    no_formal_diagnosis=False,
                ),
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Depression",
                    family_members=[],
                    no_formal_diagnosis=False,
                ),
            ],
            (
                "{{PREFERRED_NAME}}'s family history is significant for "
                "Anxiety and Depression."
            ),
        ),
        (
            [
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Anxiety",
                    family_members=[],
                    no_formal_diagnosis=True,
                ),
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Depression",
                    family_members=[],
                    no_formal_diagnosis=True,
                ),
            ],
            (
                "Family history of the following diagnoses was denied: Anxiety and "
                "Depression."
            ),
        ),
        (
            [
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Anxiety",
                    family_members=[],
                    no_formal_diagnosis=True,
                ),
                descriptors.FamilyPsychiatricHistory(
                    diagnosis="Depression",
                    family_members=["brother"],
                    no_formal_diagnosis=False,
                ),
            ],
            (
                "{{PREFERRED_NAME}}'s family history is significant for Depression "
                "(brother). Family history of Anxiety was denied."
            ),
        ),
    ],
)
def test_family_diagnoses_transformer(
    base: list[descriptors.FamilyPsychiatricHistory],
    expected: str,
) -> None:
    """Test that the FamilyDiagnoses transformer returns the expected strings."""
    transformer = transformers.FamilyDiagnoses(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            (
                "{{REPORTING_GUARDIAN}} denied any history of violence or trauma for "
                "{{PREFERRED_NAME}}."
            ),
        ),
        (
            "test history",
            '{{REPORTING_GUARDIAN}} reported that "test history".',
        ),
    ],
)
def test_violence_and_trauma_transformer_no_history(base: str, expected: str) -> None:
    """Test that the ViolenceAndTrauma transformer returns the expected strings."""
    transformer = transformers.ViolenceAndTrauma(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            (
                "{{REPORTING_GUARDIAN}} denied any history of homicidality or "
                "severe physically aggressive behaviors towards others for "
                "{{PREFERRED_NAME}}."
            ),
        ),
        (
            "test history",
            '{{REPORTING_GUARDIAN}} reported that "test history".',
        ),
    ],
)
def test_aggressive_behavior_transformer(base: str, expected: str) -> None:
    """Test that the AggressiveBehavior transformer returns the expected strings."""
    transformer = transformers.AggressiveBehavior(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            (
                "{{REPORTING_GUARDIAN}} denied any history of ACS involvement for "
                "{{PREFERRED_NAME}}."
            ),
        ),
        (
            "test history",
            '{{REPORTING_GUARDIAN}} reported that "test history".',
        ),
    ],
)
def test_children_services_transformer(base: str, expected: str) -> None:
    """Test that the ChildrenServices transformer returns the expected strings."""
    transformer = transformers.ChildrenServices(base)

    actual = transformer.transform()

    assert actual == expected


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (
            "",
            (
                "{{REPORTING_GUARDIAN}} denied any history of serious self-injurious"
                " harm or suicidal ideation for {{PREFERRED_NAME}}"
            ),
        ),
        (
            "test history",
            '{{REPORTING_GUARDIAN}} reported that "test history".',
        ),
    ],
)
def test_self_harm(base: str, expected: str) -> None:
    """Test that the SelfHarm transformer returns the expected strings."""
    transformer = transformers.SelfHarm(base)

    actual = transformer.transform()

    assert actual == expected