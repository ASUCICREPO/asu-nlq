import json
from chatbot_config import get_prompt, get_config, get_id
from utilities import converse_with_model, parse_and_send_response, download_s3_json

def orchestrate(event):
    """Main orchestration logic for processing chat requests"""
    
    print("Starting orchestration with event:", event)

    # Extract WebSocket connection ID for response routing
    connectionId = event["requestContext"]["connectionId"]

    # Parse chat history from the WebSocket message body
    chatHistory = json.loads(event["body"])["messages"]

    document = download_s3_json() #TODO: remove, this is just for testing purposes

    test = converse_with_model( #TODO: remove, this is just for testing purposes
        get_id("final_response"),
        chatHistory,
        config=get_config("final_response"),
        system=get_prompt("final_response"),
        streaming=False
    )

    # Get AI model response using streaming for real-time delivery
    response = converse_with_model(
        get_id("final_response"), 
        chatHistory, 
        config=get_config("final_response"), 
        system=get_prompt("final_response"),
        streaming=True
    )

    # Stream the AI response back to the client
    parse_and_send_response(response, connectionId)

    print("Orchestration completed")
    return