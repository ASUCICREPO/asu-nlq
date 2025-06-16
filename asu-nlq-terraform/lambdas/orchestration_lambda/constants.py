import os
import logging

"""
Constants for NLQ project
This module contains configuration constants used throughout the application
"""

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Logging configuration - change LOG_LEVEL to control all modules
LOG_LEVEL = logging.WARNING  # or logging.DEBUG, logging.WARNING, etc.
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

# Template file containing the JSON schema definition for the database
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