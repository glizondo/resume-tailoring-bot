import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx2pdf import convert



def extract_text_between_keywords(text, start_keyword, end_keyword):
    pattern = re.compile(re.escape(start_keyword) + '(.*?)' + re.escape(end_keyword), re.S)
    matches = pattern.search(text)
    return matches.group(1)


def extract_text_from_keyword_to_end(text, start_keyword):
    pattern = re.compile(re.escape(start_keyword) + '(.*)', re.S)
    matches = pattern.search(text)
    return matches.group(1) if matches else None


def create_resume(resume_chat_gpt, user):
    doc = Document()
    heading = doc.add_heading(f'{user[1]} {user[2]}', 0)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subheading = f'{user[3]}, {user[5]} - {user[6]} - {user[7]} - {user[8]}'
    subheading_paragraph = doc.add_paragraph()
    subheading_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = subheading_paragraph.add_run(subheading, 0)
    run.bold = True
    run.font.size = Pt(14)

    education = str(extract_text_between_keywords(resume_chat_gpt, "EDUCATION", "WORK EXPERIENCES"))
    work_experience = str(extract_text_between_keywords(resume_chat_gpt, "WORK EXPERIENCES", "SKILLS"))
    skills = str(extract_text_from_keyword_to_end(resume_chat_gpt, "SKILLS"))

    # Education
    doc.add_heading('Education:', level=1)
    education_text = education
    doc.add_paragraph(education_text)

    # Experience
    doc.add_heading('Work Experience:', level=1)
    experience_text = work_experience
    doc.add_paragraph(experience_text)

    # Skills
    doc.add_heading('Skills:', level=1)
    skills_text = skills
    doc.add_paragraph(skills_text)

    # Save the document
    doc.save('resume_created.docx')
    convert('resume_created.docx', 'resume_created.pdf')

