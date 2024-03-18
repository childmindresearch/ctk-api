"""Unit tests for the intake form parser."""

from typing import Any

from ctk_api.routers.file_conversion.intake import descriptors, parser


def test_guardian_parser(
    test_redcap_data: dict[str, Any],
) -> None:
    """Tests the Guardian intake form parser."""
    expected_relationship = descriptors.GuardianRelationship(
        test_redcap_data["guardian_relationship___1"],
    ).name.replace("_", " ")

    guardian = parser.Guardian(test_redcap_data)

    assert guardian.first_name == test_redcap_data["guardian_first_name"]
    assert guardian.last_name == test_redcap_data["guardian_last_name"]
    assert guardian.full_name == f"{guardian.first_name} {guardian.last_name}"
    assert guardian.relationship == expected_relationship


def test_guardian_parser_other_relationship(
    test_redcap_data: dict[str, Any],
) -> None:
    """Tests the Guardian intake form parser with an 'other' relationship."""
    test_redcap_data["guardian_relationship___1"] = (
        descriptors.GuardianRelationship.other.value
    )
    test_redcap_data["other_relation"] = "xkcd"

    guardian = parser.Guardian(test_redcap_data)

    assert guardian.relationship == test_redcap_data["other_relation"]


def test_household_parser(
    test_redcap_data: dict[str, Any],
) -> None:
    """Tests the Household intake form parser."""
    expected_marital_status = descriptors.GuardianMaritalStatus(
        test_redcap_data["guardian_maritalstatus"],
    ).name
    n_household_members = test_redcap_data["residing_number"]
    max_languages = 25
    n_languages = sum(
        [
            int(test_redcap_data[f"language___{index}"])
            for index in range(1, max_languages + 1)
        ],
    )

    household = parser.Household(test_redcap_data)

    assert household.city == test_redcap_data["city"]
    assert household.state == descriptors.USState(int(test_redcap_data["state"])).name
    assert household.guardian_marital_status == expected_marital_status
    assert len(household.members) == n_household_members
    assert len(household.languages) == n_languages


def test_language_parser(
    test_redcap_data: dict[str, Any],
) -> None:
    """Tests the Language intake form parser."""
    identifier = 1
    expected_fluency = descriptors.LanguageFluency(
        test_redcap_data[f"child_language{identifier}_fluency"],
    ).name

    language = parser.Language(test_redcap_data, identifier)

    assert language.name == test_redcap_data[f"child_language{identifier}"]
    assert (
        language.spoken_whole_life
        == test_redcap_data[f"child_language{identifier}_spoken"]
    )
    assert (
        language.spoken_since_age == test_redcap_data[f"child_language{identifier}_age"]
    )
    assert language.setting == test_redcap_data[f"child_language{identifier}_setting"]
    assert language.fluency == expected_fluency
