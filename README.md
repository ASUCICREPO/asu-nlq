# ASU NLQ Deployment Guide

## Table of Contents
- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [EC2 Instance Setup](#ec2-instance-setup)
  - [Create EC2 Instance](#create-ec2-instance)
  - [Install Required Packages](#install-required-packages)
  - [Clone Repository](#clone-repository)
- [Data Dictionary Configuration](#data-dictionary-configuration)
  - [Setup Process](#setup-process)
- [Redshift Database Setup](#redshift-database-setup)
  - [Create Redshift Serverless](#create-redshift-serverless)
  - [Load Data into Redshift](#load-data-into-redshift)
- [Knowledge Base Configuration](#knowledge-base-configuration)
  - [General Setup](#general-setup)
  - [Add Data Dictionary](#add-data-dictionary)
  - [Grant Permissions](#grant-permissions)
- [Terraform Deployment](#terraform-deployment)
  - [Deploy Infrastructure](#deploy-infrastructure)
  - [Access Deployed Application](#access-deployed-application)
- [Stack Management](#stack-management)
  - [How to Delete the Stack](#how-to-delete-the-stack)
  - [How to Update Data Dictionary](#how-to-update-data-dictionary)

## Introduction

The ASU NLQ (Natural Language Query) application is a sophisticated data querying system that enables users to interact with structured databases using natural language queries. This deployment guide provides step-by-step instructions for setting up the complete infrastructure on AWS.

Key technical components include:
- EC2 instance for deployment management
- Amazon Redshift Serverless for data warehousing
- AWS Bedrock Knowledge Base for natural language processing
- Terraform for infrastructure as code
- AWS Amplify for frontend hosting

## Prerequisites

Before beginning deployment, ensure you have the following:

1. **AWS Account Access**
   - Valid AWS credentials with administrative permissions
   - Access to AWS Console

2. **Data Requirements**
   - CSV formatted data files (under 100MB per file)
   - Complete understanding of data schema and relationships

3. **Network Configuration**
   - Default VPC available in your AWS region
   - If default VPC doesn't exist, create using: [AWS VPC Documentation](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-default-vpc.html)

## EC2 Instance Setup

### Create EC2 Instance

1. **Navigate to EC2 Console**
   - Log into your AWS Console
   - Search for "EC2" in the services search bar
   - Click on "EC2" under Services

2. **Launch Instance**
   - Click "Launch Instance" button
   - Follow standard deployment documentation instructions
   - Use default VPC configuration
   - Wait for instance to reach "running" state

3. **Connect to Instance**
   - Navigate to the Instances page
   - Select your created instance
   - Click "Connect"
   - Use connection details: Public IP, username: `ec2-user`

> **Note**: Save your instance details for future management operations.

### Install Required Packages

Execute the following commands in your EC2 terminal:

> **Note**: When password prompts appear, press Enter. Use Ctrl+Shift+V for terminal paste operations.

1. **Install Git**
   ```bash
   sudo yum install -y git
   ```

2. **Install Yum Utilities**
   ```bash
   sudo yum install -y yum-utils
   ```

3. **Add HashiCorp Repository**
   ```bash
   sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo
   ```

4. **Install Terraform**
   ```bash
   sudo yum install -y terraform
   ```

5. **Verify Installations**
   ```bash
   git --version
   terraform version
   node --version
   npm --version
   ```

### Clone Repository

```bash
git clone https://github.com/ASUCICREPO/asu-nlq
```

## Data Dictionary Configuration

### Setup Process

1. **Navigate to Utilities Directory**
   ```bash
   cd asu-nlq/Utilities
   ```

2. **Run Schema Manager**
   ```bash
   python3 schema_manager.py
   ```

3. **Configure Data Schema**
   - Use `--print` flag to view current state
   - Use `--edit` flag to make modifications
   - Follow interactive prompts to enter all required information
   - Document all table names, column names, and descriptions

> **Important**: Ensure all attribute names are entered exactly as they appear in your data files. The system requires exact matches to function properly.

## Redshift Database Setup

### Create Redshift Serverless

1. **Access Redshift Console**
   - Navigate to AWS Redshift service in the console
   - Select "Redshift Serverless" from the menu

2. **Create Workgroup**
   - Click "Create new workgroup"
   - Enter a descriptive name for the workgroup
   - Set base capacity: `4`
   - Set max capacity: `4`
   - Select default VPC for network and security
   - Choose default security group
   - Select all four default subnets
   - Click "Next" to proceed

3. **Create Namespace**
   - Enter a descriptive name for the namespace
   - Under permissions, choose "Create new IAM role"
   - Keep default settings
   - Click "Create" to finalize setup

> **Note**: Record the workgroup and namespace names for later configuration steps.

### Load Data into Redshift

1. **Access Query Editor**
   - From the Redshift console left menu, select "Query editor V2"
   - Connect to your created database (typically named "dev")

2. **Upload Data Files**
   - Select "Load data" option
   - Choose "From local file"
   - Ensure files are in CSV format

3. **Configure Table Creation**
   - Select "Load new table" in the menu
   - Choose "public" for the schema
   - Enter table name from your data dictionary document
   - Click "Create table and load data"

> **Important**: This process assumes data files are under 100MB. For larger files, use S3 bucket upload method. Data loading may take several minutes to complete.

## Knowledge Base Configuration

### General Setup

1. **Access Bedrock Console**
   - Navigate to AWS Bedrock service
   - In the left menu under "Build", select "Knowledge bases"
   - Click "Create with structured data store"

2. **Configure Basic Settings**
   - Enter a descriptive name and description
   - Click "Next"
   - Select the workgroup created in previous steps
   - Select the "dev" database (or your custom database name)

### Add Data Dictionary

1. **Configure Table Descriptions**
   - Under "Query configuration", locate "Table and column descriptions"
   - Load each description from your earlier data dictionary setup
   - Use format: `dev.public.table_name` for table names

2. **Add Attribute Descriptions**
   - For whole table description: Enter without any attribute name
   - For each attribute: Provide exact attribute name and description
   - Reference your data dictionary document for accurate information

> **Critical**: Attribute names must be entered exactly as they appear in your database. Any discrepancy will cause system failure.

3. **Complete Knowledge Base Creation**
   - Wait for knowledge base creation to complete
   - Copy the IAM role from the info link immediately
   - Format example: `IAMR:AmazonBedrockExecutionRoleForKnowledgeBase_3r2xd`
   - Save the knowledge base ID for future use

### Grant Permissions

1. **Return to Query Editor**
   - Navigate back to Redshift Query editor V2
   - Connect to your database

2. **Execute Permission Commands**
   Replace `${service-role}` with your copied IAM role and `${schemaName}` with "public":

   ```sql
   CREATE USER "IAMR:${service-role}" WITH PASSWORD DISABLE;
   GRANT SELECT ON ALL TABLES IN SCHEMA ${schemaName} TO "IAMR:${serviceRole}";
   GRANT USAGE ON SCHEMA ${schemaName} TO "IAMR:${serviceRole}";
   ```

3. **Sync Knowledge Base**
   - Return to Bedrock Knowledge bases menu
   - Select your knowledge base
   - Under "Query engine", click "Sync" to sync data
   - Wait for synchronization to complete

> **Reference**: For detailed information, see [AWS Bedrock Knowledge Base Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html)

## Terraform Deployment

### Deploy Infrastructure

1. **Navigate to Terraform Directory**
   ```bash
   cd ..
   cd asu-nlq-terraform
   ```

2. **Configure Knowledge Base**
   ```bash
   python3 setup.py
   ```
   - Enter the knowledge base ID when prompted

3. **Set AWS Credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=""
   export AWS_SECRET_ACCESS_KEY=""
   export AWS_SESSION_TOKEN=""
   ```

4. **Initialize and Deploy**
   ```bash
   terraform init
   terraform apply
   ```
   - Type `yes` when prompted to confirm deployment
   - Wait for deployment completion (several minutes)

5. **Complete Deployment**
   - Exit the EC2 instance
   - Stop the instance through AWS Console (do not terminate)

> **Important**: Keep the EC2 instance for future deployment management, updates, and deletion operations.

### Access Deployed Application

- Navigate to AWS Amplify service in the console
- Locate your deployed application
- Access the provided website link

## Stack Management

### How to Delete the Stack

1. **Start EC2 Instance**
   - Restart the same EC2 instance used for deployment

2. **Navigate to Terraform Directory**
   ```bash
   cd asu-nlq/asu-nlq-terraform
   ```

3. **Set AWS Credentials**
   ```bash
   export AWS_ACCESS_KEY_ID=""
   export AWS_SECRET_ACCESS_KEY=""
   export AWS_SESSION_TOKEN=""
   ```

4. **Destroy Infrastructure**
   ```bash
   terraform destroy
   ```

> **Note**: Knowledge base and Redshift database must be manually deleted as they are not managed by the Terraform stack. Amplify is managed automatically and does not require manual deletion.

### How to Update Data Dictionary

1. **Start EC2 Instance**
   - Restart the EC2 instance
   - Navigate to the Utilities folder

2. **Update Schema**
   ```bash
   python3 schema_manager.py --edit
   ```
   - Use the interactive program to add/modify database schema and values

3. **Redeploy Infrastructure**
   ```bash
   cd ../asu-nlq-terraform
   ```
   - Export AWS credentials again
   - Run `terraform apply`

4. **Update Database**
   - Navigate to Redshift Query editor V2
   - Clear existing data
   - Upload new CSV data with your modifications

5. **Update Knowledge Base**
   - Navigate to your knowledge base in Bedrock console
   - Click "Edit"
   - Under query configuration, add/remove attributes according to changes
   - Use `schema_manager.py --print` to view required changes
   - Sync the knowledge base to apply updates

⚠️ **Important**: Always ensure data consistency between your CSV files, Redshift database, and Knowledge Base configuration to maintain system functionality.