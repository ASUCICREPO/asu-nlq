####################################################################################################
# Perform zipping of all the lambda files as needed
####################################################################################################

data "aws_caller_identity" "current" {}

data "archive_file" "amplify_deployment_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/amplify_deployment_lambda/"
  output_path = "${path.module}/../../lambdas/zips/amplify_deployment_lambda.zip"
}

####################################################################################################
# This section defines the S3 bucket for storing the frontend files
####################################################################################################
# Defines the S3 bucket for storing database descriptions and schemas
resource "aws_s3_bucket" "asu_nlq_frontend_store_bucket" {
  bucket        = "asu-nlq-frontend-store-bucket-${var.random_suffix}"
  force_destroy = true
}

resource "aws_s3_bucket_policy" "asu_nlq_frontend_store_bucket_policy" {
  bucket = aws_s3_bucket.asu_nlq_frontend_store_bucket.id
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "VisualEditor0",
        "Effect": "Allow",
        "Principal": {
          "AWS": "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        "Action": [
          "s3:GetObjectAcl",
          "s3:PutObjectVersionAcl",
          "s3:PutObjectAcl"
        ],
        "Resource": [
          "${aws_s3_bucket.asu_nlq_frontend_store_bucket.arn}",
          "${aws_s3_bucket.asu_nlq_frontend_store_bucket.arn}/*"
        ]
      }
    ]
  })
}

# Upload the frontend file zip to S3
resource "aws_s3_object" "asu_nlq_frontend_store_upload" {
  bucket       = aws_s3_bucket.asu_nlq_frontend_store_bucket.id
  key          = "build.zip"
  source       = var.frontend_build_zip_path
  depends_on   = [aws_s3_bucket.asu_nlq_frontend_store_bucket, aws_s3_bucket_policy.asu_nlq_frontend_store_bucket_policy]
  content_type = "application/zip"
}

####################################################################################################
# This section defines the Lambda used to manage the amplify deployment
####################################################################################################

# IAM Role for Lambda
resource "aws_iam_role" "asu_nlq_chatbot_lambda_exec_role" {
  name = "asu-nlq-chatbot-lambda-exec-role-${var.random_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda to access S3
resource "aws_iam_role_policy" "asu_nlq_chatbot_lambda_s3_access" {
  name = "asu-nlq-chatbot-lambda-s3-access-${var.random_suffix}"
  role = aws_iam_role.asu_nlq_chatbot_lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.asu_nlq_frontend_store_bucket.arn,
          "${aws_s3_bucket.asu_nlq_frontend_store_bucket.arn}/*"
        ]
      }
    ]
  })
}

# IAM Policy for Lambda to access Amplify, create and manage apps
resource "aws_iam_role_policy" "asu_nlq_chatbot_lambda_amplify_access" {
  name = "asu-nlq-chatbot-lambda-amplify-access-${var.random_suffix}"
  role = aws_iam_role.asu_nlq_chatbot_lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "amplify:CreateApp",
          "amplify:UpdateApp",
          "amplify:CreateBranch",
          "amplify:UpdateBranch",
          "amplify:GetApp",
          "amplify:GetBranch",
          "amplify:ListApps",
          "amplify:ListBranches",
          "amplify:StartDeployment",
          
        ]
        Resource = "*"
      }
    ]
  })
}


# CloudWatch Logs policy for Lambda # TODO - can standardize role attachement strategy accross the two lambdas?
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_lambda_logs" {
  role       = aws_iam_role.asu_nlq_chatbot_lambda_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function
resource "aws_lambda_function" "asu_nlq_amplify_deployment_lambda" {
  function_name    = "asu_nlq_amplify_deployment_lambda-${var.random_suffix}"
  role             = aws_iam_role.asu_nlq_chatbot_lambda_exec_role.arn

  handler          = "lambda_function.lambda_handler"
  filename         = data.archive_file.amplify_deployment_lambda_zip.output_path
  source_code_hash = data.archive_file.amplify_deployment_lambda_zip.output_base64sha256
  
  runtime          = "python3.13"
  timeout          = 60  # Set the maximum runtime to 60 seconds

  environment {
    variables = {
      FRONTEND_BUCKET_NAME    = aws_s3_bucket.asu_nlq_frontend_store_bucket.id
      FRONTEND_ZIP_NAME       = "build.zip"
      AMPLIFY_APP_NAME        = "ASU_NLQ_Chatbot_App-${var.random_suffix}"
    }
  }

}

resource "aws_cloudformation_stack" "asu_nlq_chatbot_custom_resource" {
  name = "asu-nlq-chatbot-custom-resource-stack-${var.random_suffix}"
  
  template_body = jsonencode({
    AWSTemplateFormatVersion = "2010-09-09"
    Description = "Custom Resource for ASU NLQ Chatbot Amplify Deployment Lambda Invocation"
    
    Resources = {
      CustomResource = {
        Type = "Custom::LambdaResource"
        Properties = {
          ServiceToken = aws_lambda_function.asu_nlq_amplify_deployment_lambda.arn
          ServiceTimeout = 60
        }
      }
    }
  })

  depends_on = [
    aws_lambda_function.asu_nlq_amplify_deployment_lambda, 
    aws_s3_object.asu_nlq_frontend_store_upload,
    aws_iam_role_policy.asu_nlq_chatbot_lambda_s3_access,
    aws_iam_role_policy.asu_nlq_chatbot_lambda_amplify_access,
  ]
}

