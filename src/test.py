from utils.config_loader import Config

def test_config():
    config = Config()
    print("Telegram Bot Token:", config.get('telegram_bot_token'))
    print("Twilio Account SID:", config.get('twilio.account_sid'))
    print("Twilio Auth Token:", config.get('twilio.auth_token'))
    print("Twilio Phone Number:", config.get('twilio.phone_number'))
    print("Company Name:", config.get('company_name'))
    print("Default Message:", config.get('default_message'))

if __name__ == "__main__":
    test_config()