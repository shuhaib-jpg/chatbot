# config.py
import os

class Config:
    """Bot configuration from environment variables"""
    
    # Bot credentials - NEVER hardcode real values here
    APP_ID = os.getenv("MicrosoftAppId", "")
    APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
    APP_TENANT_ID = os.getenv("MicrosoftAppTenantId", "")
    
    # Server config
    PORT = int(os.getenv("PORT", "8000"))
    
    @staticmethod
    def is_production():
        """Check if running in production (has credentials)"""
        return bool(Config.APP_ID and Config.APP_PASSWORD)