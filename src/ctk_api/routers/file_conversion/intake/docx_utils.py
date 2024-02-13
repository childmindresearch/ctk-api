import dataclasses
import re

import docx
import mlconjug3
import spacy
from spacy import symbols, tokens

NLP = spacy.load("en_core_web_sm")


@dataclasses.dataclass
class SubjectVerbPair:
    """A pair of a subject and a verb in a sentence."""

    sentence: str
    subject_token: tokens.Token
    verb_token: tokens.Token

    @property
    def subject(self) -> str:
        """The subject of the sentence."""
        return self.subject_token.text

    @property
    def verb(self) -> str:
        """The verb of the sentence."""
        return self.verb_token.text

    @property
    def verb_indices(self) -> tuple[int, int]:
        """The indices of the verb in the sentence."""
        return self.verb_token.idx, self.verb_token.idx + len(self.verb)


def correct_they_conjugation(document: docx.Document) -> None:
    """Corrects the conjugation of verbs associated with they.

    Acts in-place on the document.

    Args:
        document: The document to correct.

    Notes:
        See https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
        for a full list of word tags.
    """
    replacer = DocxReplace(document)
    conjugator = mlconjug3.Conjugator(language="en")

    for paragraph in document.paragraphs:
        sentences = paragraph.text.split(".")
        for sentence in sentences:
            words = sentence.split(" ")
            lower_words = [word.lower() for word in words]
            if "they" not in lower_words:
                continue
            subject_verb_pairs = _find_subject_verb(sentence)
            subject_verb_they = [
                pair for pair in subject_verb_pairs if "they" in pair.subject.lower()
            ]
            for pair in subject_verb_they:
                for child in pair.verb_token.children:
                    if child.tag_ == "VBZ":
                        pair.verb_token = child
                        break
                if pair.verb_token.tag_ != "VBZ":
                    continue

                verb = conjugator.conjugate(pair.verb_token.lemma_)
                conjugated_verb = verb["indicative"]["indicative present"]["they"]
                new_sentence = (
                    sentence[: pair.verb_indices[0]]
                    + conjugated_verb
                    + sentence[pair.verb_indices[1] :]
                )

                replacer.replace(sentence, new_sentence)


def _find_subject_verb(sentence: str) -> list[tuple[int, int]]:
    """Finds the subject and verb of a sentence, only if the subject.

    Args:
        sentence: The sentence to analyze.

    Returns:
        A list of indices of subjects and verbs
    """
    doc = NLP(sentence)
    return [
        SubjectVerbPair(
            sentence=sentence,
            subject_token=word,
            verb_token=word.head,
        )
        for word in doc
        if word.dep in [symbols.nsubj, symbols.nsubjpass]
        and word.head.tag_.startswith("VB")
    ]


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

        match_indices = [
            match.start() for match in re.finditer(re.escape(find), paragraph.text)
        ]

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
