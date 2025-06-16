import logging
import constants  # This configures logging

logger = logging.getLogger(__name__)

# Error handling prompt - should never be seen by users
error_prompt = "An error occurred, you should never recieve this prompt, if you do, please reply only with 'An error occurred, please try again later.'"

logger.info("Error prompt loaded successfully")
