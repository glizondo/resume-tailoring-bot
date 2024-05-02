import re

from docx.shared import Pt


def extract_text_between_keywords(text, start_keyword, end_keyword):
    pattern = re.compile(rf"{start_keyword}(.*?){end_keyword}", re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return ""


def extract_text_from_keyword_to_end(text, start_keyword):
    pattern = re.compile(re.escape(start_keyword) + '(.*)', re.S)
    matches = pattern.search(text)
    return matches.group(1) if matches else None


def extract_text_from_beginning_to_keyword(text, end_keyword):
    pattern = re.compile('(.*?)' + re.escape(end_keyword), re.S)
    matches = pattern.search(text)
    return matches.group(1)


def set_spacing_for_heading(heading):
    for run in heading.runs:
        run.font.size = Pt(14)
    paragraph_format = heading.paragraph_format
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)


def set_no_spacing_paragraph(paragraph):
    paragraph_format = paragraph.paragraph_format
    paragraph_format.space_before = Pt(0)
    paragraph_format.space_after = Pt(0)
    paragraph_format.line_spacing = 1.0
