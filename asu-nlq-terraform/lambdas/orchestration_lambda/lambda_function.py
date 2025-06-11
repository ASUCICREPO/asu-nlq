import boto3
import json
from orchestration import orchestrate


def lambda_handler(event, context):
    """Main Lambda entry point - handles both initial calls and background processing"""
    
    # Check if this is the background processing call
    if event.get('background_processing'):
        # Execute the main orchestration logic
        orchestrate(event)
        return {"statusCode": 200}
    
    # This is the initial WebSocket call - start background processing
    lambda_client = boto3.client('lambda')
    background_event = event.copy()
    background_event['background_processing'] = True
    
    # Self-invoke Lambda asynchronously to prevent WebSocket timeout
    lambda_client.invoke(
        FunctionName=context.function_name,
        InvocationType='Event',
        Payload=json.dumps(background_event)
    )
    
    # Return immediately to keep WebSocket connection alive
    return {"statusCode": 200}