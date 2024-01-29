# pip install -r requirements.txt

import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext, \
    CallbackQueryHandler
from pathlib import Path
import numpy as np
import os

from credentials import credentials

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)



# COMMANDS
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    print("Start command ran")
    await update.message.reply_html(
        rf"Welcome to the Resume Tailoring Tool. go to /help to find out what you can do")


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
                                    "specific position \n/createcoverletter - Create a cover letter based on your "
                                    "skills and requirements for a \n/jobnotifications - Request to be notified "
                                    "every time a new job is posted on LinkedIn")


# HANDLERS
def echo_text(update, context):
    text = update.message.text
    username = ''
    try:
        username = update.message.chat.first_name
    except:
        pass
    return 'What do you mean by "' + text + '"? ' + f"Please, check the /help command for hints of what to do next"


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(echo_text(update, context))


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
    # app.add_handler(CallbackQueryHandler(handle_response_query_user))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # app.add_handler(MessageHandler(filters.PHOTO, check_origin_photo))

    # Errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
