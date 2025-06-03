import json
from chatbot_config import get_prompt, get_config, get_id
from utilities import converse_with_model, parse_and_send_response, download_s3_json, create_history

def orchestrate(event):
    """Main orchestration logic for processing chat requests"""
    
    print("Starting orchestration with event:", event)

    # Extract WebSocket connection ID for response routing
    connectionId = event["requestContext"]["connectionId"]

    # Parse chat history from the WebSocket message body
    chatHistory = json.loads(event["body"])["messages"]

    # Get database schema from S3
    schema = download_s3_json()

    # Classify the user's query using a classification model
    classification = classify_query(chatHistory[-1], chatHistory, schema)
    print("Classification:", classification)

    # Send classification result back to the client
    parse_and_send_response(classification, connectionId, classic=True)

    # # Get AI model response using streaming for real-time delivery
    # response = converse_with_model(
    #     get_id("final_response"), 
    #     chatHistory, 
    #     config=get_config("final_response"), 
    #     system=get_prompt("final_response"),
    #     streaming=True
    # )

    # # Stream the AI response back to the client
    # parse_and_send_response(response, connectionId)

    print("Orchestration completed")
    return

def classify_query(message, chatHistory, schema):
    """Classify the user's query using a classification prompted model - outputs json document"""

    history = create_history(chatHistory)

    # Get AI model response
    response = converse_with_model(
        get_id("classify"),
        [message],
        config=get_config("classify"),
        system=get_prompt("classify", message=message["content"][0]["text"], chatHistory=history, schema=json.dumps(schema, indent=4)),
        streaming=False
    )

    return response