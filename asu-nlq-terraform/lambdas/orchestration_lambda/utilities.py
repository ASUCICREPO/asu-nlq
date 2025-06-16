import boto3
from botocore.exceptions import ClientError
import json
import logging
import traceback
import constants
import sqlite3
import pandas as pd

import constants  # This configures logging

logger = logging.getLogger(__name__)


def get_clients():
    """Initialize and return all AWS service clients"""
    logger.info("Initializing AWS clients")
    
    try:
        apiGatewayURL = "https" + constants.API_GATEWAY_URL[3:] + "/prod"
        logger.info(f"API Gateway URL: {apiGatewayURL}")
        
        # Initialize AWS service clients
        gateway = boto3.client("apigatewaymanagementapi", endpoint_url=apiGatewayURL)
        bedrock = boto3.client('bedrock-runtime')
        s3_client = boto3.client('s3')
        
        logger.info("AWS clients initialized successfully")
        return gateway, bedrock, s3_client
        
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {e}")
        raise


# Initialize AWS service clients
gateway, bedrock, s3_client = get_clients()


def send_to_gateway(connectionId, json_data):
    """Send JSON data to client via WebSocket connection"""
    logger.info(f"Sending data to connection: {connectionId}")
    
    try:
        gateway.post_to_connection(
            ConnectionId=connectionId, 
            Data=json.dumps(json_data)
        )
        logger.info("Data sent successfully")
        
    except ClientError as e:
        logger.error(f"Failed to send to gateway: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending to gateway: {e}")
        raise


def converse_with_model(modelId, chatHistory, config=None, system=None, streaming=False):
    """Get response from Bedrock AI model with optional streaming"""
    logger.info(f"Conversing with model: {modelId}, streaming: {streaming}")
    
    try:
        if streaming:
            response = bedrock.converse_stream(
                modelId=modelId,
                messages=chatHistory,
                inferenceConfig=config,
                system=system
            )
        else:
            response = bedrock.converse(
                modelId=modelId,
                messages=chatHistory,
                inferenceConfig=config,
                system=system
            )
        
        logger.info("Model conversation completed")
        return response
        
    except ClientError as e:
        logger.error(f"Bedrock client error: {e}")
        raise
    except Exception as e:
        logger.error(f"Model conversation failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def parse_and_send_response(response, connectionId, classic=None, pure=None):
    """Parse streaming response and send events to client in real-time"""
    logger.info("Parsing and sending response")
    
    try:
        if classic:
            if pure:
                json_data = {
                    "message": response,
                }
            else:
                json_data = {
                    "message": response["output"]["message"]["content"][0]["text"],
                }
            send_to_gateway(connectionId, json_data)
            logger.info("Classic response sent")
            return
        
        # Handle streaming response
        stream = response.get('stream')
        if stream:
            event_count = 0
            for event in stream:
                event_count += 1
                
                # Handle content delta events (partial response chunks)
                if "contentBlockDelta" in event:
                    contentBlockDelta = event["contentBlockDelta"]
                    json_data = {
                        "type": "contentBlockDelta",
                        "data": contentBlockDelta
                    }
                    send_to_gateway(connectionId, json_data)
                
                # Handle message start events
                elif "messageStart" in event:
                    json_data = {
                        "type": "messageStart",
                        "data": event["messageStart"]
                    }
                    send_to_gateway(connectionId, json_data)
                
                # Handle message completion events
                elif "messageStop" in event:
                    json_data = {
                        "type": "messageStop",
                        "data": event["messageStop"]
                    }
                    send_to_gateway(connectionId, json_data)
                
                # Log any unhandled event types
                else:
                    logger.warning(f"Unhandled event type: {event}")
            
            logger.info(f"Processed {event_count} streaming events")
        
    except Exception as e:
        logger.error(f"Response parsing failed: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise


def download_s3_json(bucket_name=None, file_key=None):
    """Download and parse JSON file from S3 bucket"""
    bucket = bucket_name or constants.DATABASE_DESCRIPTIONS_S3_NAME
    key = file_key or (constants.TEMPLATE_NAME + ".json")
    
    logger.info(f"Downloading JSON from S3: {bucket}/{key}")
    
    try:
        # Download the JSON file from S3
        response = s3_client.get_object(Bucket=bucket, Key=key)
        
        # Read file content and parse as JSON
        file_content = response['Body'].read()
        json_data = json.loads(file_content)
        
        logger.info("JSON file downloaded and parsed successfully")
        return json_data
        
    except ClientError as e:
        logger.error(f"S3 client error downloading JSON: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error downloading JSON: {e}")
        raise


def create_history(chatHistory):
    """Create a formatted conversation history for AI model input"""
    logger.info(f"Creating history from {len(chatHistory)} messages")
    
    try:
        history = ""
        for message in chatHistory:
            role = message["role"]
            content = message["content"][0]["text"]
            history += f"{role}: {content}\n\n"
        
        logger.info("Chat history formatted successfully")
        return history
        
    except KeyError as e:
        logger.error(f"Invalid message format in chat history: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to create history: {e}")
        raise


def download_database_from_s3(bucket_name=None, file_key=None):
    """Download database file from S3 and return local filepath"""
    bucket = bucket_name or constants.DATABASE_DESCRIPTIONS_S3_NAME
    key = file_key or (constants.DATABASE_NAME + ".db")
    local_path = f"/tmp/{constants.DATABASE_NAME}"
    
    logger.info(f"Downloading database from S3: {bucket}/{key}")
    
    try:
        # Download the database file from S3
        s3_client.download_file(bucket, key, local_path)
        
        logger.info(f"Database downloaded to: {local_path}")
        return local_path
        
    except ClientError as e:
        logger.error(f"S3 client error downloading database: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to download database: {e}")
        raise


def execute_sql_query(db_path, sql_statement):
    """Execute SQL query on database and return results as DataFrame"""
    logger.info(f"Executing SQL query on: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        
        # Execute query and create DataFrame
        df_result = pd.read_sql_query(sql_statement, conn)
        
        # Close the connection
        conn.close()
        
        logger.info(f"Query executed successfully, returned {len(df_result)} rows")
        return df_result.to_string()
        
    except sqlite3.Error as e:
        logger.error(f"SQLite error: {e}")
        logger.error(f"Failed query: {sql_statement}")
        raise
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        logger.error(f"Failed query: {sql_statement}")
        raise