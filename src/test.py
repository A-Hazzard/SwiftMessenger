from utils.config_loader import Config

def test_config():
    config = Config()
    print("Telegram Bot Token:", config.get('telegram_bot_token'))
    print("TextBelt API Key:", config.get('textbelt.api_key'))
    print("TextBelt API URL:", config.get('textbelt.api_url'))
    print("Company Name:", config.get('company_name'))
    print("Default Message:", config.get('default_message'))

if __name__ == "__main__":
    test_config()