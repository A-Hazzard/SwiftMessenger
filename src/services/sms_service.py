import requests
import re
import socket
import time
from utils.config_loader import Config

class SMSService:
    def __init__(self):
        self.config = Config()
        self.api_key = self.config.get('textbelt')['api_key']
        self.api_url = self.config.get('textbelt')['api_url']
        
    def check_internet_connection(self) -> bool:
        """Check if there's an active internet connection."""
        try:
            # Try to connect to TextBelt's API
            requests.get('https://textbelt.com', timeout=5)
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
                
                # Prepare the payload for TextBelt
                payload = {
                    'phone': to_number,
                    'message': full_message,
                    'key': self.api_key,
                }

                response = requests.post(self.api_url, json=payload)
                result = response.json()

                if result.get('success'):
                    return True, "Message sent successfully"
                else:
                    error = result.get('error') or "Unknown error"
                    if 'quota' in error.lower():
                        return False, "SMS quota exceeded. Please check your TextBelt credits."
                    return False, f"Failed to send message: {error}"
                    
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return False, f"Network error: {str(e)}. Please check your internet connection."
                
            except Exception as e:
                return False, f"Unexpected error: {str(e)}"
                
        return False, "Failed to send message after multiple attempts. Please try again later."
