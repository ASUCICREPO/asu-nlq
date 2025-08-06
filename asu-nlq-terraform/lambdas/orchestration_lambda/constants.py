import os
import logging

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Create custom logging levels
TIMER_LEVEL = 25  # Between INFO (20) and WARNING (30)
CUSTOM_LEVEL = 35  # Between WARNING (30) and ERROR (40)

# Add level names
logging.addLevelName(TIMER_LEVEL, 'TIMER')
logging.addLevelName(CUSTOM_LEVEL, 'CUSTOM')

def timer(self, message, *args, **kwargs):
    """Custom timer logging method"""
    if self.isEnabledFor(TIMER_LEVEL):
        self._log(TIMER_LEVEL, message, args, **kwargs)

def custom(self, message, *args, **kwargs):
    """Custom logging method for your new level"""
    if self.isEnabledFor(CUSTOM_LEVEL):
        self._log(CUSTOM_LEVEL, message, args, **kwargs)

# Add the custom methods to Logger class
logging.Logger.timer = timer
logging.Logger.custom = custom

# Logging configuration - change LOG_LEVEL to control all modules
# Available levels: TIMER_LEVEL, CUSTOM_LEVEL, logging.INFO, logging.WARNING, etc.
LOG_LEVEL = TIMER_LEVEL  # Change this to control what gets logged
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'

def setup_logging():
    """Configure logging for the entire application"""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        force=True  # Override any existing configuration
    )

# Call setup when constants is imported
setup_logging()

# ============================================================================
# DATABASE SCHEMA CONFIGURATION
# ============================================================================

DATABASE_NAME = os.environ.get("DATABASE_NAME")
if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME environment variable is required")

TEMPLATE_NAME = os.environ.get("TEMPLATE_NAME")
if not TEMPLATE_NAME:
    raise ValueError("TEMPLATE_NAME environment variable is required")

API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
if not API_GATEWAY_URL:
    raise ValueError("API_GATEWAY_URL environment variable is required")

DATABASE_DESCRIPTIONS_S3_NAME = os.environ.get("DATABASE_DESCRIPTIONS_S3_NAME")
if not DATABASE_DESCRIPTIONS_S3_NAME:
    raise ValueError("DATABASE_DESCRIPTIONS_S3_NAME environment variable is required")

KNOWLEDGE_BASE_ID = os.environ.get("KNOWLEDGE_BASE_ID")
if not KNOWLEDGE_BASE_ID:
    raise ValueError("KNOWLEDGE_BASE_ID environment variable is required")