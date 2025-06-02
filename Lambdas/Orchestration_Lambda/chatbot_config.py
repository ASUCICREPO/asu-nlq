"""
Chatbot Configuration Manager
Handles prompts, configuration settings, and model IDs for different chatbot interaction types.
"""

# ============================================================================
# PROMPT DEFINITIONS
# ============================================================================

# Main system prompt for final responses
system_prompt = "you are a helpful assistant, answer the question as best you can, if you don't know the answer, say 'I don't know'."

# Error handling prompt - should never be seen by users
error_Prompt = "An error occurred, you should never recieve this prompt, if you do, please reply only with 'An error occurred, please try again later.'"

# Classification prompt (currently empty)
classify_prompt = ""


# ============================================================================
# MODEL ID DEFINITIONS
# ============================================================================

# Model ID for final response generation
final_response_id = "us.amazon.nova-pro-v1:0"

# Model ID for classification tasks (currently empty)
classify_id = ""


# ============================================================================
# PROMPT RETRIEVAL FUNCTION
# ============================================================================

def get_prompt(type):
    """
    Returns the appropriate prompt based on the specified type.
    
    Args:
        type (str): The type of prompt needed ('final_response', 'classify', or other)
    
    Returns:
        list: A list containing a dictionary with the prompt text
    """
    prompt = ""
    match type:
        case "final_response":
            prompt = system_prompt
        case "classify":
            prompt = classify_prompt
        case _:
            prompt = error_Prompt
    return [
        {
            "text": prompt
        }
    ]


# ============================================================================
# CONFIGURATION RETRIEVAL FUNCTION
# ============================================================================

# Get various config settings based on which step will use them
def get_config(type):
    """
    Returns configuration settings based on the specified type.
    
    Args:
        type (str): The type of configuration needed
    
    Returns:
        dict: Configuration dictionary containing temperature and other settings
    """
    match type:
        case "final_response":
            return {
                "temperature": 0.4,
            }
        case "classify":
            return {
                "temperature": 0.1,
            }
        case _:
            return {
                "temperature": 0.3,
            }


# ============================================================================
# MODEL ID RETRIEVAL FUNCTION
# ============================================================================

def get_id(type):
    """
    Returns the appropriate model ID based on the specified type.
    
    Args:
        type (str): The type of model ID needed
    
    Returns:
        str: The model ID string
    """
    match type:
        case "final_response":
            return final_response_id
        case "classify":
            return classify_id
        case _:
            return "us.amazon.nova-pro-v1:0"