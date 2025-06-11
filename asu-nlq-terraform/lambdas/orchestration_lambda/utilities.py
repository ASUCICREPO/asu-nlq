import boto3
from botocore.exceptions import ClientError
import json
import constants
import sqlite3
import pandas as pd


def get_clients():
    """Initialize and return all AWS service clients"""
    
    apiGatewayURL = "https" + constants.API_GATEWAY_URL[3:] + "/prod"  # Ensure URL starts with https and ends with /prod
    print("API Gateway URL:", apiGatewayURL)
    
    # Initialize AWS service clients
    gateway = boto3.client("apigatewaymanagementapi", endpoint_url=apiGatewayURL)
    bedrock = boto3.client('bedrock-runtime')
    s3_client = boto3.client('s3')
    
    return gateway, bedrock, s3_client


# Initialize AWS service clients
gateway, bedrock, s3_client = get_clients()


def send_to_gateway(connectionId, json_data):
    """Send JSON data to client via WebSocket connection"""
    
    gateway.post_to_connection(
        ConnectionId=connectionId, 
        Data=json.dumps(json_data)
    )
    return


def converse_with_model(modelId, chatHistory, config=None, system=None, streaming=False):
    """Get response from Bedrock AI model with optional streaming"""
    
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
    
    return response


def parse_and_send_response(response, connectionId, classic=None, pure=None):
    """Parse streaming response and send events to client in real-time"""

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
        return
    
    stream = response.get('stream')
    if stream:
        for event in stream:
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
                print("Unhandled event type:", event)


def download_s3_json(bucket_name=None, file_key=None):
    """Download and parse JSON file from S3 bucket"""
    
    # Use default values from constants if not provided
    bucket = bucket_name or constants.DATABASE_DESCRIPTIONS_S3_NAME
    key = file_key or (constants.TEMPLATE_NAME + ".json")
    
    # Download the JSON file from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    
    # Read file content and parse as JSON
    file_content = response['Body'].read()
    return json.loads(file_content)


def create_history(chatHistory):
    """Create a formatted conversation history for AI model input"""
    
    history = ""
    for message in chatHistory:
        role = message["role"]
        content = message["content"][0]["text"]
        history += f"{role}: {content}\n\n"
    
    return history


def download_database_from_s3(bucket_name=None, file_key=None):
    """Download database file from S3 and return local filepath"""

    # Use default values from constants if not provided
    bucket = bucket_name or constants.DATABASE_DESCRIPTIONS_S3_NAME
    key = file_key or (constants.DATABASE_NAME + ".db")
    
    # Set local path in /tmp directory
    local_path = f"/tmp/{constants.DATABASE_NAME}"
    
    # Download the database file from S3
    s3_client.download_file(bucket, key, local_path)
    return local_path


def execute_sql_query(db_path, sql_statement):
    """Execute SQL query on database and return results as DataFrame"""
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    
    # Execute query and create DataFrame
    df_result = pd.read_sql_query(sql_statement, conn)
    
    # Close the connection
    conn.close()
    
    return df_result.to_string()
        
   