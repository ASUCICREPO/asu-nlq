import json
from chatbot_config import get_prompt, get_config, get_id
from utilities import converse_with_model, parse_and_send_response, download_s3_json, create_history, download_database_from_s3, execute_sql_query

def orchestrate(event):
    """Main orchestration logic for processing chat requests"""
    print("Starting orchestration with event:", event)
    
    # Extract WebSocket connection ID for response routing
    connectionId = event["requestContext"]["connectionId"]
    
    try:
        # Parse chat history from the WebSocket message body
        chatHistory = json.loads(event["body"])["messages"]
        
        # Get database schema from S3
        schema = download_s3_json()
        
        # Classify the user's query using a classification model, and respond to it
        classification = json.loads(classify_query(chatHistory[-1], chatHistory, schema)["output"]["message"]["content"][0]["text"])
        
        # Check the classification type and respond accordingly
        if (classification["classification"] == "SQL_Query"):

            # Respond to the SQL query classification and send it to the client #TODO implement this
            response = respond_to_sql_query(chatHistory=chatHistory, schema=schema, reasoning=classification)
            parse_and_send_response(response, connectionId)

        elif (classification["classification"] == "NoSQL_Query"):

            # Respond to the NoSQL query classification and send it to the client
            response = respond_to_nosql_query(chatHistory, schema, classification)
            parse_and_send_response(response, connectionId)

        elif (classification["classification"] == "Dangerous"): #TODO add retriver for basic responses, error, dangerous etc

            # Respond to the dangerous query
            parse_and_send_response("I'm sorry, I cannot answer that question. Please make a new chat.", connectionId, classic=True, pure=True)

        else:
            # Send error message for unknown classification
            raise ValueError("Unknown classification type: {}".format(classification["classification"]))  
              
    except Exception as e:
        # Handle any unexpected errors
        error_msg = f"Unexpected error in orchestrate: {str(e)}"
        print(f"General error: {error_msg}")
        parse_and_send_response("An unexpected error occurred. Please try again later.", connectionId, classic=True, pure=True) #TODO add retriver for basic responses, error, dangerous etc
    
    print("Orchestration completed")
    return 



    # # download database from S3
    # database_path = download_database_from_s3()

    # query = "SELECT Term, SUM(Students) as TotalStudents FROM asu_facts WHERE Undergraduate_or_Graduate = 'Undergraduate' AND College = 'Engineering' AND Term IN ('Fall 2021', 'Fall 2022') GROUP BY Term ORDER BY Term ASC;"

    # results = execute_sql_query(database_path, query)

    # print("Results:", results)




# Classify the user's query using a classification prompted model
def classify_query(message, chatHistory, schema):
    """Classify the user's query using a classification prompted model - outputs json document"""

    history = create_history(chatHistory)

    schema=json.dumps(schema, indent=4)

    # Get AI model response
    response = converse_with_model(
        get_id("classify"),
        [message],
        config=get_config("classify"),
        system=get_prompt("classify", message=message["content"][0]["text"], chatHistory=history, schema=schema),
        streaming=False
    )

    return response

# Respond to a NoSQL query classification
def respond_to_nosql_query(chatHistory, scheme, reasoning):
    """Respond to a NoSQL query classification"""

    schema=json.dumps(scheme, indent=4)

    reasoning=reasoning["reasoning"]

    response = converse_with_model(
        get_id("no_sql"), 
        chatHistory, 
        config=get_config("no_sql"), 
        system=get_prompt("no_sql", chatHistory=chatHistory, schema=schema, reasoning=reasoning),
        streaming=True
    )

    return response

# Respond to a SQL query classification #TODO implement this
def respond_to_sql_query(chatHistory, schema, reasoning):
    """Respond to a SQL query classification"""

    # Create a very specific question to generate SQL on
    response = create_question(message=chatHistory[-1], chatHistory=chatHistory, schema=schema, reasoning=reasoning)

    # Parse the response to get the specific question
    specific_question = json.loads(response["output"]["message"]["content"][0]["text"])

    # Get attributes JSON with the database schema
    attribute_json = json.loads(get_attributes_json(message=specific_question["improved_question"], schema=schema)["output"]["message"]["content"][0]["text"])

    # Get SQL queries based on the attributes JSON and specific question and the schema
    queries = json.loads(get_sql_queries(message=specific_question["improved_question"], schema=schema, attributes=json.dumps(attribute_json, indent=4))["output"]["message"]["content"][0]["text"])

    # Download the database from S3
    database_path = download_database_from_s3()

    # Execute the SQL queries and get the results
    results = ""
    for query in queries["queries"]:
        results += query + "\n" + execute_sql_query(database_path, query) + "\n\n"

    # create the final response
    final_response = get_final_response(chatHistory=chatHistory, schema=schema, specific_question=specific_question["improved_question"], results=results)


    return final_response

# Create a very specific question to generate SQL on
def create_question(message, chatHistory, schema, reasoning):
    """Create a very specific question to generate SQL on"""

    chatHistory=create_history(chatHistory)

    schema = json.dumps(schema, indent=4)

    reasoning = reasoning["reasoning"]

    response = converse_with_model(
        get_id("create_question"),
        [message],
        config=get_config("create_question"),
        system=get_prompt("create_question", message=message["content"][0]["text"], chatHistory=chatHistory, schema=schema, reasoning=reasoning),
        streaming=False
    )

    return response

# Get attributes JSON for the database schema
def get_attributes_json(message, schema):
    """Get attributes JSON for the database schema"""

    schema=json.dumps(schema, indent=4)

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
        system=get_prompt("attributes_json", message=message, schema=schema),
        streaming=False
    )

    
    return response

# Get SQL queries based on the attributes JSON and specific question and the schema
def get_sql_queries(message, schema, attributes):
    """Get SQL queries based on the attributes JSON and specific question and the schema"""

    # Format the schema and attributes for the model
    schema = json.dumps(schema, indent=4)

    # Format the message for the model
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
        system=get_prompt("sql_generation", message=message, schema=schema, attributes=attributes),
        streaming=False
    )
    print("SQL queries:", response)
    

    return response

# Get the final response based on the chat history, schema, specific question and results
def get_final_response(chatHistory, schema, specific_question, results):
    """Get the final response based on the chat history, schema, specific question and results"""

    schema = json.dumps(schema, indent=4)

    response = converse_with_model(
        get_id("final_response"),
        chatHistory,
        config=get_config("final_response"),
        system=get_prompt("final_response", message=specific_question, schema=schema, results=results),
        streaming=True
    )

    return response


   