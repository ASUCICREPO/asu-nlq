import boto3
from botocore.exceptions import ClientError
import json
import os
import constants


def get_clients():
    """Initialize and return all AWS service clients"""
    
    # Validate API Gateway URL from environment
    if os.environ.get("API_GATEWAY_URL") is None:
        raise ValueError("API Gateway URL not set in environment variables")
    
    apiGatewayURL = os.environ["API_GATEWAY_URL"]
    
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


def parse_and_send_response(response, connectionId):
    """Parse streaming response and send events to client in real-time"""
    
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
    bucket = bucket_name or os.environ["DATABASE_DESCRIPTIONS_S3_NAME"]
    key = file_key or constants.DATABASE_SCHEMA_TEMPLATE_FILENAME
    
    # Download the JSON file from S3
    response = s3_client.get_object(Bucket=bucket, Key=key)
    
    # Read file content and parse as JSON
    file_content = response['Body'].read()
    return json.loads(file_content)