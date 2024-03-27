from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx2pdf import convert

from text_tools import text_extraction


def create_cover_letter(cover_letter_chatgpt, user):
    doc = Document()
    subheading = f'{user[1]} {user[2]}\n{user[3]}, {user[5]}\n{user[6]}\n{user[7]}'
    subheading_paragraph = doc.add_paragraph()
    subheading_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    run = subheading_paragraph.add_run(subheading, 0)
    run.bold = False
    run.font.size = Pt(11)

    text_heading = doc.add_heading('', level=1)
    text_extraction.set_spacing_for_heading(text_heading)
    text_paragraph = doc.add_paragraph(
        text_extraction.extract_text_from_beginning_to_keyword(cover_letter_chatgpt, "END"))
    text_extraction.set_no_spacing_paragraph(text_paragraph)

    # Save the document
    doc.save('cover_letter_created.docx')
    convert('cover_letter_created.docx', 'cover_letter_created.pdf')
