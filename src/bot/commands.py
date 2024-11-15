from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.sms_service import SMSService
from utils.config_loader import Config
import asyncio
import telegram

sms_service = SMSService()
config = Config()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to SMS Sender Bot!\n"
        "Available commands:\n"
        "/send <phone_number> - Send SMS to a single number\n"
        "/bulk_send - Send SMS to multiple numbers\n"
        "/set_message <message> - Set a default message"
    )

async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please provide a phone number: /send <phone_number>\n"
            "Example: /send +1234567890"
        )
        return

    phone_number = context.args[0]
    message = context.user_data.get('message', config.get('default_message'))

    # Confirm the sending of the SMS with the user
    keyboard = [
        [InlineKeyboardButton("✅ Confirm", callback_data='confirm_send')],
        [InlineKeyboardButton("❌ Cancel", callback_data='cancel_send')]
    ]
    await update.message.reply_text(
        f"You are about to send the following message to {phone_number}:\n\n{message}\n\nDo you want to proceed?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['pending_send'] = (phone_number, message)  # Store the pending send details

async def set_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the message to be sent"""
    try:
        if not context.args:
            await update.message.reply_text(
                "Please provide a message: /set_message <your message>\n"
                "Example: /set_message Hello from SMS Bot!"
            )
            return

        message = ' '.join(context.args)
        if len(message) > 160:  # SMS standard length
            await update.message.reply_text("Message too long. Please keep it under 160 characters.")
            return
            
        # Confirm the message with the user
        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data='confirm_message')],
            [InlineKeyboardButton("❌ Cancel", callback_data='cancel_message')]
        ]
        await update.message.reply_text(
            f"You have set the message to:\n\n{message}\n\nDo you want to confirm this message?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['pending_message'] = message  # Store the pending message
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")