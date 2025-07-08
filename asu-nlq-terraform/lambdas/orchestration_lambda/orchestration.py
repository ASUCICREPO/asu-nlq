import json
import logging
import traceback
from chatbot_config import get_prompt, get_config, get_id
from utilities import (
    converse_with_model,
    parse_and_send_response,    
    download_s3_json,
    create_history,
    execute_knowledge_base_query,
    format_results_for_response
)
import constants  # This configures logging
logger = logging.getLogger(__name__)


# Orchestrate the chat request processing
def orchestrate(event):
    """
    Main orchestration function for processing chat requests via WebSocket.
    
    Extracts connection info, parses messages, classifies queries, and routes
    to appropriate handlers (SQL, NoSQL, or dangerous query blocking).
    """
    logger.info("Starting orchestration")
    
    # Extract WebSocket connection ID
    try:
        connectionId = event["requestContext"]["connectionId"]
        logger.info(f"Processing connection: {connectionId}")
    except KeyError:
        logger.error("Failed to extract connection ID")
        return None
    
    try:
        # Parse chat history
        chatHistory = json.loads(event["body"])["messages"]

        # Ensure updated chat history to include "BREAK_TOKEN" for streaming responses to not screw up prompting
        print("Chat history before fix:", chatHistory)  # Debugging line
        chatHistory = fix_chat_history(chatHistory)
        print("Chat history after fix:", chatHistory)  # Debugging line

        logger.info(f"Parsed {len(chatHistory)} messages")
        
        # Get database schema from S3
        schema = download_s3_json()
        logger.info("Downloaded schema from S3")
        
        # Classify the user's query
        classification_response = classify_query(chatHistory[-1], chatHistory, schema)
        classification = json.loads(classification_response["output"]["message"]["content"][0]["text"])
        logger.info(f"Query classified as: {classification['classification']}")
        
        # Route to appropriate handler
        if classification["classification"] == "SQL_Query":
            response = respond_to_sql_query(chatHistory=chatHistory, schema=schema, reasoning=classification)
            parse_and_send_response(response, connectionId)
            logger.info("SQL query processed successfully")

        elif classification["classification"] == "NoSQL_Query":
            response = respond_to_nosql_query(chatHistory, schema, classification)
            parse_and_send_response(response, connectionId)
            logger.info("NoSQL query processed successfully")

        elif classification["classification"] == "Dangerous":
            logger.warning("Dangerous query blocked")
            parse_and_send_response("I'm sorry, I cannot answer that question. Please make a new chat.", 
                                  connectionId, classic=True, pure=True)

        else:
            logger.error(f"Unknown classification: {classification['classification']}")
            raise ValueError(f"Unknown classification type: {classification['classification']}")
              
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}")
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        
        if connectionId:
            parse_and_send_response("An unexpected error occurred. Please try again later.", 
                                  connectionId, classic=True, pure=True)
    
    logger.info("Orchestration completed")
    return None


# Classify the user's query to determine response strategy.
def classify_query(message, chatHistory, schema):
    """
    Classify the user's query using AI to determine response strategy.
    Returns classification with reasoning for routing decisions.
    """
    logger.info("Classifying user query")
    
    try:
        history = create_history(chatHistory)
        schema_json = json.dumps(schema, indent=4)

        response = converse_with_model(
            get_id("classify"),
            [message],
            config=get_config("classify"),
            system=get_prompt("classify", message=message["content"][0]["text"], chatHistory=history, schema=schema_json),
            streaming=False
        )
        
        logger.info("Query classification completed")
        return response
        
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        raise


# Respond to NoSQL queries by streaming responses.
def respond_to_nosql_query(chatHistory, schema, reasoning):
    """
    Handle NoSQL database queries with streaming responses.
    Processes non-relational database operations and document queries.
    """
    logger.info("Processing NoSQL query")
    
    try:
        schema_json = json.dumps(schema, indent=4)
        query_reasoning = reasoning.get("reasoning", "")

        response = converse_with_model(
            get_id("no_sql"), 
            chatHistory, 
            config=get_config("no_sql"), 
            system=get_prompt("no_sql", chatHistory=chatHistory, schema=schema_json, reasoning=query_reasoning),
            streaming=True
        )
        
        logger.info("NoSQL query completed")
        return response
        
    except Exception as e:
        logger.error(f"NoSQL query failed: {e}")
        raise


# Respond to SQL queries by orchestrating a multi-stage pipeline.
def respond_to_sql_query(chatHistory, schema, reasoning):
    """
    Handle SQL queries through multi-stage pipeline:
    1. Create specific question from user input
    2. Retrieve answers from the database
    3. Generate final response based on query results.
    This orchestrates the entire SQL query process, ensuring robust error handling.
    """
    logger.info("Starting SQL query pipeline")
    
    try:
        # Stage 1: Create specific question
        logger.info("Creating specific question")
        response = create_question(message=chatHistory[-1], chatHistory=chatHistory, schema=schema, reasoning=reasoning)
        specific_question_json = json.loads(response["output"]["message"]["content"][0]["text"])

        # Check if the improved question is present in the response
        if "improved_questions" not in specific_question_json:
            logger.error("Improved question not found in response")
            raise ValueError("Improved question missing from response")
        specific_question = specific_question_json["improved_questions"]
        print(f"Specific question created: {specific_question}") # Don't use logger, this should always be printed to the console


        # Stage 2: get answers from the database
        logger.info("Retrieving answers from the database")
        results = retrieve_answers_from_database(
            questions=specific_question, 
        )
        # Check if results are empty
        if not results:
            logger.warning("No results found for the specific question")
            results = "No results found for your query."

        # Format results for response
        results = format_results_for_response(specific_question, results)


        # Stage 3: Generate final response
        logger.info("Generating final response")
        final_response = get_final_response(
            chatHistory=chatHistory, 
            schema=schema, 
            results=results
        )
        
        logger.info("SQL pipeline completed")
        return final_response
        
    except Exception as e:
        logger.error(f"SQL pipeline failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


# Create a specific question based on user input and schema.
def create_question(message, chatHistory, schema, reasoning):
    """
    Transform user input into a specific, actionable database question.
    Uses conversation context and schema to refine vague queries.
    """
    logger.info("Creating specific question")
    
    try:
        formatted_history = create_history(chatHistory)
        schema_json = json.dumps(schema, indent=4)
        query_reasoning = reasoning.get("reasoning", "")

        response = converse_with_model(
            get_id("create_question"),
            [message],
            config=get_config("create_question"),
            system=get_prompt(
                "create_question", 
                message=message["content"][0]["text"], 
                chatHistory=formatted_history, 
                schema=schema_json, 
                reasoning=query_reasoning
            ),
            streaming=False
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Question creation failed: {e}")
        raise


# Retrieve final response based on SQL query results.
def get_final_response(chatHistory, schema, results):
    """
    Convert SQL query results into natural language response.
    Synthesizes data into conversational format that answers the user's question.
    """
    logger.info("Generating final response")
    
    try:
        schema_json = json.dumps(schema, indent=4)

        response = converse_with_model(
            get_id("final_response"),
            chatHistory,
            config=get_config("final_response"),
            system=get_prompt("final_response", schema=schema_json, results=results),
            streaming=True
        )
        
        logger.info("Final response generated")
        return response
        
    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        raise


# Retrieve answers from the database based on the specific question.
def retrieve_answers_from_database(questions):
    """
    Retrieve answers from the database based on the specific question.
    This function executes the SQL queries and returns the results. - All inside bedrock knowledge bases
    """
    logger.info("Retrieving answers from the database")
    try:
        # Send question to the knowledge base
        results = execute_knowledge_base_query(questions)
        logger.info("Database query executed successfully")
        return results
    except Exception as e:
        logger.error(f"Database retrieval failed: {e}")
        raise


# Ensure chat history is updated to include "BREAK_TOKEN" for streaming responses.
def fix_chat_history(chatHistory):
    """
    Ensure chat history is updated to include "BREAK_TOKEN" for streaming responses.
    """
    for message in chatHistory:
        if message["role"] == "assistant":
            current_text = message["content"][0]["text"]
            if not current_text.endswith("BREAK_TOKEN"):
                message["content"][0]["text"] = current_text + "BREAK_TOKEN"
    return chatHistory

