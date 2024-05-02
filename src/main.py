# pip install -r requirements.txt

import logging
from telegram.ext import Application
from src.credentials import credentials
from src.handlers import setup_handlers


def setup_logging():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)


def setup_bot():
    app = Application.builder().token(credentials.bot_token).build()
    setup_handlers(app)
    return app


def main():
    setup_logging()
    bot = setup_bot()
    bot.run_polling()


if __name__ == '__main__':
    main()
