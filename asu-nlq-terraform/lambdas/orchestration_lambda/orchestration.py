import json
import logging
import traceback
from chatbot_config import get_prompt, get_config, get_id
from utilities import converse_with_model, parse_and_send_response, download_s3_json, create_history, download_database_from_s3, execute_sql_query

import constants  # This configures logging

logger = logging.getLogger(__name__)

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


def respond_to_sql_query(chatHistory, schema, reasoning):
    """
    Handle SQL queries through multi-stage pipeline:
    1. Create specific question
    2. Extract relevant attributes  
    3. Generate SQL queries
    4. Execute queries on database
    5. Generate natural language response
    """
    logger.info("Starting SQL query pipeline")
    
    try:
        # Stage 1: Create specific question
        logger.info("Creating specific question")
        response = create_question(message=chatHistory[-1], chatHistory=chatHistory, schema=schema, reasoning=reasoning)
        specific_question = json.loads(response["output"]["message"]["content"][0]["text"])

        # Stage 2: Extract relevant attributes
        logger.info("Extracting database attributes")
        attribute_response = get_attributes_json(message=specific_question["improved_question"], schema=schema)
        attribute_json = json.loads(attribute_response["output"]["message"]["content"][0]["text"])

        # Stage 3: Generate SQL queries
        logger.info("Generating SQL queries")
        queries_response = get_sql_queries(
            message=specific_question["improved_question"], 
            schema=schema, 
            attributes=json.dumps(attribute_json, indent=4)
        )
        queries = json.loads(queries_response["output"]["message"]["content"][0]["text"])

        # Stage 4: Execute queries
        logger.info("Executing SQL queries")
        database_path = download_database_from_s3()
        
        results = ""
        for query in queries["queries"]:
            try:
                query_result = execute_sql_query(database_path, query)
                results += f"{query}\n{query_result}\n\n"
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                results += f"{query}\nError: {str(e)}\n\n"

        # Stage 5: Generate final response
        logger.info("Generating final response")
        final_response = get_final_response(
            chatHistory=chatHistory, 
            schema=schema, 
            specific_question=specific_question["improved_question"], 
            results=results
        )
        
        logger.info("SQL pipeline completed")
        return final_response
        
    except Exception as e:
        logger.error(f"SQL pipeline failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


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


def get_attributes_json(message, schema):
    """
    Extract relevant database attributes for the given query.
    Identifies which tables and columns are needed for the question.
    """
    logger.info("Extracting relevant attributes")
    
    try:
        schema_json = json.dumps(schema, indent=4)

        message_formatted = {
            "role": "user",
            "content": [{
                "text": message,
            }]
        }
        
        response = converse_with_model(
            get_id("attributes_json"),
            [message_formatted],
            config=get_config("attributes_json"),
            system=get_prompt("attributes_json", message=message, schema=schema_json),
            streaming=False
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Attribute extraction failed: {e}")
        raise


def get_sql_queries(message, schema, attributes):
    """
    Generate optimized SQL queries based on the question and relevant attributes.
    Creates efficient queries using identified schema elements.
    """
    logger.info("Generating SQL queries")
    
    try:
        schema_json = json.dumps(schema, indent=4)

        message_formatted = {
            "role": "user",
            "content": [{
                "text": message,
            }]
        }

        response = converse_with_model(
            get_id("sql_generation"),
            [message_formatted],
            config=get_config("sql_generation"),
            system=get_prompt("sql_generation", message=message, schema=schema_json, attributes=attributes),
            streaming=False
        )
        
        logger.info("SQL generation completed")
        return response
        
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        raise


def get_final_response(chatHistory, schema, specific_question, results):
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
            system=get_prompt("final_response", message=specific_question, schema=schema_json, results=results),
            streaming=True
        )
        
        logger.info("Final response generated")
        return response
        
    except Exception as e:
        logger.error(f"Final response generation failed: {e}")
        raise