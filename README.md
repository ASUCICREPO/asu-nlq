# ASU NLQ Project

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [AWS Console Setup](#aws-console-setup)
  - [Configure Bedrock Model Access](#configure-bedrock-model-access)
  - [Create S3 Bucket for Knowledge Base](#create-s3-bucket-for-knowledge-base)
  - [Configure IAM User for Terraform](#configure-iam-user-for-terraform)
- [Terraform Configuration](#terraform-configuration)
  - [Configure Terraform Variables](#configure-terraform-variables)
  - [Initialize Terraform](#initialize-terraform)
  - [Plan Deployment](#plan-deployment)
  - [Deploy Infrastructure](#deploy-infrastructure)
- [Knowledge Base Setup](#knowledge-base-setup)
  - [Upload Documents](#upload-documents)
  - [Sync Knowledge Base](#sync-knowledge-base)
- [Application Configuration](#application-configuration)
  - [Update Environment Variables](#update-environment-variables)
  - [Deploy Application](#deploy-application)
- [Testing and Validation](#testing-and-validation)
  - [Verify Knowledge Base](#verify-knowledge-base)
  - [Test Application](#test-application)
- [Maintenance](#maintenance)
  - [Update Documents](#update-documents)
  - [Monitor Performance](#monitor-performance)
  - [Destroy Infrastructure](#destroy-infrastructure)

## Introduction
The ASU NLQ (Natural Language Query) Project is an intelligent question-answering system developed for the Cloud Innovation Center (CIC), a collaborative partnership between AWS and Arizona State University. This application leverages AWS Bedrock's knowledge base capabilities to provide accurate, context-aware responses to natural language queries by converting them into SQL queries against structured data.

The system employs advanced AI technology to process natural language questions and translate them into SQL queries that can be executed against a Redshift database. Using AWS services and generative AI models, it creates a comprehensive data querying interface that understands complex natural language and generates appropriate SQL statements.

Key technical features include:
- **Terraform Infrastructure as Code** for reproducible deployments
- **AWS Bedrock Knowledge Base** for document processing and retrieval
- **Amazon Redshift Serverless** for SQL-based data storage and querying
- **AWS Nova Pro models** for advanced AI processing and natural language understanding
- **AWS Lambda** functions for serverless processing
- **Amazon S3** for document storage and management

## Prerequisites
Before beginning deployment, ensure you have the following tools installed and configured on your system:

1. **Terraform**
   - Download and install from [https://www.terraform.io/downloads]()
   - Verify installation:
   ```bash
   terraform --version
   ```
   - Required version: 1.5.0 or later

2. **AWS CLI**
   - Download and install from [https://aws.amazon.com/cli/]()
   - Verify installation:
   ```bash
   aws --version
   ```
   - Configure with credentials:
   ```bash
   aws configure
   ```

3. **Git**
   - Download and install from [https://git-scm.com/]()
   - Verify installation:
   ```bash
   git --version
   ```

4. **Python and pip** (for document processing scripts)
   - Download and install from [https://www.python.org/]()
   - Verify installation:
   ```bash
   python --version
   pip --version
   ```

5. **Clone the repository**
   ```bash
   git clone https://github.com/ASUCICREPO/asu-nlq
   cd asu-nlq
   ```

⚠️ **Important**: Ensure you have appropriate AWS permissions to create Bedrock, OpenSearch, S3, Lambda, and IAM resources before proceeding.

## AWS Console Setup

### Configure Bedrock Model Access

1. **Navigate to Amazon Bedrock Console**
   - Log into your AWS Console
   - Search for "Bedrock" in the services search bar
   - Click on "Amazon Bedrock" under Services

2. **Request Model Access**
   - In the left navigation panel, click "Model access"
   - Click "Request model access" in the top right corner
   - Select the following models for this project:
     - **Amazon Nova Pro** (for natural language to SQL translation)
     - **Amazon Nova Canvas** (for multi-modal capabilities)
     - **Amazon Titan Text Embeddings v2** (for semantic understanding)
   - For each model:
     - Click "Request model access"
     - Review and accept the End User License Agreement
     - Click "Submit"

3. **Verify Model Access**
   - Wait for model access approval (typically 5-15 minutes)
   - Refresh the page and ensure all requested models show "Access granted"
   
> **Note**: Model access is required before deploying the Terraform infrastructure. The deployment will fail if models are not accessible.

⚠️ **Important**: Model access approval is account-specific and may take up to 24 hours in some cases. Plan accordingly for your deployment timeline.

### Create S3 Bucket for Knowledge Base

1. **Navigate to S3 Console**
   - Log into your AWS Console
   - Search for "S3" in the services search bar
   - Click on "S3" under Services

2. **Create Knowledge Base Bucket**
   - Click the "Create bucket" button in the top right corner
   - Configure bucket settings:
     - Bucket name: `asu-nlq-knowledge-base-{unique-suffix}` (e.g., `asu-nlq-knowledge-base-demo-2024`)
     - Region: Choose your preferred region (recommend `us-east-1` or `us-west-2`)
     - Keep all other settings at their defaults
   - Click "Create bucket"

3. **Create Document Structure**
   - Navigate into your newly created bucket
   - Create the following folder structure for schema and data files:
     ```
     schemas/
     ├── database_schema.sql
     ├── table_definitions/
     └── sample_queries/
     ```
   - Click "Create folder" for each directory

> **Note**: Save your bucket name and region, as these will be needed for Terraform variable configuration. This bucket will store database schemas and documentation for the NLQ system.

### Configure IAM User for Terraform

1. **Navigate to IAM Console**
   - Log into your AWS Console
   - Search for "IAM" in the services search bar
   - Click on "IAM" under Services

2. **Create Terraform User**
   - Click "Users" in the left navigation panel
   - Click "Create user"
   - Configure user details:
     - User name: `terraform-asu-nlq`
     - AWS access type: Select "Programmatic access"
   - Click "Next: Permissions"

3. **Attach Policies**
   - Select "Attach existing policies directly"
   - Search for and attach the following AWS managed policies:
     - `AmazonBedrockFullAccess`
     - `AmazonRedshiftFullAccess`
     - `AmazonS3FullAccess`
     - `IAMFullAccess`
     - `AWSLambdaFullAccess`
   - Click "Next: Tags" (skip tags)
   - Click "Next: Review"
   - Click "Create user"

4. **Save Credentials**
   - Copy and securely store the Access Key ID and Secret Access Key
   - Configure these credentials in your AWS CLI:
   ```bash
   aws configure --profile terraform-asu-nlq
   ```

⚠️ **Important**: Store these credentials securely and never commit them to version control. Consider using AWS credential profiles for better security management.

## Terraform Configuration

### Configure Terraform Variables

1. **Navigate to Terraform Directory**
   ```bash
   cd terraform/
   ```

2. **Create Variables File**
   - Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```
   - Open `terraform.tfvars` in your preferred editor

3. **Configure Required Variables**
   - Update the following variables with your specific values:
   ```hcl
   # AWS Configuration
   aws_region = "us-east-1"  # Your chosen AWS region
   aws_profile = "terraform-asu-nlq"  # Your AWS CLI profile name
   
   # Project Configuration
   project_name = "asu-nlq"
   environment = "production"  # or "development", "staging"
   
   # S3 Configuration
   knowledge_base_bucket_name = "asu-nlq-knowledge-base-demo-2024"  # Your bucket name
   
   # Bedrock Configuration
   embedding_model_id = "amazon.titan-embed-text-v2:0"
   foundation_model_id = "amazon.nova-pro-v1:0"
   
   # Redshift Configuration
   redshift_cluster_name = "asu-nlq-cluster"
   redshift_database_name = "asu_nlq_db"
   redshift_username = "admin"
   
   # Knowledge Base Configuration
   knowledge_base_name = "ASU-NLQ-KnowledgeBase"
   knowledge_base_description = "Knowledge base for ASU NLQ natural language to SQL query system"
   
   # Application Configuration
   api_name = "asu-nlq-api"
   lambda_timeout = 300  # 5 minutes
   lambda_memory = 1024  # MB
   ```

4. **Validate Variables**
   - Ensure all bucket names and model IDs match your AWS configuration
   - Verify region consistency across all resources
   - Confirm model access has been granted for specified Nova Pro model IDs

> **Note**: The `terraform.tfvars` file should not be committed to version control as it may contain sensitive information.

### Initialize Terraform

1. **Initialize Terraform Backend**
   ```bash
   terraform init
   ```
   - This command will:
     - Download required provider plugins (AWS, Redshift)
     - Initialize the local backend configuration
     - Create the `.terraform` directory

2. **Verify Initialization**
   - Ensure no errors occurred during initialization
   - Check that all required providers (AWS, Redshift) are downloaded
   - Verify local state configuration

> **Note**: This project uses local Terraform state management. The `terraform.tfstate` file will be created in your project directory and should be handled carefully.

### Plan Deployment

1. **Review Deployment Plan**
   ```bash
   terraform plan
   ```
   - This command will:
     - Validate your configuration
     - Show all resources that will be created
     - Identify any configuration errors

2. **Analyze Plan Output**
   - Review the planned resources (typically 15-25 resources)
   - Verify IAM roles and policies are correctly configured
   - Confirm S3 bucket and Redshift cluster settings
   - Check Lambda function configurations

3. **Save Plan (Optional)**
   ```bash
   terraform plan -out=deployment.tfplan
   ```

⚠️ **Important**: Carefully review the plan output before proceeding to deployment. Pay special attention to IAM policies and resource naming conventions.

### Deploy Infrastructure

1. **Apply Terraform Configuration**
   ```bash
   terraform apply
   ```
   - Review the plan one final time
   - Type `yes` when prompted to confirm deployment
   - Deployment typically takes 8-12 minutes

2. **Monitor Deployment Progress**
   - Watch for any error messages during deployment
   - Note the order of resource creation
   - Be patient with Redshift cluster creation (longest step)

3. **Verify Deployment Completion**
   ```bash
   terraform output
   ```
   - Save the output values for application configuration:
     - Knowledge Base ID
     - Redshift Cluster Endpoint
     - Lambda Function ARNs
     - S3 Bucket Names

> **Note**: Redshift Serverless cluster creation can take 5-10 minutes. The deployment will wait for completion before proceeding.

⚠️ **Important**: If deployment fails, review error messages carefully. Common issues include insufficient IAM permissions or Nova Pro model access not being granted.

## Knowledge Base Setup

### Upload Schema Documentation

1. **Prepare Schema Files**
   - Ensure all database schema files are properly formatted:
     - SQL schema files (.sql)
     - Table documentation (.md or .txt)
     - Sample query files (.sql)
     - Data dictionary files (.csv or .txt)
   - Organize files by database schema or functional area

2. **Upload to S3 Bucket**
   - Navigate to your knowledge base S3 bucket in the AWS Console
   - Upload schema documentation to appropriate folders:
   ```bash
   # Using AWS CLI
   aws s3 cp ./schemas/ s3://your-bucket-name/schemas/ --recursive
   ```
   - Or use the AWS Console drag-and-drop interface

3. **Verify Upload**
   - Confirm all schema files are successfully uploaded
   - Check file formats and organization
   - Ensure proper folder structure is maintained

### Sync Knowledge Base

1. **Navigate to Bedrock Console**
   - Go to Amazon Bedrock in AWS Console
   - Click "Knowledge bases" in the left navigation panel
   - Find your knowledge base (should match the name from terraform.tfvars)

2. **Initiate Sync**
   - Click on your knowledge base name
   - Navigate to the "Data source" tab
   - Click "Sync" in the top right corner
   - Confirm the sync operation

3. **Monitor Sync Progress**
   - Watch the sync status in the console
   - Sync typically takes 3-8 minutes depending on schema complexity
   - Status will change from "Syncing" to "Ready" when complete

⚠️ **Important**: The knowledge base must be synced before the application can understand your database schema and generate appropriate SQL queries. Re-sync whenever you update schema documentation.

## Application Configuration

### Update Environment Variables

1. **Retrieve Terraform Outputs**
   ```bash
   cd terraform/
   terraform output -json > ../outputs.json
   ```

2. **Configure Application**
   - Navigate to the application directory:
   ```bash
   cd ../application/
   ```
   - Create or update the environment file:
   ```bash
   cp .env.example .env
   ```

3. **Update Environment Variables**
   - Open `.env` and configure the following:
   ```env
   # AWS Configuration
   AWS_REGION=us-east-1
   AWS_PROFILE=terraform-asu-nlq
   
   # Bedrock Configuration
   KNOWLEDGE_BASE_ID=XXXXXXXXXX  # From terraform output
   FOUNDATION_MODEL_ID=amazon.nova-pro-v1:0
   
   # Redshift Configuration
   REDSHIFT_CLUSTER_ENDPOINT=asu-nlq-cluster.xxxxxxxxxx.us-east-1.redshift-serverless.amazonaws.com:5439/asu_nlq_db  # From terraform output
   REDSHIFT_DATABASE_NAME=asu_nlq_db
   REDSHIFT_USERNAME=admin
   
   # API Configuration
   API_GATEWAY_URL=https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod  # From terraform output
   LAMBDA_FUNCTION_NAME=asu-nlq-query-handler  # From terraform output
   
   # Application Settings
   MAX_TOKENS=4000
   TEMPERATURE=0.1
   TOP_P=0.9
   ```

### Deploy Application

1. **Install Dependencies**
   ```bash
   npm install
   # or
   pip install -r requirements.txt
   ```

2. **Build Application**
   ```bash
   npm run build
   # or for Python applications
   python setup.py build
   ```

3. **Deploy to Lambda** (if applicable)
   ```bash
   # Create deployment package
   zip -r deployment.zip .
   
   # Update Lambda function
   aws lambda update-function-code \
     --function-name asu-nlq-query-handler \
     --zip-file fileb://deployment.zip
   ```

## Testing and Validation

### Verify Knowledge Base

1. **Test Knowledge Base Query**
   - Navigate to Bedrock Console
   - Go to your knowledge base
   - Click "Test knowledge base" tab
   - Enter a test query related to your database schema (e.g., "What tables contain customer information?")
   - Verify relevant schema information is returned

2. **Check Schema Processing**
   - Ensure all uploaded schema files appear in the data source
   - Verify schema documentation is properly indexed
   - Test queries about table relationships and column definitions

### Test Application

1. **Unit Tests**
   ```bash
   # Run application tests
   npm test
   # or
   python -m pytest tests/
   ```

2. **Integration Tests**
   - Test API endpoints
   - Verify Lambda function responses
   - Check error handling and edge cases

3. **End-to-End Testing**
   - Submit various natural language queries through the application
   - Verify generated SQL queries are syntactically correct
   - Test query execution against the Redshift database
   - Validate returned results match expected data

⚠️ **Important**: Always test with a variety of natural language queries to ensure the system properly understands your database schema and generates valid SQL statements.

## Maintenance

### Update Documents

1. **Add New Schema Files**
   - Upload new database schema documentation to the appropriate S3 folders
   - Ensure proper naming conventions and file formats
   - Trigger knowledge base sync after upload

2. **Modify Existing Schema Documentation**
   - Replace schema files in S3 bucket when database structure changes
   - Re-sync knowledge base to update schema understanding
   - Test natural language queries to verify updates are reflected

3. **Remove Schema Files**
   - Delete outdated schema documentation from S3 bucket
   - Sync knowledge base to remove from index
   - Update any hardcoded references in application code

### Monitor Performance

1. **CloudWatch Monitoring**
   - Monitor Lambda function metrics:
     - Duration
     - Error rate
     - Invocation count
   - Set up alarms for unusual patterns

2. **Cost Optimization**
   - Review Bedrock Nova Pro model usage
   - Monitor Redshift Serverless compute costs
   - Optimize Lambda memory allocation based on usage

3. **Knowledge Base Analytics**
   - Track natural language query patterns and popular database questions
   - Identify gaps in schema documentation
   - Optimize SQL generation based on query success rates
   - Monitor frequently accessed tables and columns

### Destroy Infrastructure

1. **Backup Important Data**
   - Export any custom configurations
   - Save important documents from S3
   - Document any customizations made

2. **Clean Up Resources**
   ```bash
   cd terraform/
   terraform destroy
   ```
   - Type `yes` when prompted to confirm destruction
   - Monitor progress to ensure all resources are removed

3. **Verify Cleanup**
   - Check AWS Console to confirm resource deletion
   - Verify no unexpected charges remain
   - Remove any manually created resources not managed by Terraform

⚠️ **Important**: The destroy operation will permanently delete all resources and data. Ensure you have backups of any important information before proceeding.

⚠️ **Important**: The local `terraform.tfstate` file will be updated to reflect the destroyed infrastructure. Keep this file until you're certain all resources are properly cleaned up.

> **Note**: Some resources like S3 buckets with content may require manual cleanup before Terraform can destroy them. Empty buckets before running `terraform destroy`.
