![Logo](./assets/logo.jpg)

# SMS Sender Telegram Bot

A Telegram bot for sending international SMS messages with company branding and easy configuration using Twilio.

## Features
- 📱 Button-based interface for easy operation
- 🌍 International SMS support with company name header
- 📨 Single and bulk SMS sending capabilities
- ⚙️ Easy configuration via config.json
- 🔄 Powered by Twilio's reliable SMS infrastructure

## Setup

### 1. Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (from @BotFather)
- Twilio Account (SID, Auth Token, and Phone Number)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/A-Hazzard/SwitftMessenger.git

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create your own `config/config.json` file based on the `config/configExample.json` template:
```json
{
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "twilio": {
        "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
        "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
        "from_number": "YOUR_TWILIO_PHONE_NUMBER"
    },
    "company_name": "YOUR_COMPANY_NAME",
    "default_message": "Your default message here"
}
```
- Copy `config/configExample.json` to `config/config.json`
- Replace the placeholder values with your actual credentials and settings
- Get your Twilio credentials from your Twilio Console Dashboard

### 4. Run the Bot
```bash
python src/main.py
```

## Usage

### Main Menu Buttons
- 📝 Set Message - Configure your SMS message
- 📱 Send Single SMS - Send to one number
- 📲 Send Bulk SMS - Send to multiple numbers

### SMS Format
- Numbers must be in international format (E.164)
- Examples: 
  - +1234567890 (US)
  - +447911123456 (UK)
  - +61412345678 (Australia)
- Company name appears automatically at the top of each message

### Bulk Sending
- Enter multiple numbers separated by commas
- Example: +1234567890, +447911123456, +61412345678

## Important Notes
- All credentials are stored in `config.json` for easy updates
- Messages will display your company name at the top
- Supports international SMS to any country where Twilio operates
- Make sure to maintain sufficient Twilio credits for sending messages