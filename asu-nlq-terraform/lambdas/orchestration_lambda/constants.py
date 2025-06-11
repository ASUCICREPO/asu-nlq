import os
"""
Constants for NLQ project
This module contains configuration constants used throughout the application
"""
# Database Schema Configuration
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