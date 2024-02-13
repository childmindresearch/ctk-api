"""Contains report writing functionality for intake information."""
import functools
import tempfile
from collections.abc import Callable
from typing import ParamSpec, TypeVar

import docx
import fastapi
from docx.enum import text
from docxcompose import composer
from fastapi import status

from ctk_api.core import config
from ctk_api.routers.file_conversion.intake import docx_utils, parser

P = ParamSpec("P")
T = TypeVar("T")

DATA_DIR = config.DATA_DIR
RGB_INTAKE = (178, 161, 199)
RGB_TESTING = (155, 187, 89)
PLACEHOLDER = "_____________"


def write_with_rgb_text(
    rgb: tuple[int, int, int],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to format the report for a specific team with RGB codes.

    Clinicians use color to denote which section of the report is part of
    which procedure. This decorator applies the formatting to the runs of
    the new paragraphs created in the function. This assumes all paragraphs
    are appended to the end of the report. Only usable with the ReportWriter
    class.

    Args:
        func: The function to decorate.
        rgb: The RGB code to use for the formatting.

    Returns:
        The decorated function.
    """

    def decorator(
        func: Callable[P, T],
    ) -> Callable[P, T]:
        """Decorator to format the report for a specific team.

        Args:
            func: The function to decorate.

        Returns:
            The decorated function.
        """

        @functools.wraps(func)
        def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> T:
            if not isinstance(args[0], ReportWriter):
                msg = "This decorator is only usable with the ReportWriter class."
                raise fastapi.HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=msg,
                )

            self: ReportWriter = args[0]  # type: ignore[assignment]
            n_paragraphs_before = len(self.report.paragraphs)
            output = func(*args, **kwargs)
            n_paragraphs_after = len(self.report.paragraphs)
            for paragraph in self.report.paragraphs[
                n_paragraphs_before:n_paragraphs_after
            ]:
                for para_run in paragraph.runs:
                    para_run.font.color.rgb = docx.shared.RGBColor(*rgb)

            return output

        return wrapper

    return decorator


class ReportWriter:
    """Writes a report for intake information."""

    def __init__(self, intake: parser.IntakeInformation) -> None:
        """Initializes the report writer.

        Args:
            intake: The intake information.
        """
        self.intake = intake
        self.report = docx.Document(DATA_DIR / "report_template.docx")
        self.report_closing_statement = docx.Document(
            DATA_DIR / "report_template_closing_statement.docx",
        )

    def replace_patient_information(self) -> None:
        """Replaces the patient information in the report."""
        replacements = {
            "full_name": self.intake.patient.full_name,
            "preferred_name": self.intake.patient.preferred_name,
            "date_of_birth": self.intake.patient.date_of_birth.strftime("%m/%d/%Y"),
            "date_of_intake": self.intake.date_of_intake.strftime("%m/%d/%Y"),
            "reporting_guardian": self.intake.patient.guardian.full_name,
        }

        for template, replacement in replacements.items():
            template_formatted = "{{" + template.upper() + "}}"
            docx_utils.DocxReplace(self.report).replace(template_formatted, replacement)

    @write_with_rgb_text(RGB_INTAKE)
    def write_reason_for_visit(self) -> None:
        """Writes the reason for visit to the end of the report."""
        patient = self.intake.patient
        handedness = patient.handedness.transform()
        iep = patient.education.individualized_educational_program.transform()
        past_diagnoses = patient.past_diagnoses.transform()
        gender = self._gender_and_age_to_string()
        concerns = f'"{patient.concerns}"' if patient.concerns else PLACEHOLDER
        referral = f'"{patient.referral}"' if patient.referral else PLACEHOLDER
        desired_outcome = (
            f'"{patient.desired_outcome}"' if patient.desired_outcome else PLACEHOLDER
        )

        text = f"""
            At the time of enrollment, {patient.preferred_name} was a
            {patient.age}-year-old, {handedness} {gender} with {past_diagnoses}.
            {patient.preferred_name} was placed in a
            {patient.education.school_type.name} school grade
            {patient.education.grade} classroom at
            {patient.education.school_name}. {patient.preferred_name} {iep}.
            {patient.preferred_name} and {patient.pronouns[2]} mother/father,
            Mr./Ms./Mrs. Parentfirstname Parentlastname, attended the present
            evaluation due to concerns regarding {concerns}. The family is
            hoping for {desired_outcome}. The family learned of the study/was
            referred to the study through {referral}.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("REASON FOR VISIT", level=1)
        self.report.add_paragraph(text)

    @write_with_rgb_text(RGB_INTAKE)
    def write_developmental_history(self) -> None:
        """Writes the developmental history to the end of the report."""
        self.report.add_heading("DEVELOPMENTAL HISTORY", level=1)
        self.write_prenatal_history()
        self.write_developmental_milestones()
        self.write_early_education()

    def write_prenatal_history(self) -> None:
        """Writes the prenatal and birth history of the patient to the report."""
        patient = self.intake.patient
        development = patient.development
        pregnancy_symptoms = development.birth_complications.transform()
        delivery = development.delivery.transform()
        delivery_location = development.delivery_location.transform()
        adaptability = development.adaptability.transform()

        text = f"""
            {patient.guardian.full_name} reported {pregnancy_symptoms}.
            {patient.preferred_name} was born at
            {development.weeks_of_pregnancy} of gestation with {delivery} at
            {delivery_location}. {patient.preferred_name} had {adaptability}
            during infancy and was {development.soothing_difficulty.name} to
            soothe.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("Prenatal and Birth History", level=2)
        self.report.add_paragraph(text)

    def write_developmental_milestones(self) -> None:
        """Writes the developmental milestones to the report."""
        patient = self.intake.patient
        started_walking = patient.development.started_walking.transform()
        started_talking = patient.development.started_talking.transform()
        daytime_dryness = patient.development.daytime_dryness.transform()
        nighttime_dryness = patient.development.nighttime_dryness.transform()

        text = f"""
            {patient.preferred_name} achievement of social, language, fine and
            gross motor developmental milestones were within normal limits, as
            reported by {patient.guardian.full_name}. {patient.preferred_name}
            {started_walking} and {started_talking}.
            {patient.pronouns[0].capitalize()} {daytime_dryness} and
            {nighttime_dryness}.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("Developmental Milestones", level=2)
        self.report.add_paragraph(text)

    def write_early_education(self) -> None:
        """Writes the early education information to the report."""
        patient = self.intake.patient
        development = patient.development

        reporting_guardian = patient.guardian.full_name
        early_intervention = development.early_intervention_age.transform()
        cpse = development.cpse_age.transform()

        text = f"""
            {reporting_guardian} reported that
            {patient.preferred_name} {early_intervention} and {cpse}.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("Early Educational Interventions", level=2)
        self.report.add_paragraph(text)

    @write_with_rgb_text(RGB_INTAKE)
    def write_psychiatric_history(self) -> None:
        """Writes the psychiatric history to the end of the report."""
        self.report.add_heading("PSYCHRIATIC HISTORY", level=1)
        self.write_past_psychriatic_diagnoses()
        self.report.add_heading("Past Psychiatric Hospitalizations", level=2)
        self.report.add_heading("Past Therapeutic Interventions", level=2)
        self.report.add_heading(
            "Past Self-Injurious Behaviors and Suicidality",
            level=2,
        )
        self.report.add_heading(
            "Past Severe Aggressive Behaviors and Homicidality",
            level=2,
        )
        self.report.add_heading("Exposure to Violence and Trauma", level=2)
        self.report.add_heading(
            "Administration for Children's Services (ACS) Involvement",
            level=2,
        )
        self.write_family_psychiatric_history()

    def write_past_psychriatic_diagnoses(self) -> None:
        """Writes the past psychiatric diagnoses to the report."""
        patient = self.intake.patient
        past_diagnoses = patient.past_diagnoses.transform(short=False)

        text = f"""
            {patient.preferred_name} {past_diagnoses}.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("Past Psychiatric Diagnoses", level=2)
        self.report.add_paragraph(text)

    def write_family_psychiatric_history(self) -> None:
        """Writes the family psychiatric history to the report."""
        patient = self.intake.patient
        family_psychiatric_history = (
            patient.family_psychiatric_history.family_diagnoses.transform()
        )

        text = f"""
            {family_psychiatric_history}
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("Family Psychiatric History", level=2)
        self.report.add_paragraph(text)

    @write_with_rgb_text(RGB_TESTING)
    def write_recommendations(self) -> None:
        """Writes the recommendations to the report."""
        text = """
            Based on the results of the evaluation, the following recommendations are
            provided:
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("RECOMMENDATIONS", level=1)
        self.report.add_paragraph(text)
        self.report.add_heading("Further Evaluation", level=2)
        self.report.add_paragraph("")
        self.report.add_heading("Academics and Learning", level=2)
        self.report.add_paragraph("")
        self.report.add_heading("Psychotherapy", level=2)
        self.report.add_paragraph("")
        self.report.add_heading("Psychopharmacology", level=2)
        self.report.add_paragraph("")

    @write_with_rgb_text(rgb=RGB_TESTING)
    def write_dsm_5_diagnoses(self) -> None:
        """Writes the DSM-5 diagnoses to the report."""
        text = "Code\t\tDisorder Name"

        self.report.add_heading("DSM-5 Diagnoses", level=1)
        self.report.add_paragraph(text)

    def write_remaining_headers(self) -> None:
        """Writes headers for unimplemented sections to the report."""
        self.report.add_heading("ACADEMIC AND EDUCATIONAL HISTORY", level=1)
        self.report.add_heading("Previous Testing", level=2)
        self.report.add_heading("Educational History", level=2)
        self.report.add_heading("SOCIAL HISTORY", level=1)
        self.report.add_heading("Home and Adaptive Functioning", level=2)
        self.report.add_heading("Social functioning", level=2)
        self.write_psychiatric_history()

        self.report.add_heading("MEDICAL HISTORY", level=1)
        self.report.add_heading("CURRENT PSYCHIATRIC FUNCTIONING", level=1)
        self.report.add_heading("Current Psychiatric Medications", level=2)
        self.report.add_heading(
            "MENTAL STATUS EXAMINATION AND TESTING BEHAVIORAL OBSERVATIONS",
            level=1,
        )
        self.add_page_break()
        self.report.add_heading(
            "Insert List of Tests, Normal Curve and RA Text",
            level=0,
        )
        self.add_page_break()
        self.report.add_heading("CLINICAL SUMMARY AND IMPRESSIONS", level=1)
        self.report.add_heading("Cognition, Language and Learning Evaluation", level=2)
        self.report.add_heading("Mental Health Assessment", level=2)
        self.write_dsm_5_diagnoses()
        self.write_recommendations()

    def write_closing_statement(self) -> None:
        """Writes the closing statement to the report.

        This is done by merging two documents. We use composer because
        python-docx is not great for copying images.
        """
        replacements = {
            "preferred_name": self.intake.patient.preferred_name,
            "pronoun_0": self.intake.patient.pronouns[0],
            "pronoun_1": self.intake.patient.pronouns[1],
            "pronoun_2": self.intake.patient.pronouns[2],
        }

        for template, replacement in replacements.items():
            template_formatted = "{{" + template.upper() + "}}"
            docx_utils.DocxReplace(self.report_closing_statement).replace(
                template_formatted,
                replacement,
            )

        docx_utils.correct_they_conjugation(self.report_closing_statement)

        composer_obj = composer.Composer(self.report)
        composer_obj.append(self.report_closing_statement)
        with tempfile.NamedTemporaryFile(suffix=".docx") as docx_file:
            composer_obj.save(docx_file.name)
            self.report = docx.Document(docx_file.name)

    def transform(self) -> None:
        """Transforms the intake information to a report."""
        self.replace_patient_information()
        self.write_reason_for_visit()
        self.write_developmental_history()
        self.write_remaining_headers()
        self.write_closing_statement()

    def add_page_break(self) -> None:
        """Adds a page break to the report."""
        run = self.report.paragraphs[-1].add_run()
        run.add_break(text.WD_BREAK.PAGE)

    def _gender_and_age_to_string(self) -> str:
        """Converts the gender and age to an appropriate string."""
        age = self.intake.patient.age
        gender = self.intake.patient.gender
        child_age_cutoff = 15
        upper_age_cutoff = 18

        if age < child_age_cutoff:
            return (
                "girl" if "female" in gender else "boy" if "male" in gender else "child"
            )

        gender_string = (
            "woman" if "female" in gender else "man" if "male" in gender else "adult"
        )

        if age < upper_age_cutoff:
            return f"young {gender_string}"
        return gender_string

    @staticmethod
    def _remove_whitespace(text: str) -> str:
        """Removes excess whitespace from a string."""
        return " ".join(text.split())
