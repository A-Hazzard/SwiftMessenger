from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, 
    filters, CallbackQueryHandler, CommandHandler
)
from services.sms_service import SMSService
from utils.config_loader import Config

# Conversation states
CHOOSING_ACTION, ENTERING_NUMBERS, CONFIRMING = range(3)

sms_service = SMSService()
config = Config()

async def start_bulk_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bulk send process"""
    await update.message.reply_text(
        "Please enter phone numbers separated by commas.\n"
        "Example: +1234567890, +9876543210"
    )
    return ENTERING_NUMBERS

async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming phone numbers"""
    numbers = [num.strip() for num in update.message.text.split(',')]
    valid_numbers = []
    invalid_numbers = []

    for number in numbers:
        if sms_service.validate_phone_number(number):
            valid_numbers.append(number)
        else:
            invalid_numbers.append(number)

    if invalid_numbers:
        await update.message.reply_text(
            f"Invalid numbers found: {', '.join(invalid_numbers)}\n"
            "Please try again with valid numbers."
        )
        return ENTERING_NUMBERS

    if not valid_numbers:
        await update.message.reply_text(
            "No valid numbers provided. Please enter valid phone numbers."
        )
        return ENTERING_NUMBERS

    context.user_data['numbers'] = valid_numbers
    keyboard = [[
        InlineKeyboardButton("✅ Confirm", callback_data='confirm'),
        InlineKeyboardButton("❌ Cancel", callback_data='cancel')
    ]]
    
    await update.message.reply_text(
        f"Ready to send to {len(valid_numbers)} numbers.\n"
        "Would you like to proceed?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return CONFIRMING

def get_bulk_send_handler():
    """Create and return the bulk send conversation handler"""
    return ConversationHandler(
        entry_points=[CommandHandler("bulk_send", start_bulk_send)],
        states={
            ENTERING_NUMBERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers)
            ],
            CONFIRMING: [CallbackQueryHandler(handle_confirmation)],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)]
    )

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bulk send confirmation callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'cancel':
        await query.edit_message_text("Operation cancelled.")
        return ConversationHandler.END
    
    if query.data == 'confirm':
        numbers = context.user_data.get('numbers', [])
        message = context.user_data.get('message', config.get('default_message'))
        
        if not numbers:
            await query.edit_message_text("No valid numbers to send SMS.")
            return ConversationHandler.END
            
        # Send messages and collect results
        results = []
        for number in numbers:
            success, response = sms_service.send_sms(number, message)
            status = "✅" if success else "❌"
            results.append(f"{status} {number}: {response}")
        
        result_message = "SMS Sending Results:\n" + "\n".join(results)
        
        # Split message if it's too long
        if len(result_message) > 4096:  # Telegram's message length limit
            chunks = [result_message[i:i+4096] for i in range(0, len(result_message), 4096)]
            for chunk in chunks:
                await query.message.reply_text(chunk)
        else:
            await query.edit_message_text(result_message)
            
        return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu with buttons"""
    keyboard = [
        [KeyboardButton("📝 Set Message")],
        [KeyboardButton("📱 Send Single SMS"), KeyboardButton("📲 Send Bulk SMS")],
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        "Welcome to SMS Sender Bot! 📱\n\n"
        "How to use:\n"
        "1️⃣ First, click '📝 Set Message' to set your SMS text\n"
        "2️⃣ Then choose either:\n"
        "   • '📱 Send Single SMS' for one recipient\n"
        "   • '📲 Send Bulk SMS' for multiple recipients\n\n"
        "Your message will be saved until you set a new one.\n"
        "The company name will automatically appear at the top of each message.",
        reply_markup=reply_markup
    )
    return CHOOSING_ACTION

async def handle_message_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle message confirmation callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_message':
        await query.edit_message_text("Message setting cancelled.")
        return ConversationHandler.END

    if query.data == 'confirm_message':
        message = context.user_data.get('pending_message')
        if message:
            context.user_data['message'] = message
            await query.edit_message_text("✅ Message has been set successfully!")
        else:
            await query.edit_message_text("❌ Error: No message to set.")
        return ConversationHandler.END

async def handle_send_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle single send confirmation callbacks"""
    query = update.callback_query
    await query.answer()

    if query.data == 'cancel_send':
        await query.edit_message_text("SMS sending cancelled.")
        return ConversationHandler.END

    if query.data == 'confirm_send':
        phone_number, message = context.user_data.get('pending_send', (None, None))
        if phone_number and message:
            success, response = sms_service.send_sms(phone_number, message)
            status = "✅" if success else "❌"
            await query.edit_message_text(f"{status} {response}")
        else:
            await query.edit_message_text("❌ Error: Missing phone number or message.")
        return ConversationHandler.END

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    text = update.message.text
    
    if text == "📝 Set Message":
        await update.message.reply_text(
            "Please send your message using:\n"
            "/set_message Your message here"
        )
    elif text == "📱 Send Single SMS":
        await update.message.reply_text(
            "Please send the number using:\n"
            "/send +1234567890"
        )
    elif text == "📲 Send Bulk SMS":
        return await start_bulk_send(update, context)