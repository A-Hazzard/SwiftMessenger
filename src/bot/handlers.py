from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from services.sms_service import SMSService
from utils.config_loader import Config

# Conversation states
CHOOSING_ACTION, ENTERING_NUMBERS = range(2)

sms_service = SMSService()
config = Config()

async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Starting handle_numbers function")
    try:
        print(f"Received input: {update.message.text}")
        
        numbers = [num.strip() for num in update.message.text.split(',')]
        valid_numbers = []
        invalid_numbers = []

        for number in numbers:
            print(f"Processing number: {number}")
            if sms_service.validate_phone_number(number):
                valid_numbers.append(number)
            else:
                invalid_numbers.append(number)

        print(f"Valid numbers: {valid_numbers}")
        print(f"Invalid numbers: {invalid_numbers}")

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

        message = context.user_data.get('message', config.get('default_message'))
        results = []
        for number in valid_numbers:
            try:
                print(f"Sending SMS to {number}")
                success, response = sms_service.send_sms(number, message)
                status = "✅" if success else "❌"
                results.append(f"{status} {number}: {response}")
                print(f"Result for {number}: {response}")
            except Exception as e:
                print(f"Error sending SMS to {number}: {e}")
                results.append(f"❌ {number}: Error occurred")

        result_message = "SMS Sending Results:\n" + "\n".join(results)
        print(f"Send results: {result_message}")

        if len(result_message) > 4096:
            chunks = [result_message[i:i+4096] for i in range(0, len(result_message), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(result_message)

        print("Ending handle_numbers function")
        return ConversationHandler.END
    except Exception as e:
        print(f"Error in handle_numbers: {e}")

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
        await update.message.reply_text(
            "Please enter phone numbers separated by commas.\n"
            "Example: +1234567890, +9876543210"
        )
        return ENTERING_NUMBERS

async def handle_send_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation of sending SMS"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    if query.data == 'confirm_send':
        phone_number, message = context.user_data.get('pending_send', (None, None))
        if phone_number and message:
            success, response = sms_service.send_sms(phone_number, message)
            await query.edit_message_text(f"Send result: {response}")
        else:
            await query.edit_message_text("No pending send found.")
    elif query.data == 'cancel_send':
        await query.edit_message_text("Send operation cancelled.")

async def handle_message_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation of setting message"""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    if query.data == 'confirm_message':
        message = context.user_data.get('pending_message')
        if message:
            context.user_data['message'] = message
            await query.edit_message_text("Message set successfully.")
        else:
            await query.edit_message_text("No pending message found.")
    elif query.data == 'cancel_message':
        await query.edit_message_text("Message setting cancelled.")