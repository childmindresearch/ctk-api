"""Contains report writing functionality for intake information."""
import itertools
import tempfile
from typing import ParamSpec, TypeVar

import docx
from docx.enum import table as enum_table
from docx.enum import text as enum_text
from docxcompose import composer

from ctk_api.core import config
from ctk_api.routers.file_conversion.intake import descriptors, parser, utils

P = ParamSpec("P")
T = TypeVar("T")

DATA_DIR = config.DATA_DIR
RGB_INTAKE = (178, 161, 199)
RGB_TESTING = (155, 187, 89)
RGB_TEMPLATE = (247, 150, 70)
PLACEHOLDER = "______"


class ReportWriter:
    """Writes a report for intake information."""

    def __init__(self, intake: parser.IntakeInformation) -> None:
        """Initializes the report writer.

        Args:
            intake: The intake information.
        """
        self.intake = intake
        self.report = docx.Document(DATA_DIR / "report_template.docx")
        self.report_mental_status_examination = docx.Document(
            DATA_DIR / "report_template_mental_status_examination.docx",
        )
        self.report_closing_statement = docx.Document(
            DATA_DIR / "report_template_closing_statement.docx",
        )

    def transform(self) -> None:
        """Transforms the intake information to a report."""
        self.write_reason_for_visit()
        self.write_developmental_history()
        self.write_academic_history()
        self.write_social_history()
        self.write_psychiatric_history()
        self.write_medical_history()
        self.write_current_psychiatric_functioning()
        self.add_page_break()
        self.write_mental_status_examination()
        self.write_dsm_5_diagnoses()
        self.write_recommendations()
        self.write_closing_statement()
        self.replace_patient_information()
        self.apply_corrections()

    def replace_patient_information(self) -> None:
        """Replaces the patient information in the report."""
        replacements = {
            "full_name": self.intake.patient.full_name,
            "preferred_name": self.intake.patient.first_name,
            "date_of_birth": self.intake.patient.date_of_birth.strftime("%m/%d/%Y"),
            "reporting_guardian": self.intake.patient.guardian.title_name,
            "aged_gender": self.intake.patient.age_gender_label,
            "pronoun_0": self.intake.patient.pronouns[0],
            "pronoun_1": self.intake.patient.pronouns[1],
            "pronoun_2": self.intake.patient.pronouns[2],
            "pronoun_4": self.intake.patient.pronouns[4],
        }

        for template, replacement in replacements.items():
            template_formatted = "{{" + template.upper() + "}}"
            utils.DocxReplace(self.report).replace(template_formatted, replacement)

    def write_reason_for_visit(self) -> None:
        """Writes the reason for visit to the end of the report."""
        patient = self.intake.patient
        handedness = patient.handedness
        iep = patient.education.individualized_educational_program
        past_diagnoses = patient.psychiatric_history.past_diagnoses.transform(
            short=True,
        )
        classroom = patient.education.classroom_type

        if patient.education.grade.isnumeric():
            grade_superscript = utils.ordinal_suffix(int(patient.education.grade))
        else:
            grade_superscript = ""

        texts = [
            f"""
            At the time of enrollment, {patient.first_name} was a
            {patient.age}-year-old, {handedness} {patient.age_gender_label}
            {past_diagnoses}. {patient.first_name} was placed in a {classroom}
            {patient.education.grade}""",
            f"{grade_superscript} ",
            f"""
            grade classroom at {patient.education.school_name}.
            {patient.first_name} {iep}. {patient.first_name} and
            {patient.pronouns[2]} {patient.guardian.relationship},
            {patient.guardian.title_full_name}, attended the present evaluation due to
            concerns regarding {PLACEHOLDER}. The family is hoping for
            {PLACEHOLDER}. The family learned of the study through
            {PLACEHOLDER}.
        """,
        ]
        texts = [utils.remove_excess_whitespace(text) for text in texts]

        heading = self.report.add_heading("REASON FOR VISIT", level=1)
        paragraph = self.report.add_paragraph(texts[0])
        paragraph.add_run(texts[1]).font.superscript = True
        paragraph.add_run(" " + texts[2])
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

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
        pregnancy_symptoms = development.birth_complications
        delivery = development.delivery
        delivery_location = development.delivery_location
        adaptability = development.adaptability
        duration_of_pregnancy = development.duration_of_pregnancy

        text = f"""
            {patient.guardian.title_name} reported {pregnancy_symptoms}.
            {patient.first_name} was born at
            {duration_of_pregnancy} of gestation with {delivery} at
            {delivery_location}. {patient.first_name} had {adaptability}
            during infancy and was {development.soothing_difficulty.name} to
            soothe.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Prenatal and Birth History", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_developmental_milestones(self) -> None:
        """Writes the developmental milestones to the report."""
        patient = self.intake.patient
        started_walking = patient.development.started_walking
        started_talking = patient.development.started_talking
        daytime_dryness = patient.development.daytime_dryness
        nighttime_dryness = patient.development.nighttime_dryness

        text = f"""
            {patient.first_name}'s achievement of social, language, fine and
            gross motor developmental milestones were within normal limits, as
            reported by {patient.guardian.title_name}. {patient.first_name}
            {started_walking} and {started_talking}.
            {patient.pronouns[0].capitalize()} {daytime_dryness} and
            {nighttime_dryness}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Developmental Milestones", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_early_education(self) -> None:
        """Writes the early education information to the report."""
        patient = self.intake.patient
        development = patient.development

        reporting_guardian = patient.guardian.title_name
        early_intervention = development.early_intervention_age
        cpse = development.cpse_age

        text = f"""
            {reporting_guardian} reported that
            {patient.first_name} {early_intervention} and {cpse}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Early Educational Interventions", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_academic_history(self) -> None:
        """Writes the academic history to the end of the report."""
        heading = self.report.add_heading("ACADEMIC AND EDUCATIONAL HISTORY", level=1)
        utils.format_paragraphs(heading, font_rgb=RGB_INTAKE)
        self.write_previous_testing()
        self.write_academic_history_table()
        self.write_educational_history()

    def write_previous_testing(self) -> None:
        """Writes the previous testing information to the report."""
        patient = self.intake.patient

        text = f"""
        {patient.first_name} has no history of previous psychoeducational
        evaluations./{patient.first_name} was evaluated by {PLACEHOLDER} in 20XX.
        Documentation of the results of the evaluation(s) were unavailable at
        the time of writing this report/ Notable results include:
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Previous Testing", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_TEMPLATE)

    def write_academic_history_table(self) -> None:
        """Writes the academic history table to the report."""
        paragraph = self.report.add_paragraph("Name, Date of Assessment")
        utils.format_paragraphs(
            paragraph,
            font_rgb=RGB_INTAKE,
            bold=True,
            alignment=enum_text.WD_PARAGRAPH_ALIGNMENT.CENTER,
        )

        table = self.report.add_table(7, 4)
        table.style = "Table Grid"
        header_row = table.rows[0].cells

        header_texts = [
            "Domain/Index/Subtest",
            "Standard Score",
            "Percentile Rank",
            "Descriptor",
        ]
        for i, header in enumerate(header_texts):
            header_row[i].text = header
            header_row[i].width = 10
            utils.format_cell(
                header_row[i],
                bold=True,
                font_rgb=RGB_INTAKE,
                background_rgb=(217, 217, 217),
                alignment=enum_text.WD_ALIGN_PARAGRAPH.CENTER,
            )
        for row in table.rows:
            row.height = 1
            row.height_rule = enum_table.WD_ROW_HEIGHT_RULE.EXACTLY
            for cell in row.cells:
                utils.format_cell(
                    cell,
                    line_spacing=1,
                    space_after=0,
                    space_before=0,
                )

    def write_educational_history(self) -> None:
        """Writes the educational history to the report."""
        patient = self.intake.patient
        education = patient.education
        has_iep = (
            education.individualized_educational_program.base
            == descriptors.IndividualizedEducationProgram.yes.value
        )

        if has_iep:
            iep_prior_text = f"""
                {patient.first_name} was
                granted an Individualized Education Program (IEP) in
                {PLACEHOLDER} grade due to {PLACEHOLDER}
                difficulties.
            """
        else:
            iep_prior_text = f"""{patient.first_name} has never had an
                              Individiualized Education Program (IEP)."""
        if education.grade.isnumeric():
            grade_superscript = utils.ordinal_suffix(education.grade)
        else:
            grade_superscript = ""
        past_schools = education.past_schools

        text_prior = f"""
            {patient.first_name} {past_schools}. {patient.pronouns[0]}
            previously struggled with (provide details of academic challenges
            and behavioral difficulties in school). {iep_prior_text}
        """
        texts_current = [
            f"""{patient.first_name} is currently in the {education.grade}""",
            f"{grade_superscript} ",
            f"""
                grade at {education.school_name}.
                {patient.first_name} does/does not receive special
                education services and maintains/does not have an IEP
                allowing accommodations for/including {PLACEHOLDER}.
                {patient.first_name} is generally an average/above
                average/below average student and receives mostly (describe
                grades). [Describe any academic issues reported by parent or
                child.] {patient.first_name} continues to exhibit
                weaknesses in {PLACEHOLDER}.
            """,
        ]
        text_prior = utils.remove_excess_whitespace(text_prior)
        texts_current = [utils.remove_excess_whitespace(text) for text in texts_current]

        heading = self.report.add_heading("Educational History", level=2)
        prior_paragraph = self.report.add_paragraph(text_prior)
        utils.format_paragraphs((heading, prior_paragraph), font_rgb=RGB_INTAKE)

        current_paragraph = self.report.add_paragraph(texts_current[0])
        current_paragraph.add_run(texts_current[1]).font.superscript = True
        current_paragraph.add_run(" " + texts_current[2])
        utils.format_paragraphs(current_paragraph, font_rgb=RGB_TEMPLATE)

    def write_social_history(self) -> None:
        """Writes the social history to the end of the report."""
        heading = self.report.add_heading("SOCIAL HISTORY", level=1)
        utils.format_paragraphs(heading, font_rgb=RGB_INTAKE)
        self.write_home_and_adaptive_functioning()
        self.write_social_functioning()

    def write_home_and_adaptive_functioning(self) -> None:
        """Writes the home and adaptive functioning to the report."""
        patient = self.intake.patient
        household = patient.household
        household_members = utils.join_with_oxford_comma(
            [
                (
                    f"{member.relationship} ({member.age}y, "
                    f"{member.grade_occupation.lower()}, "
                    f"{member.relationship_quality} relationship)"
                )
                for member in household.members
            ],
        )
        language_fluencies = self._join_patient_languages(self.intake.patient.languages)

        text_home = f"""
            {patient.first_name} lives in {household.city},
            {household.state}, with {patient.pronouns[2]} {household_members}.
            The {patient.guardian.parent_or_guardian}s are
            {household.guardian_marital_status}.
            {utils.join_with_oxford_comma(household.languages)} {"are" if
            len(household.languages) > 1 else "is"} spoken at home.
            {patient.language_spoken_best} is reportedly
            {patient.first_name}'s preferred language.
            {patient.first_name} {language_fluencies}.
        """

        text_adaptive = f"""
            {patient.guardian.title_name} denied any concerns with {patient.pronouns[2]}
            functioning in the home setting// Per {patient.guardian.title_name},
            {patient.first_name} has a history of {PLACEHOLDER} (temper
            outbursts, oppositional behaviors, etc.) in the home setting. (Write
            details of behavioral difficulties). (Also include any history of
            sleep difficulties, daily living skills, poor hygiene, etc.)
            """
        text_home = utils.remove_excess_whitespace(text_home)
        text_adaptive = utils.remove_excess_whitespace(text_adaptive)

        heading = self.report.add_heading("Home and Adaptive Functioning", level=2)
        home_paragraph = self.report.add_paragraph(text_home)
        adaptive_paragraph = self.report.add_paragraph(text_adaptive)

        utils.format_paragraphs((heading, home_paragraph), font_rgb=RGB_INTAKE)
        utils.format_paragraphs(adaptive_paragraph, font_rgb=RGB_TEMPLATE)

    def write_social_functioning(self) -> None:
        """Writes the social functioning to the report."""
        patient = self.intake.patient

        text = f"""
            {patient.guardian.title_name} was pleased to describe
            {patient.first_name} as a (insert adjective e.g., affectionate)
            {patient.age_gender_label}. {patient.guardian.title_name} reported
            that {patient.pronouns[0]} has many/several/one friends in
            {patient.pronouns[2]} peer group in school and on
            {patient.pronouns[2]} team/club/etc. {patient.first_name}
            socializes with friends outside of school and has a
            (positive/fair/poor) relationship with them.
            {patient.first_name}'s hobbies include {PLACEHOLDER}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Social Functioning", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_psychiatric_history(self) -> None:
        """Writes the psychiatric history to the end of the report."""
        heading = self.report.add_heading("PSYCHRIATIC HISTORY", level=1)
        utils.format_paragraphs(heading, font_rgb=RGB_INTAKE)
        self.write_past_psychriatic_diagnoses()
        self.write_past_psychiatric_hospitalizations()
        self.write_past_therapeutic_interventions()
        self.write_past_self_injurious_behaviors_and_suicidality()
        self.write_past_aggressive_behaviors_and_homicidality()
        self.expose_to_violence_and_trauma()
        self.administration_for_childrens_services_involvement()
        self.write_family_psychiatric_history()

    def write_past_psychiatric_hospitalizations(self) -> None:
        """Writes the past psychiatric hospitalizations to the report."""
        patient = self.intake.patient
        text = f"""
            {patient.guardian.title_name} denied any history of past psychiatric
            hospitalizations for {patient.first_name}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Past Psychiatric Hospitalizations", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_TEMPLATE)

    def administration_for_childrens_services_involvement(self) -> None:
        """Writes the ACS involvement to the report."""
        patient = self.intake.patient

        text = str(patient.psychiatric_history.children_services)
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading(
            "Administration for Children's Services (ACS) Involvement",
            level=2,
        )
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_past_aggressive_behaviors_and_homicidality(self) -> None:
        """Writes the past aggressive behaviors and homicidality to the report."""
        patient = self.intake.patient

        text = str(patient.psychiatric_history.aggresive_behaviors)
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading(
            "Past Severe Aggressive Behaviors and Homicidality",
            level=2,
        )
        report = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, report), font_rgb=RGB_INTAKE)

    def write_past_psychriatic_diagnoses(self) -> None:
        """Writes the past psychiatric diagnoses to the report."""
        patient = self.intake.patient
        past_diagnoses = patient.psychiatric_history.past_diagnoses.transform(
            short=False,
        )

        text = f"""
            {patient.first_name} {past_diagnoses}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Past Psychiatric Diagnoses", level=2)
        report = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, report), font_rgb=RGB_INTAKE)

    def write_family_psychiatric_history(self) -> None:
        """Writes the family psychiatric history to the report."""
        patient = self.intake.patient
        family_psychiatric_history = (
            patient.psychiatric_history.family_psychiatric_history
        )
        diagnosis_text = family_psychiatric_history.family_diagnoses

        text = str(diagnosis_text)
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Family Psychiatric History", level=2)
        report = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, report), font_rgb=RGB_INTAKE)

    def write_past_therapeutic_interventions(self) -> None:
        """Writes the past therapeutic history to the report."""
        patient = self.intake.patient
        guardian = patient.guardian
        interventions = patient.psychiatric_history.therapeutic_interventions

        if not interventions:
            texts = [
                f"""
                    {patient.guardian.title_name} denied any history of therapeutic
                    interventions.
                """,
            ]
        else:
            texts = [
                f"""
                    From {intervention.start}-{intervention.end},
                    {patient.first_name} engaged in therapy with
                    {intervention.therapist} due to "{intervention.reason}" at a
                    frequency of {intervention.frequency}. {guardian.title_name}
                    described the treatment as "{intervention.effectiveness}".
                    Treatment was ended due to "{intervention.reason_ended}".
                    """
                for intervention in interventions
            ]

        texts = [utils.remove_excess_whitespace(text) for text in texts]

        heading = self.report.add_heading("Past Therapeutic Interventions", level=2)
        paragraphs = [self.report.add_paragraph(text) for text in texts]
        utils.format_paragraphs((heading, *paragraphs), font_rgb=RGB_INTAKE)

    def write_past_self_injurious_behaviors_and_suicidality(self) -> None:
        """Writes the past self-injurious behaviors and suicidality to the report."""
        patient = self.intake.patient

        text = str(patient.psychiatric_history.self_harm)
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading(
            "Past Self-Injurious Behaviors and Suicidality",
            level=2,
        )
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def expose_to_violence_and_trauma(self) -> None:
        """Writes the exposure to violence and trauma to the report."""
        patient = self.intake.patient

        text = str(patient.psychiatric_history.violence_and_trauma)
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("Exposure to Violence and Trauma", level=2)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_INTAKE)

    def write_medical_history(self) -> None:
        """Writes the medical history to the end of the report."""
        patient = self.intake.patient

        text = f"""
            {patient.first_name}'s medical history is unremarkable for
            significant medical conditions. {patient.pronouns[0]} is not
            currently taking any medications for chronic medical conditions.
            {patient.first_name} wears prescription glasses in home and
            school settings. {patient.pronouns[0]} does/does not require a
            hearing device. {patient.guardian.title_name} denied any history of
            seizures, head trauma, migraines, meningitis or encephalitis.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("MEDICAL HISTORY", level=1)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_TEMPLATE)

    def write_clinical_summary_and_impressions(self) -> None:
        """Writes the clinical summary and impressions to the report."""
        patient = self.intake.patient
        gender = patient.age_gender_label

        text = f"""
            {patient.first_name} is a
            sociable/resourceful/pleasant/hardworking/etc. {gender} who
            participated in the Healthy Brain Network research project through
            the Child Mind Institute in the interest of participating in
            research/due to parental concerns regarding {PLACEHOLDER}.
        """
        text = utils.remove_excess_whitespace(text)

        heading = self.report.add_heading("CLINICAL SUMMARY AND IMPRESSIONS", level=1)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_TESTING)

    def write_recommendations(self) -> None:
        """Writes the recommendations to the report."""
        text = """
            Based on the results of the evaluation, the following recommendations are
            provided:
        """
        text = utils.remove_excess_whitespace(text)

        level_2_headings = [
            "Further Evaluation",
            "Academics and Learning",
            "Psychotherapy",
            "Psychopharmacology",
        ]
        heading = self.report.add_heading("RECOMMENDATIONS", level=1)
        text = self.report.add_paragraph(text)
        paragraphs = [
            self.report.add_paragraph(heading) for heading in level_2_headings
        ]
        utils.format_paragraphs((heading, text, *paragraphs), font_rgb=RGB_TESTING)

    def write_dsm_5_diagnoses(self) -> None:
        """Writes the DSM-5 diagnoses to the report."""
        text = "Code\t\tDisorder Name"

        heading = self.report.add_heading("DSM-5 Diagnoses", level=1)
        paragraph = self.report.add_paragraph(text)
        utils.format_paragraphs((heading, paragraph), font_rgb=RGB_TESTING)

    def write_current_psychiatric_functioning(self) -> None:
        """Writes the current psychiatric functioning to the report.

        Note: this section mixes color codings. Color decorators are applied
        to the called functions instead.
        """
        heading = self.report.add_heading("CURRENT PSYCHIATRIC FUNCTIONING", level=1)
        utils.format_paragraphs(heading, font_rgb=RGB_INTAKE)
        self.write_current_psychiatric_medications_intake()
        self.write_current_psychiatric_medications_testing()
        self.write_denied_symptoms()

    def write_current_psychiatric_medications_intake(self) -> None:
        """Writes the current psychiatric medications to the report."""
        patient = self.intake.patient
        text = f"""
        {patient.first_name} is currently prescribed a daily/twice daily
        oral course of {PLACEHOLDER} for {PLACEHOLDER}. {patient.pronouns[0]} is
        being treated by Doctortype, DoctorName, monthly/weekly/biweekly. The
        medication has been ineffective/effective.
        """
        text = utils.remove_excess_whitespace(text)

        self.report.add_heading("Current Psychiatric Medications", level=2)
        self.report.add_paragraph(text)

    def write_current_psychiatric_medications_testing(self) -> None:
        """Writes the current psychiatric medications to the report."""
        patient = self.intake.patient
        texts = [
            f"""
        [Rule out presenting diagnoses, using headlines and KSADS/DSM criteria.
        Examples of headlines include: Temper Outbursts (ending should include
        “{patient.guardian.title_name} denied any consistent patterns of
        irritability for {patient.first_name}" if applicable), Inattention
        and Hyperactivity, Autism-Related Symptoms, Oppositional Defiant
        Behaviors, etc.].""",
            "Establish a baseline first for temper outbursts",
            f"""
           (Ex:
        Though {patient.first_name} is generally a {PLACEHOLDER} child,
        {patient.pronouns[0]} continues to have difficulties with temper
        tantrums…).
        """,
        ]
        texts = [utils.remove_excess_whitespace(text) for text in texts]

        paragraph = self.report.add_paragraph(texts[0])
        paragraph.add_run(texts[1])
        paragraph.runs[-1].bold = True
        paragraph.add_run(texts[2])
        utils.format_paragraphs(paragraph, italics=True)

    def write_denied_symptoms(self) -> None:
        """Writes the denied symptoms to the report."""
        patient = self.intake.patient
        text = f"""
        {patient.guardian.title_name} and {patient.first_name} denied any
        current significant symptoms related to mood, suicidality, psychosis,
        eating, oppositional or conduct behaviors, substance abuse, autism,
        tics, inattention/hyperactivity, enuresis/encopresis, trauma, sleep,
        panic, anxiety or obsessive-compulsive disorders.
        """
        text = utils.remove_excess_whitespace(text)

        self.report.add_paragraph(text)

    def write_mental_status_examination(self) -> None:
        """Writes the mental status examination to the report."""
        compose = composer.Composer(self.report)
        compose.append(self.report_mental_status_examination)

        with tempfile.NamedTemporaryFile(suffix=".docx") as docx_file:
            compose.save(docx_file.name)
            self.report = docx.Document(docx_file.name)

    def write_closing_statement(self) -> None:
        """Writes the closing statement to the report.

        This is done by merging two documents. We use composer because
        python-docx is not great for copying images.
        """
        composer_obj = composer.Composer(self.report)
        composer_obj.append(self.report_closing_statement)
        with tempfile.NamedTemporaryFile(suffix=".docx") as docx_file:
            composer_obj.save(docx_file.name)
            self.report = docx.Document(docx_file.name)

    def apply_corrections(self) -> None:
        """Applies various grammatical and styling corrections."""
        document_corrector = utils.DocumentCorrections(
            self.report,
            correct_they=self.intake.patient.pronouns[0] == "they",
            correct_capitalization=True,
        )
        document_corrector.correct()

    def add_page_break(self) -> None:
        """Adds a page break to the report."""
        run = self.report.paragraphs[-1].add_run()
        run.add_break(enum_text.WD_BREAK.PAGE)

    @staticmethod
    def _join_patient_languages(languages: list[parser.Language]) -> str:
        """Joins the patient's languages."""
        fluency_groups = itertools.groupby(
            languages,
            key=lambda language: language.fluency,
        )
        fluency_dict = {
            fluency: [language.name for language in language_group]
            for fluency, language_group in fluency_groups
        }

        language_descriptions = [
            f"{fluency} in {utils.join_with_oxford_comma(fluency_dict[fluency])}"
            for fluency in ["fluent", "proficient", "conversational"]
            if fluency in fluency_dict
        ]
        prepend_is = len(language_descriptions) > 0
        if "basic" in fluency_dict:
            language_descriptions.append(
                (
                    "has basic skills in "
                    f"{utils.join_with_oxford_comma(fluency_dict['basic'])}"
                ),
            )

        text = utils.join_with_oxford_comma(language_descriptions)
        if prepend_is:
            text = "is " + text
        return text
