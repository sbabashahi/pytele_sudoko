import os
import uuid

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from tele_bot import start, solution, solve, echo
from utils import frames


def main() -> None:
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler(['start', 'help'], start))
    application.add_handler(CallbackQueryHandler(solution))
    application.add_handler(MessageHandler(filters=filters.PHOTO, callback=solve))
    application.add_handler(MessageHandler(filters=filters.Document.IMAGE, callback=solve))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))

    application.run_polling()
    print('Bot is running')


if __name__ == "__main__":
    main()
    if os.getenv('DEBUG'):
        frames[0].save(
            f'output-{str(uuid.uuid4())[:4]}.gif',
            save_all=True,
            append_images=frames[1:],
            duration=300,
            loop=0,
        )
