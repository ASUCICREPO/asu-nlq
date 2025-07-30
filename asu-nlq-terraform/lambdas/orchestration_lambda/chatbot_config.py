import logging
from prompts import (
    final_response, 
    classify, 
    no_sql, 
    create_question, 
    error
) 
import constants  # This configures logging
from TestingTimer import timer

logger = logging.getLogger(__name__)


# ============================================================================
# MODEL ID DEFINITIONS
# ============================================================================

# Model ID for final response generation
final_response_id = "us.amazon.nova-pro-v1:0"

# Model ID for classification tasks
classify_id = "us.amazon.nova-micro-v1:0"

# Model ID for NoSQL query handling
no_sql_id = "us.amazon.nova-pro-v1:0"

# Model ID for creating specific questions for SQL generation
create_question_id = "us.amazon.nova-micro-v1:0"

# Model ID for error handling (default case)
error_id = "us.amazon.nova-pro-v1:0"


# ============================================================================
# TEMPERATURE DEFINITIONS
# ============================================================================

# Temperature for final response generation
final_response_temperature = 0.1

# Temperature for classification tasks
classify_temperature = 0.1

# Temperature for NoSQL query handling
no_sql_temperature = 0.4

# Temperature for creating specific questions for SQL generation
create_question_temperature = 0.1

# Default temperature for unknown types
default_temperature = 0.3


# ============================================================================
# RETRIEVAL FUNCTIONS
# ============================================================================

# This function retrieves the appropriate prompt based on the type of interaction.
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
                prompt = final_response.final_response_prompt.format(results=results, schema=schema)
            case "classify":
                prompt = classify.classify_prompt.format(message=message, schema=schema, chatHistory=chatHistory)
            case "no_sql":
                prompt = no_sql.no_sql_prompt.format(schema=schema, reasoning=reasoning)
            case "create_question":
                prompt = create_question.create_question_prompt.format(message=message, chatHistory=chatHistory, schema=schema, reasoning=reasoning)
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


# This function retrieves the configuration settings based on the type of interaction.
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
                    "temperature": final_response_temperature,
                }
            case "classify":
                config = {
                    "temperature": classify_temperature,
                }
            case "no_sql":
                config = {
                    "temperature": no_sql_temperature,
                }
            case "create_question":
                config = {
                    "temperature": create_question_temperature,
                }
            case _:
                logger.warning(f"Unknown config type: {type}, using default")
                config = {
                    "temperature": default_temperature,
                }
        
        logger.info(f"Config retrieved for type: {type}")
        return config
        
    except Exception as e:
        logger.error(f"Failed to get config for type {type}: {e}")
        raise


# This function retrieves the appropriate model ID based on the type of interaction.
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
            case _:
                logger.warning(f"Unknown model type: {type}, using error model")
                model_id = error_id
        
        logger.info(f"Model ID retrieved for type: {type}")
        return model_id
        
    except Exception as e:
        logger.error(f"Failed to get model ID for type {type}: {e}")
        raise

