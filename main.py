import logging
from telegram.ext import Application
from config import TG_BOT_TOKEN
from handlers import handler_command, handler_query, handler_get_message

logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    try:
        application = Application.builder().token(TG_BOT_TOKEN).build()

        handler_get_message.listing(application)
        handler_command.listing(application)
        handler_query.listing(application)

        logger.info("Bot started")
        application.run_polling()

    except Exception as e:
        logger.error("Error while starting bot:", e)

if __name__ == "__main__":
    main()