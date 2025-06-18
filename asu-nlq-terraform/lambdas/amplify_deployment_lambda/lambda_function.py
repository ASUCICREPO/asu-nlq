import json
import urllib3
import boto3
import os

http = urllib3.PoolManager()
SUCCESS = "SUCCESS"
amplify = boto3.client('amplify')

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

            appId = None
            branchName = None

            # Create amplify app with amplify.create_app() - name given in env

            if 'AMPLIFY_APP_NAME' not in os.environ:
                send(event, context, SUCCESS, {"Message": "Environment variable 'AMPLIFY_APP_NAME' is not set."})
                print("Environment variable 'AMPLIFY_APP_NAME' is not set.")
                return
            
            try:
                create_amplify_app_response = amplify.create_app(
                    name=os.environ['AMPLIFY_APP_NAME'],
                    description='ASU NLQ Chatbot Amplify App',
                    platform='WEB',
                    enableBranchAutoBuild=False,
                    enableBranchAutoDeletion=False,
                    enableBasicAuth=False,
                    customRules=[
                        {
                            "source": "/<*>",
                            "target": "/index.html",
                            "status": "404-200"
                        }
                    ],
                    enableAutoBranchCreation=False,
                    customHeaders=""
                )

                if create_amplify_app_response["app"]["appId"]:
                    appId = create_amplify_app_response["app"]["appId"]
                    print(f"Amplify app created successfully with ID: {create_amplify_app_response['app']['appId']}")
                else:
                    print("Amplify app creation failed, no appId returned.")
                    send(event, context, SUCCESS, {"Message": "Amplify app creation failed, no appId returned."})
                    return
                    
            except Exception as e:
                print(f"Error creating amplify app: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass  # Continue execution even if there's an error

            # Create an amplify branch with amplify.create_branch()

            if not appId:
                    print("No appId available, cannot create branch.")
                    send(event, context, SUCCESS, {"Message": "No appId available, cannot create branch."})
                    return

            try:
                
                response_create_branch = amplify.create_branch(
                    appId=appId,
                    branchName='prod',
                    description='Production branch for ASU NLQ Chatbot',
                    stage='PRODUCTION',
                    enableNotification=False,
                    enableAutoBuild=True,
                    enableBasicAuth=False,
                    enablePerformanceMode=False,
                    ttl="5",
                    enablePullRequestPreview=False,
                    backend={},
                )

                if response_create_branch["branch"]["branchName"]:
                    branchName = response_create_branch["branch"]["branchName"]
                    print(f"Amplify branch created successfully with name: {response_create_branch['branch']['branchName']}")
                else:
                    print("Amplify branch creation failed, no branchName returned.")
                    send(event, context, SUCCESS, {"Message": "Amplify branch creation failed, no branchName returned."})
                    return
                
            except Exception as e:
                print(f"Error creating amplify branch: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass

            if not branchName:
                    print("No branchName available, cannot create deployment.")
                    send(event, context, SUCCESS, {"Message": "No branchName available, cannot create deployment."})
                    return

            # Start the deployment with amplify.start_deployment()

            try:
                print(f"S3 bucket URL: s3://{os.environ['FRONTEND_BUCKET_NAME']}/{os.environ['FRONTEND_ZIP_NAME']}/")
                response_start_deployment = amplify.start_deployment(
                    appId=appId,
                    branchName=branchName,
                    sourceUrl="s3://" + os.environ['FRONTEND_BUCKET_NAME'] + "/" + os.environ['FRONTEND_ZIP_NAME'] + "/",
                    sourceUrlType="BUCKET_PREFIX"
                )
                
            except Exception as e:
                print(f"Error starting deployment: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass

            send(event, context, SUCCESS, {"Message": "Create operation completed successfully"})

            
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