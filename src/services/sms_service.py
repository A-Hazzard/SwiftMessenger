from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import re
import socket
import time
from utils.config_loader import Config

class SMSService:
    def __init__(self):
        self.config = Config()
        twilio_config = self.config.get('twilio')
        self.client = Client(twilio_config['account_sid'], twilio_config['auth_token'])
        self.from_number = twilio_config['from_number']
        
    def check_internet_connection(self) -> bool:
        """Check if there's an active internet connection."""
        try:
            socket.create_connection(("api.twilio.com", 443), timeout=3)
            return True
        except OSError:
            return False

    def validate_phone_number(self, number: str) -> bool:
        """Validate phone number format (E.164 format)."""
        pattern = r'^\+[1-9]\d{6,14}$'
        return bool(re.match(pattern, number))

    def send_sms(self, to_number: str, message: str) -> tuple[bool, str]:
        """Send SMS message with company name header."""
        if not message:
            return False, "Message cannot be empty"
            
        if not self.validate_phone_number(to_number):
            return False, "Invalid phone number format. Must start with + and country code (e.g., +1234567890)"
        
        if not self.check_internet_connection():
            return False, "No internet connection. Please check your network and try again."
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                company_name = self.config.get('company_name')
                full_message = f"{company_name}\n\n{message}"
                
                # Send using Twilio phone number
                message = self.client.messages.create(
                    from_=self.from_number,
                    body=full_message,
                    to=to_number
                )
                print(f"Message SID: {message.sid}")
                return True, "Message sent successfully"
                    
            except TwilioRestException as e:
                error_message = str(e)
                if 'insufficient funds' in error_message.lower():
                    return False, "Insufficient Twilio credits. Please check your balance."
                elif 'invalid number' in error_message.lower():
                    return False, "Invalid phone number or unreachable destination."
                elif attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, f"Twilio error: {error_message}"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, f"Unexpected error: {str(e)}"
                
        return False, "Failed to send message after multiple attempts. Please try again later."
