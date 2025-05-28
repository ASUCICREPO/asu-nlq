import boto3
import json
import os

# The Lambda main function handler
def lambda_handler(event, context):

    # Check if this is the initial call or the background processing call
    if event.get('background_processing'):

        # This is the background processing execution
        orchestrate(event)
        return {
            "statusCode": 200
        }
    
    
    # Self-invoke for background processing
    lambda_client = boto3.client('lambda')
    background_event = event.copy()
    background_event['background_processing'] = True
    
    # Invoke the lambda so that it actually does the orchestration
    lambda_client.invoke(
        FunctionName=context.function_name,
        InvocationType='Event',
        Payload=json.dumps(background_event)
    )
    
    return {
        "statusCode": 200
    }


# The main orchestration logic
def orchestrate(event):

    # Do the orchestration logic here
    print("Starting orchestration with event:", event)


    # Extract the connection ID from the event
    connectionId = event["requestContext"]["connectionId"]

    # Create a response message
    response_message = {
        "message": "Working test!"
    }

    # Send the response message back to the client
    send_to_gateway(connectionId, response_message)


    print("Orchestration completed")
    
    return


# Send a json packet body through the gateway to the client
def send_to_gateway(connectionId, json_data):
    
    # Get the API Gateway URL from environment variables
    if os.environ.get("API_GATEWAY_URL") is None:
        raise ValueError("API Gateway URL not set in environment variables")
    else:
        apiGatewayURL = os.environ["API_GATEWAY_URL"]

    # Create a client for the API Gateway Management API
    gateway = boto3.client("apigatewaymanagementapi", endpoint_url=apiGatewayURL)

    # Send the response body back through the gateway to the client
    gateway.post_to_connection(ConnectionId=connectionId, Data=json.dumps(json_data))

    return


# Converse with model through streaming response
def converse_with_model_streaming(message, modelId, chatHistory=None, config=None, system=None):

    bedrock = boto3.client('bedrock-runtime')





    response = bedrock.converse_stream(
        modelId=modelId,
        messages=chatHistory,
        inferenceConfig=config,
        system=system
    )

    return response
