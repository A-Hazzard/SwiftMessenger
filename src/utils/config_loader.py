import json
import os
import logging

class Config:
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        """Load configuration from config.json"""
        config_path = os.path.join('config', 'config.json')
        try:
            with open(config_path, 'r') as f:
                cls._config = json.load(f)
                logging.info("Configuration loaded successfully.")
        except FileNotFoundError:
            raise Exception(f"Configuration file not found at {config_path}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON in configuration file")
    
    @classmethod
    def get(cls, key: str):
        """Get a configuration value"""
        if cls._config is None:
            cls._load_config()
            
        # Handle nested keys (e.g., 'twilio.account_sid')
        keys = key.split('.')
        value = cls._config
        for k in keys:
            if k not in value:
                return None
            value = value[k]
        return value