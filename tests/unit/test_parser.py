"""Tests the intake form parser."""
import dataclasses
import pathlib
from typing import Any

import pytest

from ctk_api.routers.file_conversion.intake import descriptors, parser, utils


@pytest.fixture()
def test_data(data_dir: pathlib.Path) -> dict[str, Any]:
    """Returns a dictionary of test data."""

    @dataclasses.dataclass
    class FastApiUploadFileMimic:
        file = data_dir / "test_redcap_data.csv"

    data_frame = utils.read_subject_row(FastApiUploadFileMimic, 1)  # type: ignore[arg-type]
    return data_frame.row(0, named=True)


def test_guardian_parser(
    test_data: dict[str, Any],
) -> None:
    """Tests the Guardian intake form parser."""
    expected_relationship = descriptors.GuardianRelationship(
        test_data["guardian_relationship___1"],
    ).name

    guardian = parser.Guardian(test_data)

    assert guardian.first_name == test_data["guardian_first_name"]
    assert guardian.last_name == test_data["guardian_last_name"]
    assert guardian.full_name == f"{guardian.first_name} {guardian.last_name}"
    assert guardian.relationship == expected_relationship


def test_guardian_parser_other_relationship(
    test_data: dict[str, Any],
) -> None:
    """Tests the Guardian intake form parser with an 'other' relationship."""
    test_data[
        "guardian_relationship___1"
    ] = descriptors.GuardianRelationship.other.value
    test_data["other_relation"] = "xkcd"

    guardian = parser.Guardian(test_data)

    assert guardian.relationship == test_data["other_relation"]


def test_household_parser(
    test_data: dict[str, Any],
) -> None:
    """Tests the Household intake form parser."""
    expected_marital_status = descriptors.GuardianMaritalStatus(
        test_data["guardian_maritalstatus"],
    ).name
    n_household_members = test_data["residing_number"]
    max_languages = 25
    n_languages = sum(
        [
            int(test_data[f"language___{index}"])
            for index in range(1, max_languages + 1)
        ],
    )

    household = parser.Household(test_data)

    assert household.city == test_data["city"]
    assert household.state == descriptors.USState(int(test_data["state"])).name
    assert household.guardian_marital_status == expected_marital_status
    assert len(household.members) == n_household_members
    assert len(household.languages) == n_languages


def test_language_parser(
    test_data: dict[str, Any],
) -> None:
    """Tests the Language intake form parser."""
    identifier = 1
    expected_fluency = descriptors.LanguageFluency(
        test_data[f"child_language{identifier}_fluency"],
    ).name

    language = parser.Language(test_data, identifier)

    assert language.name == test_data[f"child_language{identifier}"]
    assert language.spoken_whole_life == test_data[f"child_language{identifier}_spoken"]
    assert language.spoken_since_age == test_data[f"child_language{identifier}_age"]
    assert language.setting == test_data[f"child_language{identifier}_setting"]
    assert language.fluency == expected_fluency
