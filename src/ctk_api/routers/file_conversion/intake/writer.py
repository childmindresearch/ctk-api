"""Contains report writing functionality for intake information."""
import re

import docx
from docx.enum import text

from ctk_api.core import config
from ctk_api.routers.file_conversion.intake import parser

DATA_DIR = config.DATA_DIR


class ReportWriter:
    """Writes a report for intake information."""

    def __init__(self, intake: parser.IntakeInformation) -> None:
        """Initializes the report writer."""
        self.intake = intake
        self.report = docx.Document(DATA_DIR / "report_template.docx")

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
            DocxReplace(self.report).replace(template_formatted, replacement)

    def write_reason_for_visit(self) -> None:
        """Writes the reason for visit to the end of the report."""
        patient = self.intake.patient
        handedness = patient.handedness.transform()
        iep = patient.education.individualized_educational_program.transform()
        gender = self._gender_and_age_to_string()

        text = f"""
            At the time of enrollment, {patient.preferred_name} was a
            {patient.age}-year-old, {handedness} {gender}.
            {patient.preferred_name} was placed in a
            {patient.education.school_type.name} school grade
            {patient.education.grade} classroom at
            {patient.education.school_name}. {patient.preferred_name} {iep}.
        """
        text = self._remove_whitespace(text)

        self.report.add_heading("REASON FOR VISIT", level=1)
        self.report.add_paragraph(text)

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

        prenatal_text = f"""
            {patient.guardian.full_name} reported {pregnancy_symptoms}.
            {patient.preferred_name} was born at
            {development.weeks_of_pregnancy} of gestation with {delivery} at
            {delivery_location}. {patient.preferred_name} had an {adaptability}
            during infancy and was {development.soothing_difficulty.name} to
            soothe.
        """
        prenatal_text = self._remove_whitespace(prenatal_text)

        self.report.add_heading("Prenatal and Birth History", level=2)
        self.report.add_paragraph(prenatal_text)

    def write_developmental_milestones(self) -> None:
        """Writes the developmental milestones to the report."""
        self.report.add_heading("Developmental Milestones", level=2)

    def write_early_education(self) -> None:
        """Writes the early education information to the report."""
        patient = self.intake.patient
        development = patient.development

        reporting_guardian = patient.guardian.full_name
        early_intervention = development.early_intervention_age.transform()
        cpse = development.cpse_age.transform()

        early_education_text = f"""
            {reporting_guardian} reported that
            {patient.preferred_name} {early_intervention} and {cpse}.
        """
        early_education_text = self._remove_whitespace(early_education_text)
        self.report.add_heading("Early Educational Interventions", level=2)
        self.report.add_paragraph(early_education_text)

    def write_unimplemented_headers(self) -> None:
        """Writes headers for unimplemented sections to the report."""
        self.report.add_heading("ACADEMIC AND EDUCATIONAL HISTORY", level=1)
        self.report.add_heading("Previous Testing", level=2)
        self.report.add_heading("Educational History", level=2)
        self.report.add_heading("SOCIAL HISTORY", level=1)
        self.report.add_heading("Home and Adaptive Functioning", level=2)
        self.report.add_heading("Social fundtioning", level=2)
        self.report.add_heading("PSYCHRIATIC HISTORY", level=1)
        self.report.add_heading("Past Psychiatric Diagnoses", level=2)
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
        self.report.add_heading("Family Psychiatric History", level=2)
        self.report.add_heading("MEDICAL HISTORY", level=1)
        self.report.add_heading("CURRENT PSYCHIATRIC FUNCTIONING", level=1)
        self.report.add_heading("Current Psychiatric Medications", level=2)
        self.report.add_heading(
            "MENTAL STATUS EXAMINATION AND TESTING BEHAVIORAL OBSERVATIONS",
            level=1,
        )
        run = self.report.paragraphs[-1].add_run()
        run.add_break(text.WD_BREAK.PAGE)
        self.report.add_heading(
            "Insert List of Tests, Normal Curve and RA Text",
            level=0,
        )
        run = self.report.paragraphs[-1].add_run()
        run.add_break(text.WD_BREAK.PAGE)
        self.report.add_heading("CLINICAL SUMMARY AND IMPRESSIONS", level=1)
        self.report.add_heading("Cognition, Language and Learning Evaluation", level=2)
        self.report.add_heading("Mental Health Assessment", level=2)
        self.report.add_heading("DSM-5 DIAGNOSES", level=1)
        self.report.add_heading("RECOMMENDATIONS", level=1)

    def transform(self) -> None:
        """Transforms the intake information to a report."""
        self.replace_patient_information()
        self.write_reason_for_visit()
        self.write_developmental_history()
        self.write_unimplemented_headers()

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


class DocxReplace:
    """Finds and replaces text in a Word document."""

    def __init__(self, document: docx.Document) -> None:
        """Initializes a DocxReplace object for finding and replacing.

        Args:
            document: The document to be written.

        """
        self.document = document

    def replace(self, find: str, replace: str) -> None:
        """Finds and replaces text in a Word document.

        Args:
            find: The text to find.
            replace: The text to replace.
        """
        for paragraph in self.document.paragraphs:
            self._replace_in_section(paragraph, find, replace)

        for section in self.document.sections:
            for paragraph in (
                *section.footer.paragraphs,
                *section.header.paragraphs,
            ):
                self._replace_in_section(paragraph, find, replace)

    @staticmethod
    def _replace_in_section(
        paragraph: docx.text.paragraph.Paragraph,
        find: str,
        replace: str,
    ) -> None:
        """Finds and replaces text in a Word document section.

        Applying a find and replace directly to the text property will lose
        formatting. python-docx splits each paragraph into runs, where each run
        has consistent styling. So we apply the find and replace to the runs.
        The replacement will gain the formatting of the first character of the
        text it replaces.

        This function modifies in place.

        Args:
            paragraph: The Word document's paragraph.
            find: The text to find.
            replace: The text to replace.

        """
        if find not in paragraph.text:
            return

        for paragraph_run in paragraph.runs:
            paragraph_run.text = paragraph_run.text.replace(find, replace)

        if find not in paragraph.text:
            return

        match_indices = [match.start() for match in re.finditer(find, paragraph.text)]
        run_lengths = [len(run.text) for run in paragraph.runs]
        for run_index in range(len(paragraph.runs) - 1, -1, -1):
            # Reverse loop so changes to run lengths don't affect the next
            # iteration.
            run_start = sum(run_lengths[:run_index])
            run_end = run_start + run_lengths[run_index]
            run_obj = paragraph.runs[run_index]
            for match_index in match_indices:
                if match_index < run_start or match_index >= run_end:
                    continue

                overflow = match_index + len(find) - run_end
                run_obj.text = run_obj.text[: match_index - run_start] + replace

                current_index = run_index + 1
                while overflow > 0:
                    next_run = paragraph.runs[current_index]
                    new_overflow = overflow - len(next_run.text)
                    next_run.text = next_run.text[overflow:]
                    overflow = new_overflow
                    current_index += 1

                break
