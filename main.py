# pip install -r requirements.txt

import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, \
    CallbackQueryHandler
from chatgpt import chatgpt_handler
from cover_letter_creator import cover_letter_creator
from database import database_handler
from credentials import credentials
import sqlite3
from docx import Document
import re
from job_search_webs import linkedin_handler
from resume_creator import resume_creator
from text_tools import text_extraction

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

connection = sqlite3.connect("./database/resume-bot.db")

LASTNAME, CITY, STATE, COUNTRY, EMAIL, PHONE, LINKEDIN, RESUME = range(8)


# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    print(f'{user_id} {user_name}')
    # Check if user exists, add if not add new one
    exists = database_handler.check_user_exists(connection, user_id, user_name)
    print("Start command ran")
    if not exists:
        await update.message.reply_html(
            rf"Welcome to the Resume Tailoring Tool. It looks like you are new here, {user_name}. Please access your /profile to add information that will be added to your resume")
    else:
        await update.message.reply_html(
            rf"Welcome again to the Resume Tailoring Tool, {user_name}. go to /help to find out what you can do or to /profile to modify your personal and resume information")


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print(f'handle profile {update.message.text}')
    context.user_data.clear()
    await update.message.reply_text(
        f"Welcome! Type CANCEL to cancel and go back main menu. Let's start editing your profile {update.effective_user.first_name}. What is your last name?"
    )
    # print(update.message.from_user)
    return LASTNAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    print(f'last name {update.message.text}')
    if user_response != 'CANCEL':
        context.user_data['last_name'] = user_response
        await update.message.reply_text("What is your city?")
        return CITY
    else:
        await cancel(update, context)


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        context.user_data['city'] = user_response
        await update.message.reply_text("In which state do you live?")
        return STATE
    else:
        await cancel(update, context)


async def state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        context.user_data['state'] = user_response
        await update.message.reply_text("In which country do you live?")
        return COUNTRY
    else:
        await cancel(update, context)


async def country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        context.user_data['country'] = user_response
        await update.message.reply_text("Email")
        return EMAIL
    else:
        await cancel(update, context)


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        email_input = user_response
        if not re.match(email_regex, email_input):
            await update.message.reply_text("Invalid email format. Please enter a valid email:")
            return EMAIL
        context.user_data['email'] = email_input
        await update.message.reply_text("Phone number")
        return PHONE
    else:
        await cancel(update, context)


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        context.user_data['phone'] = user_response
        await update.message.reply_text("Linkedin Profile")
        return LINKEDIN
    else:
        await cancel(update, context)


async def linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        linkedin_regex = r'^(www\.)?linkedin\.com\/.*$'
        linkedin_input = user_response
        if not re.match(linkedin_regex, linkedin_input):
            await update.message.reply_text("Invalid LinkedIn profile URL. Please enter a valid LinkedIn profile URL:")
            return LINKEDIN  # Stay in the LINKEDIN state
        context.user_data['linkedin'] = linkedin_input
        user_data = context.user_data
        await database_handler.insert_data_user(connection, user_data['last_name'], user_data['city'],
                                                user_data['state'],
                                                user_data['country'], user_data['email'],
                                                user_data['phone'], user_data['linkedin'], update.effective_user.id)
        await update.message.reply_text("Thank you for sharing your information! Now one more step. Please, add your "
                                        "resume in a word document so I can store your information (Make sure the titles "
                                        "for each section are named EDUCATION, EXPERIENCE, and SKILLS")
        return RESUME
    else:
        await cancel(update, context)


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_response = update.message.text
    if user_response != 'CANCEL':
        document_id = update.message.document
        document = await context.bot.get_file(document_id)
        print(f'Document: {document}')
        print(f'Document ID: {document_id}')
        file_path = Path(str(r"resumes/resume.docx"))
        await document.download_to_drive(custom_path=file_path)
        await read_doc(update, context, file_path)
        return ConversationHandler.END
    else:
        await cancel(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    context.user_data.clear()
    await update.message.reply_text(
        'Cancelled. Please use /start to return to the main menu or /profile to edit your profile again.')
    return ConversationHandler.END


async def read_doc(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path) -> None:
    doc = Document(file_path)
    full_text = []
    for word in doc.paragraphs:
        full_text.append(word.text)
    document_text = ' '.join(full_text)
    document_cleaned = re.sub(r'\s+', ' ', document_text)
    await insert_data_resume_to_database(document_cleaned, update)
    await update.message.reply_text(
        "Thank you.\nNow feel free to do the following:\n /tailorresume - To generate a resume\n /createcoverletter - To create a cover letter")


async def insert_data_resume_to_database(document_text, update):
    user_id = update.effective_user.id
    resume_id = database_handler.add_resume(connection, user_id)
    education = str(text_extraction.extract_text_between_keywords(document_text, "EDUCATION", "EXPERIENCE"))
    database_handler.add_education(connection, resume_id, education)
    experience = str(text_extraction.extract_text_between_keywords(document_text, "EXPERIENCE", "SKILLS"))
    database_handler.add_work_experience(connection, resume_id, experience)
    skills = str(text_extraction.extract_text_from_keyword_to_end(document_text, "SKILLS"))
    database_handler.add_skill(connection, resume_id, skills)


WAITING_FOR_LINK_RESUME = 1


async def start_tailor_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please paste the link from Linkedin that contains the job")
    return WAITING_FOR_LINK_RESUME


async def receive_job_link_resume_creator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    job_link = update.message.text
    user_id = update.effective_user.id
    resume_info = database_handler.generate_query_chat_gpt(connection, user_id)
    job_info = linkedin_handler.get_job_description(job_link)
    await generate_resume_file(context, job_info, resume_info, update, user_id)
    return ConversationHandler.END


async def generate_resume_file(context, job_info, resume_info, update, user_id):
    await update.message.reply_text("Generating your resume in PDF format...")
    resume_chat_gpt = chatgpt_handler.resume_chatgpt_query(resume_info, job_info)
    user = database_handler.get_user_by_id(connection, user_id)
    await update.message.reply_text("Almost there...")
    resume_creator.create_resume(str(resume_chat_gpt), user)
    chat_id = update.message.chat_id
    await context.bot.send_document(chat_id=chat_id, document=open('resume_created.pdf', 'rb'))
    await update.message.reply_text(
        "Thank you.\nIf you did not like the resume give it another try:\n /tailorresume \n /createcoverletter - To create a cover letter")


SELECTING_TONE = 0
WAITING_FOR_LINK_COVER = 1


async def create_cover_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("Create Cover Letter command ran")
    await update.message.reply_text("What tone do you want on your cover letter? (Very formal, Formal, Casual)")
    return SELECTING_TONE


async def handle_response_cover_letter_tone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tone = update.message.text.lower()
    if tone not in ['very formal', 'formal', 'casual']:
        await update.message.reply_text(f"Please enter very formal, formal, or casual")
        return SELECTING_TONE
    context.user_data['tone_cover_letter'] = tone
    await update.message.reply_text(f"Thanks for the reply. The cover letter will have a {tone} tone. "
                                    f"Now, please paste the link from Linkedin that contains the job")
    return WAITING_FOR_LINK_COVER


async def receive_job_link_cover_letter_creator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    job_link = update.message.text
    user_id = update.effective_user.id
    resume_info = database_handler.generate_query_chat_gpt(connection, user_id)
    job_info = linkedin_handler.get_job_description(job_link)
    tone = context.user_data['tone_cover_letter']
    await generate_cover_letter_file(update, context, job_info, resume_info, user_id, tone)
    return ConversationHandler.END


async def generate_cover_letter_file(update, context, job_info, resume_info, user_id, tone) -> None:
    await update.message.reply_text("Generating your cover letter in PDF format...")
    cover_letter_chatgpt = chatgpt_handler.cover_letter_chatgpt_query(resume_info, job_info, tone)
    user = database_handler.get_user_by_id(connection, user_id)
    await update.message.reply_text("Almost there...")
    cover_letter_creator.create_cover_letter(str(cover_letter_chatgpt), user)
    chat_id = update.message.chat_id
    await context.bot.send_document(chat_id=chat_id, document=open('cover_letter_created.pdf', 'rb'))
    await update.message.reply_text(
        "Thank you.\nIf you did not like the cover letter give it another try:\n /tailorresume \n /createcoverletter - To create a cover letter")


async def job_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Job Notifications command ran")
    await update.message.reply_text("Job Notifications")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Help command ran")
    await update.message.reply_text("/start -> Start command \n/tailorresume -> Create your resume tailored to a "
                                    "specific position \n/createcoverletter -> Create a cover letter based on your "
                                    "skills and requirements \n/jobnotifications -> Request to be notified "
                                    "every time a new job is posted on LinkedIn \n/profile -> Create or "
                                    "modify your profile")


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


# MAIN
def main() -> None:
    print('Starting bot...')
    app = Application.builder().token(credentials.bot_token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('jobnotifications', job_notifications))
    app.add_handler(CommandHandler('read_doc', read_doc))
    app.add_handler(CallbackQueryHandler(handle_response_cover_letter_tone))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('profile', handle_profile)],
        states={
            LASTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, state)],
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, country)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            LINKEDIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, linkedin)],
            RESUME: [MessageHandler(filters.ATTACHMENT & ~filters.COMMAND, resume)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )
    conv_handler_resume = ConversationHandler(
        entry_points=[CommandHandler('tailorresume', start_tailor_resume)],
        states={
            WAITING_FOR_LINK_RESUME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_job_link_resume_creator)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    conv_handler_cover_letter = ConversationHandler(
        entry_points=[CommandHandler('createcoverletter', create_cover_letter)],
        states={
            SELECTING_TONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response_cover_letter_tone)],
            WAITING_FOR_LINK_COVER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_job_link_cover_letter_creator)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(conv_handler_resume)
    app.add_handler(conv_handler_cover_letter)

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
