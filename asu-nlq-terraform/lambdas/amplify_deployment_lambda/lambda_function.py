import json
import urllib3
import boto3
import os
import zipfile
import tempfile

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

            

            if 'AMPLIFY_APP_NAME' not in os.environ:
                send(event, context, SUCCESS, {"Message": "Environment variable 'AMPLIFY_APP_NAME' is not set."})
                print("Environment variable 'AMPLIFY_APP_NAME' is not set.")
                return
            
            # Unzip S3 bucket zip files
            try:

                response = extract_s3_zip(os.environ['FRONTEND_BUCKET_NAME'], "build.zip")
                if response['success']: 
                    print(f"Successfully extracted and uploaded {len(response['uploaded_files'])} files from {response['base_folder']}")     
                
            except:
                print("Error extracting zip file from S3 bucket.")
                send(event, context, SUCCESS, {"Message": "Error extracting zip file from S3 bucket."})
                pass



            # Create amplify app with amplify.create_app() - name given in env
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
                print(f"S3 bucket URL: s3://{os.environ['FRONTEND_BUCKET_NAME']}{os.environ['FRONTEND_FOLDER_NAME']}")
                response_start_deployment = amplify.start_deployment(
                    appId=appId,
                    branchName=branchName,
                    sourceUrl="s3://" + os.environ['FRONTEND_BUCKET_NAME'] + os.environ['FRONTEND_FOLDER_NAME'],
                    sourceUrlType="BUCKET_PREFIX"
                )
                
            except Exception as e:
                print(f"Error starting deployment: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass

            send(event, context, SUCCESS, {"Message": "Create operation completed successfully"})

            
        elif request_type == "Update":
            print("Handling Update request")

            # Handle unzip of new files and old file deletion

            # Unzip S3 bucket zip files
            try:
                response = extract_s3_zip(os.environ['FRONTEND_BUCKET_NAME'], "build.zip")
                if response['success']: 
                    print(f"Successfully extracted and uploaded {len(response['uploaded_files'])} files from {response['base_folder']}")     
                
            except:
                print("Error extracting zip file from S3 bucket.")
                send(event, context, SUCCESS, {"Message": "Error extracting zip file from S3 bucket."})
                pass

            # Get the app ID from the name

            if 'AMPLIFY_APP_NAME' not in os.environ:
                send(event, context, SUCCESS, {"Message": "Environment variable 'AMPLIFY_APP_NAME' is not set."})
                print("Environment variable 'AMPLIFY_APP_NAME' is not set.")
                return

            get_app_id_by_name_response = get_app_id_by_name(os.environ['AMPLIFY_APP_NAME'])
            if not get_app_id_by_name_response:
                print("No appId available, cannot update deployment.")
                send(event, context, SUCCESS, {"Message": "No appId available, cannot update deployment."})
                return
            
            appId = get_app_id_by_name_response


            # Create an amplify deployment with amplify.create_deployment()
            try:
                print(f"S3 bucket URL: s3://{os.environ['FRONTEND_BUCKET_NAME']}{os.environ['FRONTEND_FOLDER_NAME']}")
                response_start_deployment = amplify.start_deployment(
                    appId=appId,
                    branchName="prod",
                    sourceUrl="s3://" + os.environ['FRONTEND_BUCKET_NAME'] + os.environ['FRONTEND_FOLDER_NAME'],
                    sourceUrlType="BUCKET_PREFIX"
                )  
            except Exception as e:
                print(f"Error starting deployment: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass

            send(event, context, SUCCESS, {"Message": "Update operation completed successfully"})

            
        elif request_type == "Delete":
            print("Handling Delete request")

            # Get the app Id

            # Get the app ID from the name

            if 'AMPLIFY_APP_NAME' not in os.environ:
                send(event, context, SUCCESS, {"Message": "Environment variable 'AMPLIFY_APP_NAME' is not set."})
                print("Environment variable 'AMPLIFY_APP_NAME' is not set.")
                return

            get_app_id_by_name_response = get_app_id_by_name(os.environ['AMPLIFY_APP_NAME'])
            if not get_app_id_by_name_response:
                print("No appId available, cannot update deployment.")
                send(event, context, SUCCESS, {"Message": "No appId available, cannot update deployment."})
                return
            
            appId = get_app_id_by_name_response

            # Delete the amplify app with amplify.delete_app() - app id from env
            try:
                response = amplify.delete_app(
                    appId=appId,
                )

            except Exception as e:
                print(f"Error deleting amplify app: {str(e)}")
                send(event, context, SUCCESS, {"Error": str(e)})
                pass


            send(event, context, SUCCESS, {"Message": "Delete operation completed successfully"})

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


# Extracts a zip file from S3, uploads its contents back to S3
def extract_s3_zip(bucket_name, zip_key):
    # Function to extract a zip file from S3 and upload its contents back to S3
    s3_client = boto3.client('s3')
    try:
        # Determine the base folder name from the zip key
        base_folder = os.path.splitext(os.path.basename(zip_key))[0]
        
        # Check if base folder exists and clean up old files
        print(f"Checking for existing files in folder: {base_folder}")
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=f"{base_folder}/")
        
        objects_to_delete = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects_to_delete.append({'Key': obj['Key']})
        
        if objects_to_delete:
            print(f"Found {len(objects_to_delete)} existing files to delete")
            # Delete objects in batches (S3 allows max 1000 objects per delete request)
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i+1000]
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
            print(f"Successfully deleted {len(objects_to_delete)} existing files")
        else:
            print("No existing files found to delete")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the zip file from S3
            zip_file_path = os.path.join(temp_dir, 'downloaded.zip')
            print(f"Downloading {zip_key} from bucket {bucket_name}")
            s3_client.download_file(bucket_name, zip_key, zip_file_path)
            
            # Extract the zip file
            extract_dir = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                print(f"Extracted {len(zip_ref.namelist())} files")
            
            # Upload extracted files to S3
            uploaded_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    # Calculate relative path from extraction directory
                    relative_path = os.path.relpath(local_file_path, extract_dir)
                    # Create S3 key: base_folder + relative path
                    s3_key = f"{base_folder}/{relative_path}".replace(os.sep, '/')
                    
                    # Upload file to S3
                    print(f"Uploading {relative_path} to {s3_key}")
                    s3_client.upload_file(local_file_path, bucket_name, s3_key)
                    uploaded_files.append(s3_key)
            
            return {
                'success': True,
                'message': f"Successfully extracted and uploaded {len(uploaded_files)} files",
                'uploaded_files': uploaded_files,
                'base_folder': base_folder
            }
            
    except Exception as e:
        error_msg = f"Error extracting zip file: {str(e)}"
        print(error_msg)
        raise Exception(error_msg)
    

def get_app_id_by_name(name):
   """
   Retrieves the appId of an Amplify app by its name.
   
   Args:
       name (str): The name of the Amplify app to search for
       
   Returns:
       str: The appId if found, None otherwise
   """
   try:
       next_token = None
       
       while True:
           # Prepare parameters for list_apps call
           params = {}
           if next_token:
               params['nextToken'] = next_token
           
           # List apps with pagination support
           response = amplify.list_apps(**params)
           
           # Search for app with matching name
           for app in response.get('apps', []):
               if app.get('name') == name:
                   print(f"Found Amplify app '{name}' with ID: {app['appId']}")
                   return app['appId']
           
           # Check if there are more pages
           next_token = response.get('nextToken')
           if not next_token:
               break
               
       print(f"Amplify app with name '{name}' not found")
       return None
       
   except Exception as e:
       print(f"Error retrieving app ID for '{name}': {str(e)}")
       return None