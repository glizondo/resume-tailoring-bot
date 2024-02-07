# pip install -r requirements.txt

import logging
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from database import database
from credentials import credentials
import sqlite3
from docx import Document

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
    exists = database.check_user_exists(connection, user_id, user_name)
    print("Start command ran")
    if not exists:
        await update.message.reply_html(
            rf"Welcome to the Resume Tailoring Tool. It looks like you are new here, {user_name}. Please access your /profile to add information that will be added to your resume")
    else:
        await update.message.reply_html(
            rf"Welcome to the Resume Tailoring Tool. go to /help to find out what you can do")


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        f"Welcome! Let's start editing your profile {update.effective_user.first_name}. What is your last name?"
    )
    print(update.message.from_user)
    return LASTNAME


async def last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['last_name'] = update.message.text
    await update.message.reply_text("What is your city?")
    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['city'] = update.message.text
    await update.message.reply_text("In which state do you live?")
    return STATE


async def state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['state'] = update.message.text
    await update.message.reply_text("In which country do you live?")
    return COUNTRY


async def country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['country'] = update.message.text
    await update.message.reply_text("Email")
    return EMAIL


async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Phone number")
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Linkedin Profile")
    return LINKEDIN


async def linkedin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data['linkedin'] = update.message.text
    await database.insert_data_user(connection, user_data['last_name'], user_data['city'], user_data['state'],
                                    user_data['country'], user_data['email'],
                                    user_data['phone'], user_data['linkedin'], update.effective_user.id)
    await update.message.reply_text("Thank you for sharing your information! Now one more step. Please, add your "
                                    "resume in a word document so I can store your information (Make sure the titles "
                                    "for each section are named EDUCATION, EXPERIENCE, and SKILLS")
    return RESUME


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # context.user_data['phone'] = update.message.text
    document_id = update.message.document
    document = await context.bot.get_file(document_id)
    print(f'Document: {document}')
    print(f'Document ID: {document_id}')
    file_path = Path(str(r"resumes/resume.docx"))
    await document.download_to_drive(custom_path=file_path)
    await read_doc(update, context, file_path)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text('Bye! I hope we can talk again some day.')
    return ConversationHandler.END


async def read_doc(update: Update, context: ContextTypes.DEFAULT_TYPE, file_path) -> None:
    doc = Document(file_path)
    full_text = []
    for word in doc.paragraphs:
        full_text.append(word.text)
    document_text = ' '.join(full_text)
    print(document_text)
    await update.message.reply_text("Thank you")


async def tailor_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Tailor Resume command ran")
    await update.message.reply_text("Tailor Resume")


async def create_cover_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Create Cover Letter command ran")
    await update.message.reply_text("Create Cover Letter")


async def job_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Job Notifications command ran")
    await update.message.reply_text("Job Notifications")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Help command ran")
    await update.message.reply_text("/start -> Start command \n/tailorresume -> Create your resume tailored to a "
                                    "specific position \n/createcoverletter -> Create a cover letter based on your "
                                    "skills and requirements for a \n/jobnotifications -> Request to be notified "
                                    "every time a new job is posted on LinkedIn")


# HANDLERS
# def echo_text(update, context):
#     text = update.message.text
#     username = ''
#     try:
#         username = update.message.chat.first_name
#     except:
#         pass
#     return 'What do you mean by "' + text + '"? ' + f"Please, check the /help command for hints of what to do next"


# async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print(f'Update {update} caused error {context.error}')


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text(echo_text(update, context))


# MAIN
def main() -> None:
    print('Starting bot...')
    app = Application.builder().token(credentials.bot_token).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('tailorresume', tailor_resume))
    app.add_handler(CommandHandler('createcoverletter', create_cover_letter))
    app.add_handler(CommandHandler('jobnotifications', job_notifications))
    app.add_handler(CommandHandler('read_doc', read_doc))

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
    )

    app.add_handler(conv_handler)

    # Messages
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # app.add_handler(MessageHandler(filters.TEXT, conv_handler))

    # Errors
    # app.add_error_handler(error)

    print('Polling...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()