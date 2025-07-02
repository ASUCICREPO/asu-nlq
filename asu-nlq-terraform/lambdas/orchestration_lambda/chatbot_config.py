"""
Chatbot Configuration Manager
Handles prompts, configuration settings, and model IDs for different chatbot interaction types.
"""

import logging
from prompts import final_response, classify, no_sql, create_question, attributes_json, sql_generation, error

import constants  # This configures logging

logger = logging.getLogger(__name__)


# ============================================================================
# MODEL ID DEFINITIONS
# ============================================================================

# Model ID for final response generation
final_response_id = "us.amazon.nova-pro-v1:0"

# Model ID for classification tasks
classify_id = "us.amazon.nova-pro-v1:0"

# Model ID for NoSQL query handling
no_sql_id = "us.amazon.nova-pro-v1:0"

# Model ID for creating specific questions for SQL generation
create_question_id = "us.amazon.nova-pro-v1:0"

# Model ID for attributes JSON generation
attributes_json_id = "us.amazon.nova-pro-v1:0"

# Model ID for SQL generation
sql_generation_id = "us.amazon.nova-pro-v1:0"

# Model ID for error handling (default case)
error_id = "us.amazon.nova-pro-v1:0"


# ============================================================================
# PROMPT RETRIEVAL FUNCTION
# ============================================================================

def get_prompt(type, message=None, schema=None, chatHistory=None, reasoning=None, attributes=None, results=None):
    """
    Returns the appropriate prompt based on the specified type.
    Formats prompts with provided parameters for AI model consumption.
    """
    logger.info(f"Getting prompt for type: {type}")
    
    try:
        prompt = ""
        match type:
            case "final_response":
                prompt = final_response.final_response_prompt.format(message=message, results=results, schema=schema)
            case "classify":
                prompt = classify.classify_prompt.format(message=message, schema=schema, chatHistory=chatHistory)
            case "no_sql":
                prompt = no_sql.no_sql_prompt.format(schema=schema, reasoning=reasoning)
            case "create_question":
                prompt = create_question.create_question_prompt.format(message=message, chatHistory=chatHistory, schema=schema, reasoning=reasoning)
            case "attributes_json":
                prompt = attributes_json.attributes_json_prompt.format(message=message, schema=schema)
            case "sql_generation":
                prompt = sql_generation.sql_generation_prompt.format(message=message, schema=schema, attributes=attributes)
            case _:
                logger.warning(f"Unknown prompt type: {type}, using error prompt")
                prompt = error.error_prompt
        
        logger.info(f"Prompt retrieved successfully for type: {type}")
        return [
            {
                "text": prompt
            }
        ]
        
    except KeyError as e:
        logger.error(f"Missing parameter for prompt formatting: {e}")
        logger.error(f"Prompt type: {type}")
        raise
    except AttributeError as e:
        logger.error(f"Prompt module not found: {e}")
        logger.error(f"Prompt type: {type}")
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt for type {type}: {e}")
        raise


# ============================================================================
# CONFIGURATION RETRIEVAL FUNCTION
# ============================================================================

def get_config(type):
    """
    Returns configuration settings based on the specified type.
    Provides temperature and other model parameters for different use cases.
    """
    logger.info(f"Getting config for type: {type}")
    
    try:
        config = {}
        match type:
            case "final_response":
                config = {
                    "temperature": 0.4,
                }
            case "classify":
                config = {
                    "temperature": 0.1,
                }
            case "no_sql":
                config = {
                    "temperature": 0.4,
                }
            case "create_question":
                config = {
                    "temperature": 0.1,
                }
            case "attributes_json":
                config = {
                    "temperature": 0.1,
                }
            case "sql_generation":
                config = {
                    "temperature": 0.1,
                }
            case _:
                logger.warning(f"Unknown config type: {type}, using default")
                config = {
                    "temperature": 0.3,
                }
        
        logger.info(f"Config retrieved for type: {type}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to get config for type {type}: {e}")
        raise


# ============================================================================
# MODEL ID RETRIEVAL FUNCTION
# ============================================================================

def get_id(type):
    """
    Returns the appropriate model ID based on the specified type.
    Maps interaction types to their corresponding AI models.
    """
    logger.info(f"Getting model ID for type: {type}")
    
    try:
        model_id = ""
        match type:
            case "final_response":
                model_id = final_response_id
            case "classify":
                model_id = classify_id
            case "no_sql":
                model_id = no_sql_id  
            case "create_question":
                model_id = create_question_id
            case "attributes_json":
                model_id = attributes_json_id
            case "sql_generation":
                model_id = sql_generation_id
            case _:
                logger.warning(f"Unknown model type: {type}, using error model")
                model_id = error_id
        
        logger.info(f"Model ID retrieved for type: {type}")
        return model_id
        
    except Exception as e:
        logger.error(f"Failed to get model ID for type {type}: {e}")
        raise