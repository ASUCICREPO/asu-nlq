import json
import urllib3
import boto3
import os
import zipfile
import tempfile
import logging
from constants import (
    CFN_SUCCESS, CFN_FAILED, RESPONSE_MESSAGES, AMPLIFY_APP_NAME,
    FRONTEND_BUCKET_NAME, FRONTEND_FOLDER_NAME, AMPLIFY_APP_CONFIG,
    AMPLIFY_CUSTOM_RULES, AMPLIFY_BRANCH_CONFIG, AMPLIFY_DEPLOYMENT_CONFIG,
    DEFAULT_ZIP_FILE, S3_DELETE_BATCH_SIZE, APP_ID_FILE_NAME, APP_ID_FILE_KEY
)

logger = logging.getLogger(__name__)

# Initialize AWS clients and HTTP pool manager
http = urllib3.PoolManager()
amplify = boto3.client('amplify')
s3_client = boto3.client('s3')


def handle_create_request(event, context):
    """
    Handle CloudFormation Create request for Amplify app deployment.
    
    Orchestrates the complete create workflow:
    1. Extract and deploy frontend files from S3
    2. Create Amplify app and production branch
    3. Start initial deployment
    
    Args:
        event: CloudFormation event data
        context: Lambda context object
        
    Returns:
        None: Sends response directly to CloudFormation
    """
    logger.info("Starting Create request handling")
    
    try:
        # Stage 1: Extract and deploy frontend files
        logger.info("Extracting frontend files from S3")
        extract_response = extract_and_deploy_s3_zip(FRONTEND_BUCKET_NAME, DEFAULT_ZIP_FILE)
        if extract_response['success']:
            logger.info(f"Successfully extracted {len(extract_response['uploaded_files'])} files")
        else:
            logger.error("Failed to extract S3 zip file")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": RESPONSE_MESSAGES["ZIP_EXTRACTION_ERROR"]})
            return
        
        # Stage 2: Create Amplify app and branch
        logger.info("Creating Amplify app and branch")
        app_creation_response = create_amplify_app_and_branch()
        if not app_creation_response['success']:
            logger.error("Failed to create Amplify app or branch")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": app_creation_response['message']})
            return
        
        app_id = app_creation_response['app_id']
        branch_name = app_creation_response['branch_name']
        
        # Stage 2.5: Save app ID to S3 for future reference
        logger.info("Saving app ID to S3")
        save_response = save_app_id_to_s3(app_id)
        if not save_response['success']:
            logger.error("Failed to save app ID to S3")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": RESPONSE_MESSAGES["APP_ID_SAVE_ERROR"]})
            return
        
        # Stage 3: Start deployment
        logger.info("Starting Amplify deployment")
        deployment_response = deploy_to_amplify(app_id, branch_name)
        if not deployment_response['success']:
            logger.warning(f"Deployment start failed: {deployment_response['message']}")
        
        logger.info("Create request completed successfully")
        send_cfn_response(event, context, CFN_SUCCESS, 
                        {"Message": RESPONSE_MESSAGES["CREATE_SUCCESS"]})
        
    except Exception as e:
        logger.error(f"Create request failed: {str(e)}")
        send_cfn_response(event, context, CFN_SUCCESS, {"Error": str(e)})


def handle_update_request(event, context):
    """
    Handle CloudFormation Update request for Amplify app deployment.
    
    Updates existing deployment:
    1. Extract and deploy new frontend files
    2. Start deployment to existing Amplify app
    
    Args:
        event: CloudFormation event data
        context: Lambda context object
        
    Returns:
        None: Sends response directly to CloudFormation
    """
    logger.info("Starting Update request handling")
    
    try:
        # Stage 1: Extract and deploy new frontend files
        logger.info("Extracting updated frontend files from S3")
        extract_response = extract_and_deploy_s3_zip(FRONTEND_BUCKET_NAME, DEFAULT_ZIP_FILE)
        if not extract_response['success']:
            logger.error("Failed to extract S3 zip file")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": RESPONSE_MESSAGES["ZIP_EXTRACTION_ERROR"]})
            return
        
        # Stage 2: Get existing app ID from S3
        logger.info("Retrieving existing Amplify app ID from S3")
        app_id = retrieve_app_id_from_s3()
        if not app_id:
            logger.error("Cannot find existing Amplify app ID in S3")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": RESPONSE_MESSAGES["APP_ID_FILE_NOT_FOUND"]})
            return
        
        # Stage 3: Start deployment to existing app
        logger.info("Starting deployment to existing Amplify app")
        deployment_response = deploy_to_amplify(app_id, AMPLIFY_BRANCH_CONFIG['branchName'])
        if not deployment_response['success']:
            logger.warning(f"Deployment update failed: {deployment_response['message']}")
        
        logger.info("Update request completed successfully")
        send_cfn_response(event, context, CFN_SUCCESS, 
                        {"Message": RESPONSE_MESSAGES["UPDATE_SUCCESS"]})
        
    except Exception as e:
        logger.error(f"Update request failed: {str(e)}")
        send_cfn_response(event, context, CFN_SUCCESS, {"Error": str(e)})


def handle_delete_request(event, context):
    """
    Handle CloudFormation Delete request for Amplify app.
    
    Removes the Amplify app and all associated resources.
    
    Args:
        event: CloudFormation event data
        context: Lambda context object
        
    Returns:
        None: Sends response directly to CloudFormation
    """
    logger.info("Starting Delete request handling")
    
    try:
        # Get app ID from S3
        logger.info("Retrieving Amplify app ID from S3 for deletion")
        app_id = retrieve_app_id_from_s3()
        if not app_id:
            logger.warning("Amplify app ID not found in S3")
            send_cfn_response(event, context, CFN_SUCCESS, 
                            {"Message": RESPONSE_MESSAGES["APP_ID_FILE_NOT_FOUND"]})
            return
        
        # Delete the Amplify app
        logger.info(f"Deleting Amplify app with ID: {app_id}")
        deletion_response = delete_amplify_app(app_id)
        if not deletion_response['success']:
            logger.error(f"App deletion failed: {deletion_response['message']}")
        
        # Clean up app ID file from S3
        logger.info("Cleaning up app ID file from S3")
        cleanup_response = delete_app_id_file_from_s3()
        if not cleanup_response['success']:
            logger.warning(f"App ID file cleanup failed: {cleanup_response['message']}")
        
        logger.info("Delete request completed successfully")
        send_cfn_response(event, context, CFN_SUCCESS, 
                        {"Message": RESPONSE_MESSAGES["DELETE_SUCCESS"]})
        
    except Exception as e:
        logger.error(f"Delete request failed: {str(e)}")
        send_cfn_response(event, context, CFN_SUCCESS, {"Error": str(e)})


def create_amplify_app_and_branch():
    """
    Create Amplify app and production branch in sequence.
    
    Creates both the app and branch with predefined configurations,
    handling errors gracefully at each stage.
    
    Returns:
        dict: Response with success status, app_id, branch_name, and message
    """
    logger.info("Creating Amplify app")
    
    try:
        # Create Amplify app
        create_app_response = amplify.create_app(
            name=AMPLIFY_APP_NAME,
            customRules=AMPLIFY_CUSTOM_RULES,
            **AMPLIFY_APP_CONFIG
        )
        
        app_id = create_app_response.get("app", {}).get("appId")
        if not app_id:
            error_msg = "Amplify app creation failed, no appId returned"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        logger.info(f"Amplify app created successfully with ID: {app_id}")
        
        # Create production branch
        logger.info("Creating production branch")
        create_branch_response = amplify.create_branch(
            appId=app_id,
            **AMPLIFY_BRANCH_CONFIG
        )
        
        branch_name = create_branch_response.get("branch", {}).get("branchName")
        if not branch_name:
            error_msg = "Amplify branch creation failed, no branchName returned"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
        logger.info(f"Amplify branch created successfully: {branch_name}")
        
        return {
            "success": True,
            "app_id": app_id,
            "branch_name": branch_name,
            "message": "App and branch created successfully"
        }
        
    except Exception as e:
        error_msg = f"Error creating Amplify app or branch: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


def deploy_to_amplify(app_id, branch_name):
    """
    Start deployment to Amplify app from S3 source.
    
    Initiates deployment using the configured S3 bucket and folder.
    
    Args:
        app_id (str): Amplify application ID
        branch_name (str): Target branch name
        
    Returns:
        dict: Response with success status and message
    """
    logger.info(f"Starting deployment for app {app_id}, branch {branch_name}")
    
    try:
        source_url = f"s3://{FRONTEND_BUCKET_NAME}{FRONTEND_FOLDER_NAME}"
        logger.info(f"S3 source URL: {source_url}")
        
        response = amplify.start_deployment(
            appId=app_id,
            branchName=branch_name,
            sourceUrl=source_url,
            **AMPLIFY_DEPLOYMENT_CONFIG
        )
        
        job_id = response.get("jobSummary", {}).get("jobId")
        logger.info(f"Deployment started successfully with job ID: {job_id}")
        
        return {"success": True, "message": f"Deployment started with job ID: {job_id}"}
        
    except Exception as e:
        error_msg = f"Error starting deployment: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


def delete_amplify_app(app_id):
    """
    Delete Amplify app and all associated resources.
    
    Args:
        app_id (str): Amplify application ID to delete
        
    Returns:
        dict: Response with success status and message
    """
    logger.info(f"Deleting Amplify app with ID: {app_id}")
    
    try:
        response = amplify.delete_app(appId=app_id)
        logger.info("Amplify app deleted successfully")
        
        return {"success": True, "message": "Amplify app deleted successfully"}
        
    except Exception as e:
        error_msg = f"Error deleting Amplify app: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


def save_app_id_to_s3(app_id):
    """
    Save Amplify app ID to S3 for future reference.
    
    Stores the app ID in a text file in the frontend S3 bucket
    for retrieval during update and delete operations.
    
    Args:
        app_id (str): Amplify application ID to save
        
    Returns:
        dict: Response with success status and message
    """
    logger.info(f"Saving app ID {app_id} to S3")
    
    try:
        s3_client.put_object(
            Bucket=FRONTEND_BUCKET_NAME,
            Key=APP_ID_FILE_KEY,
            Body=app_id.encode('utf-8'),
            ContentType='text/plain'
        )
        
        logger.info(f"App ID saved successfully to s3://{FRONTEND_BUCKET_NAME}/{APP_ID_FILE_KEY}")
        return {"success": True, "message": "App ID saved to S3 successfully"}
        
    except Exception as e:
        error_msg = f"Error saving app ID to S3: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


def retrieve_app_id_from_s3():
    """
    Retrieve Amplify app ID from S3.
    
    Reads the app ID from the stored text file in the frontend S3 bucket.
    
    Returns:
        str: The app ID if found, None otherwise
    """
    logger.info(f"Retrieving app ID from S3: s3://{FRONTEND_BUCKET_NAME}/{APP_ID_FILE_KEY}")
    
    try:
        response = s3_client.get_object(
            Bucket=FRONTEND_BUCKET_NAME,
            Key=APP_ID_FILE_KEY
        )
        
        app_id = response['Body'].read().decode('utf-8').strip()
        logger.info(f"Successfully retrieved app ID: {app_id}")
        return app_id
        
    except s3_client.exceptions.NoSuchKey:
        logger.warning(f"App ID file not found at s3://{FRONTEND_BUCKET_NAME}/{APP_ID_FILE_KEY}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving app ID from S3: {str(e)}")
        return None


def delete_app_id_file_from_s3():
    """
    Delete the app ID file from S3 during cleanup.
    
    Removes the app ID file from the frontend S3 bucket
    after successful app deletion.
    
    Returns:
        dict: Response with success status and message
    """
    logger.info(f"Deleting app ID file from S3: s3://{FRONTEND_BUCKET_NAME}/{APP_ID_FILE_KEY}")
    
    try:
        s3_client.delete_object(
            Bucket=FRONTEND_BUCKET_NAME,
            Key=APP_ID_FILE_KEY
        )
        
        logger.info("App ID file deleted successfully from S3")
        return {"success": True, "message": "App ID file deleted from S3 successfully"}
        
    except Exception as e:
        error_msg = f"Error deleting app ID file from S3: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


def extract_and_deploy_s3_zip(bucket_name, zip_key):
    """
    Extract zip file from S3 and upload contents back to S3.
    
    Downloads zip file, extracts contents, cleans up old files,
    and uploads new files to the same S3 bucket.
    
    Args:
        bucket_name (str): S3 bucket name
        zip_key (str): S3 key of the zip file to extract
        
    Returns:
        dict: Response with success status, file count, and details
    """
    logger.info(f"Extracting zip file {zip_key} from bucket {bucket_name}")
    
    try:
        # Determine the base folder name from the zip key
        base_folder = os.path.splitext(os.path.basename(zip_key))[0]
        
        # Clean up existing files
        cleanup_response = cleanup_existing_files(bucket_name, base_folder)
        if cleanup_response['files_deleted'] > 0:
            logger.info(f"Cleaned up {cleanup_response['files_deleted']} existing files")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the zip file from S3
            zip_file_path = os.path.join(temp_dir, 'downloaded.zip')
            logger.info(f"Downloading {zip_key} from bucket {bucket_name}")
            s3_client.download_file(bucket_name, zip_key, zip_file_path)
            
            # Extract the zip file
            extract_dir = os.path.join(temp_dir, 'extracted')
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                logger.info(f"Extracted {len(zip_ref.namelist())} files")
            
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
                    logger.debug(f"Uploading {relative_path} to {s3_key}")
                    s3_client.upload_file(local_file_path, bucket_name, s3_key)
                    uploaded_files.append(s3_key)
            
            logger.info(f"Successfully uploaded {len(uploaded_files)} files")
            
            return {
                'success': True,
                'message': f"Successfully extracted and uploaded {len(uploaded_files)} files",
                'uploaded_files': uploaded_files,
                'base_folder': base_folder
            }
            
    except Exception as e:
        error_msg = f"Error extracting zip file: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'message': error_msg}


def cleanup_existing_files(bucket_name, base_folder):
    """
    Remove existing files from S3 folder before deploying new ones.
    
    Lists and deletes all objects with the specified prefix,
    handling pagination and batch deletion limits.
    
    Args:
        bucket_name (str): S3 bucket name
        base_folder (str): Folder prefix to clean up
        
    Returns:
        dict: Response with cleanup results and file count
    """
    logger.info(f"Cleaning up existing files in folder: {base_folder}")
    
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=f"{base_folder}/")
        
        objects_to_delete = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    objects_to_delete.append({'Key': obj['Key']})
        
        if objects_to_delete:
            logger.info(f"Found {len(objects_to_delete)} existing files to delete")
            
            # Delete objects in batches (S3 allows max 1000 objects per delete request)
            total_deleted = 0
            for i in range(0, len(objects_to_delete), S3_DELETE_BATCH_SIZE):
                batch = objects_to_delete[i:i + S3_DELETE_BATCH_SIZE]
                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch}
                )
                total_deleted += len(batch)
            
            logger.info(f"Successfully deleted {total_deleted} existing files")
            return {'success': True, 'files_deleted': total_deleted}
        else:
            logger.info("No existing files found to delete")
            return {'success': True, 'files_deleted': 0}
            
    except Exception as e:
        error_msg = f"Error cleaning up existing files: {str(e)}"
        logger.error(error_msg)
        return {'success': False, 'message': error_msg, 'files_deleted': 0}


def send_cfn_response(event, context, response_status, response_data, physical_resource_id=None, no_echo=False, reason=None):
    """
    Send response back to CloudFormation service.
    
    Constructs and sends the required response format for CloudFormation
    custom resources using the pre-signed URL from the event.
    
    Args:
        event: CloudFormation event data containing ResponseURL
        context: Lambda context object
        response_status (str): SUCCESS or FAILED
        response_data (dict): Custom data to return
        physical_resource_id (str, optional): Resource identifier
        no_echo (bool, optional): Whether to mask the response
        reason (str, optional): Custom reason for the response
    """
    logger.info(f"Sending CloudFormation response: {response_status}")
    
    try:
        response_url = event['ResponseURL']
        
        response_body = {
            'Status': response_status,
            'Reason': reason or f"See CloudWatch Log Stream: {context.log_stream_name}",
            'PhysicalResourceId': physical_resource_id or context.log_stream_name,
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'NoEcho': no_echo,
            'Data': response_data
        }
        
        json_response_body = json.dumps(response_body)
        logger.debug(f"Response body: {json_response_body}")
        
        headers = {
            'content-type': '',
            'content-length': str(len(json_response_body))
        }
        
        response = http.request('PUT', response_url, headers=headers, body=json_response_body)
        logger.info(f"CloudFormation response sent successfully: {response.status}")
        
    except Exception as e:
        logger.error(f"Failed to send CloudFormation response: {str(e)}")
        # Don't re-raise - we don't want the Lambda to fail if CFN response fails