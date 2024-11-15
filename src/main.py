import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.handlers import start, handle_button, handle_numbers, handle_send_confirmation, handle_message_confirmation
from bot.commands import send, set_message
from utils.config_loader import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # Set to DEBUG to capture detailed logs
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler("bot.log")  # Log to a file
    ]
)

def main():
    try:
        logging.info("Starting SMS Sender Bot...")
        config = Config()
        bot_token = config.get('telegram_bot_token')
        logging.info(f"Using bot token: {bot_token}")
        
        app = (ApplicationBuilder()
               .token(bot_token)
               .connection_pool_size(8)
               .connect_timeout(60.0)
               .read_timeout(60.0)
               .write_timeout(60.0)
               .pool_timeout(60.0)
               .build())
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("send", send))
        app.add_handler(CommandHandler("set_message", set_message))
        
        # Add button handler
        app.add_handler(MessageHandler(
            filters.TEXT & filters.Regex('^(📝 Set Message|📱 Send Single SMS|📲 Send Bulk SMS)$'),
            handle_button
        ))
        
        # Add message handler for entering numbers
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, handle_numbers
        ))
        
        # Add callback query handlers
        app.add_handler(CallbackQueryHandler(handle_send_confirmation, pattern='^(confirm_send|cancel_send)$'))
        app.add_handler(CallbackQueryHandler(handle_message_confirmation, pattern='^(confirm_message|cancel_message)$'))
        
        logging.info("Bot is starting...")
        app.run_polling(
            poll_interval=1.0,
            timeout=30,
            drop_pending_updates=True
        )
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()