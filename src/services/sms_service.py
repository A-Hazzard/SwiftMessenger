from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from utils.config_loader import Config
import re
import socket
import requests
import time

class SMSService:
    def __init__(self):
        self.config = Config()
        self.client = Client(
            self.config.get('twilio')['account_sid'],
            self.config.get('twilio')['auth_token']
        )
        
    def check_internet_connection(self) -> bool:
        """Check if there's an active internet connection."""
        try:
            # Try to connect to Twilio's API
            requests.get('https://api.twilio.com', timeout=5)
            return True
        except requests.RequestException:
            try:
                # Fallback to a reliable DNS
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                return True
            except OSError:
                return False

    def validate_phone_number(self, number: str) -> bool:
        """Validate phone number format (E.164 format)."""
        pattern = r'^\+?1?\d{9,15}$'
        return bool(re.match(pattern, number))

    def send_sms(self, to_number: str, message: str) -> tuple[bool, str]:
        """Send SMS message with company name header."""
        if not message:
            return False, "Message cannot be empty"
            
        if not self.validate_phone_number(to_number):
            return False, "Invalid phone number format. Use international format (e.g., +1234567890)"
        
        # Add + if not present
        if not to_number.startswith('+'):
            to_number = '+' + to_number
        
        # Check internet connection first
        if not self.check_internet_connection():
            return False, "No internet connection. Please check your network and try again."
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                # Add company name to message
                company_name = self.config.get('company_name')
                full_message = f"{company_name}\n\n{message}"
                
                self.client.messages.create(
                    body=full_message,
                    from_=self.config.get('twilio')['phone_number'],
                    to=to_number
                )
                return True, "Message sent successfully"
                
            except TwilioRestException as e:
                error_code = str(e.code)
                if error_code == "20003":  # Authentication Error
                    return False, "Authentication failed. Please check your Twilio credentials."
                elif error_code == "20404":  # Phone number not found
                    return False, "The provided phone number is not valid or not supported."
                elif error_code == "20429":  # Too many requests
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return False, "Too many requests. Please try again later."
                else:
                    return False, f"Twilio error: {str(e)}"
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, f"Network error: {str(e)}. Please check your internet connection."
                
            except Exception as e:
                return False, f"Unexpected error: {str(e)}"
                
        return False, "Failed to send message after multiple attempts. Please try again later."
