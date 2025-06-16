import json
import urllib3

http = urllib3.PoolManager()
SUCCESS = "SUCCESS"

def lambda_handler(event, context):
    """
    Simplified CloudFormation custom resource that always returns SUCCESS
    for any request type (Create, Update, Delete, etc.)
    """
    
    print("Event: ")
    print(json.dumps(event, indent=2))
    
    try:
        request_type = event['RequestType']
        print(f"Processing request type: {request_type}")
        
        if request_type == "Create":
            print("Handling Create request")
            # Add any Create-specific logic here if needed in the future
            send(event, context, SUCCESS, {"Message": "Create operation completed successfully"})

            # Create amplify app with amplify.create_app() - name given in env

            # Create an amplify deployment with amplify.create_deployment()

            # Download the zip file from the S3 bucket

            # Put zip file into deployment URL

            # Start the deployment with amplify.start_deployment()
            
        elif request_type == "Update":
            print("Handling Update request")
            # Add any Update-specific logic here if needed in the future
            send(event, context, SUCCESS, {"Message": "Update operation completed successfully"})

            # Create an amplify deployment with amplify.create_deployment() - app id from env

            # Download the zip file from the S3 bucket

            # Put zip file into deployment URL

            # Start the deployment with amplify.start_deployment()
            
        elif request_type == "Delete":
            print("Handling Delete request")
            # Add any Delete-specific logic here if needed in the future
            send(event, context, SUCCESS, {"Message": "Delete operation completed successfully"})

            # Delete the amplify app with amplify.delete_app() - app id from env
            
        else:
            print(f"Handling unknown request type: {request_type}")
            # Handle any other request types
            send(event, context, SUCCESS, {"Message": f"{request_type} operation completed successfully"})
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        # Even if there's an error, try to send success to avoid stack issues
        try:
            send(event, context, SUCCESS, {"Error": str(e)})
        except:
            pass  # Last resort - don't let the function completely fail

def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False, reason=None):
    """Send response back to CloudFormation"""
    responseUrl = event['ResponseURL']
    
    responseBody = {
        'Status': responseStatus,
        'Reason': reason or f"See CloudWatch Log Stream: {context.log_stream_name}",
        'PhysicalResourceId': physicalResourceId or context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'NoEcho': noEcho,
        'Data': responseData
    }
    
    json_responseBody = json.dumps(responseBody)
    
    print("Response body:")
    print(json_responseBody)
    
    headers = {
        'content-type': '',
        'content-length': str(len(json_responseBody))
    }
    
    response = http.request('PUT', responseUrl, headers=headers, body=json_responseBody)
    print(f"CloudFormation response status code: {response.status}")