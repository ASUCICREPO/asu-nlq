####################################################################################################
# Perform zipping of all the lambda files as needed
####################################################################################################

data "archive_file" "orchestration_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../lambdas/orchestration_lambda/"
  output_path = "${path.module}/../../lambdas/zips/orchestration_lambda.zip"
}


####################################################################################################
# This section defines the S3 bucket for storing database descriptions and database files
####################################################################################################

#Defines the S3 bucket for storing database descriptions and schemas
resource "aws_s3_bucket" "asu_nlq_chatbot_database_descriptions_bucket" {
  bucket = "asu-nlq-chatbot-database-descriptions-${var.random_suffix}"
  force_destroy = true
}

# Upload the description database file to S3
resource "aws_s3_object" "asu_nlq_chatbot_database_descriptions_upload" {
  bucket = aws_s3_bucket.asu_nlq_chatbot_database_descriptions_bucket.id
  key    = "${var.template_name}.json"
  source = "${path.root}/S3/${var.template_name}.json"
  etag   = filemd5("${path.root}/S3/${var.template_name}.json")

  depends_on = [aws_s3_bucket.asu_nlq_chatbot_database_descriptions_bucket]

  content_type = "application/json"
}

# Upload the database file to S3
resource "aws_s3_object" "asu_nlq_chatbot_database_upload" {
  bucket = aws_s3_bucket.asu_nlq_chatbot_database_descriptions_bucket.id
  key    = "${var.database_name}.db"
  source = "${path.root}/S3/${var.database_name}.db"
  etag   = filemd5("${path.root}/S3/${var.database_name}.db")

  depends_on = [aws_s3_bucket.asu_nlq_chatbot_database_descriptions_bucket]

  content_type = "application/vnd.sqlite3"
}


####################################################################################################
#This section defines the IAM policies and roles for the lambda functions
####################################################################################################

#Defines the basic execution policy for lambda functions
resource "aws_iam_policy" "asu_nlq_chatbot_lambda_basic_execution" {
  name        = "asu_nlq_chatbot_lambda_basic_execution_policy_${var.random_suffix}"
  description = "ASU NLQ Chatbot Lambda basic execution policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
  })
}

#Defines the bedrock access policy for lambda functions
resource "aws_iam_policy" "asu_nlq_chatbot_lambda_bedrock_access" {
  name        = "asu_nlq_chatbot_lambda_bedrock_access_policy_${var.random_suffix}"
  description = "ASU NLQ Chatbot Lambda bedrock access policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "BedrockAll",
            "Effect": "Allow",
            "Action": [
                "bedrock:*"
            ],
            "Resource": "*"
        },
        {
            "Sid": "DescribeKey",
            "Effect": "Allow",
            "Action": [
                "kms:DescribeKey"
            ],
            "Resource": "arn:*:kms:*:::*"
        },
        {
            "Sid": "APIsWithAllResourceAccess",
            "Effect": "Allow",
            "Action": [
                "iam:ListRoles",
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets",
                "ec2:DescribeSecurityGroups"
            ],
            "Resource": "*"
        },
        {
            "Sid": "PassRoleToBedrock",
            "Effect": "Allow",
            "Action": [
                "iam:PassRole"
            ],
            "Resource": "arn:aws:iam::*:role/*AmazonBedrock*",
            "Condition": {
                "StringEquals": {
                    "iam:PassedToService": [
                        "bedrock.amazonaws.com"
                    ]
                }
            }
        }
    ]
  })
}

#Defines the S3 access policy for lambda functions
resource "aws_iam_policy" "asu_nlq_chatbot_lambda_S3_access" {
  name        = "asu_nlq_chatbot_lambda_S3_access_policy_${var.random_suffix}"
  description = "ASU NLQ Chatbot lambda S3 access policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "s3-object-lambda:*"
            ],
            "Resource": "*"
        }
    ]
  })
}

#Defines the Api gateway access policy for lambda functions
resource "aws_iam_policy" "asu_nlq_chatbot_lambda_api_gateway_access" {
  name        = "asu_nlq_chatbot_lambda_api_gateway_access_policy_${var.random_suffix}"
  description = "ASU NLQ Chatbot lambda api gateway access policy"

  policy = jsonencode({
    "Statement": [
        {
            "Action": [
                "execute-api:Invoke",
                "execute-api:ManageConnections"
            ],
            "Effect": "Allow",
            "Resource": "arn:aws:execute-api:*:*:*"
        }
    ],
    "Version": "2012-10-17"
})
}

#Defines the lambda function execution access policy for lambda functions
resource "aws_iam_policy" "asu_nlq_chatbot_lambda_function_execution_access" {
  name        = "asu_nlq_chatbot_lambda_function_execution_access_policy_${var.random_suffix}"
  description = "ASU NLQ Chatbot lambda function execution access policy"

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "lambda:InvokeFunction",
            "Resource": [
                "${aws_lambda_function.asu_nlq_chatbot_orchestration_lambda.arn}",
                "${aws_lambda_function.asu_nlq_chatbot_orchestration_lambda.arn}:*"
            ],
            "Effect": "Allow"
        }
    ]
  })
}


####################################################################################################
#Defines the IAM roles, and attaches their policies, for the lambda functions
####################################################################################################

#Defines the IAM role for the orchestration_lambda function
resource "aws_iam_role" "asu_nlq_chatbot_orchestration_lambda_role" {
  name = "asu_nlq_chatbot_orchestration_lambda_role_${var.random_suffix}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com",
        },
      },
    ],
  })
}
# Attach the basic execution policy to the role
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_orchestration_lambda_basic_execution_policy_attachment" {
  role       = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.name
  policy_arn = aws_iam_policy.asu_nlq_chatbot_lambda_basic_execution.arn
}
# Attach the bedrock access policy to the role
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_orchestration_lambda_bedrock_access_policy_attachment" {
  role       = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.name
  policy_arn = aws_iam_policy.asu_nlq_chatbot_lambda_bedrock_access.arn
}
# Attach the S3 access policy to the role
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_orchestration_lambda_S3_access_policy_attachment" {
  role       = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.name
  policy_arn = aws_iam_policy.asu_nlq_chatbot_lambda_S3_access.arn
}
# Attach the API gateway access policy to the role
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_orchestration_lambda_api_gateway_access_policy_attachment" {
  role       = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.name
  policy_arn = aws_iam_policy.asu_nlq_chatbot_lambda_api_gateway_access.arn
}
# Attach the lambda function execution access policy to the role
resource "aws_iam_role_policy_attachment" "asu_nlq_chatbot_orchestration_lambda_function_execution_access_policy_attachment" {
  role       = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.name
  policy_arn = aws_iam_policy.asu_nlq_chatbot_lambda_function_execution_access.arn
}


####################################################################################################
#This section defines the lambda functions
####################################################################################################

# Defines the bedrock orchestration lambda function
resource "aws_lambda_function" "asu_nlq_chatbot_orchestration_lambda" {
  function_name = "asu_nlq_chatbot_orchestration_lambda_${var.random_suffix}"
  role = aws_iam_role.asu_nlq_chatbot_orchestration_lambda_role.arn

  handler = "lambda_function.lambda_handler"
  filename = data.archive_file.orchestration_lambda_zip.output_path
  source_code_hash = data.archive_file.orchestration_lambda_zip.output_base64sha256

  runtime = "python3.13"
  timeout = 60
  memory_size = 256
  layers = [
    "arn:aws:lambda:${var.aws_region}:336392948345:layer:AWSSDKPandas-Python313:1" # AWS SDK for Pandas layer
  ]

  environment {
    variables = {
      API_GATEWAY_URL = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.api_endpoint,
      DATABASE_DESCRIPTIONS_S3_NAME = aws_s3_bucket.asu_nlq_chatbot_database_descriptions_bucket.id,
      TEMPLATE_NAME = var.template_name,
      DATABASE_NAME = var.database_name
    }
  }
}


####################################################################################################
#This section defines the websocket API gateway
####################################################################################################

#Defines the websocket API gateway
resource "aws_apigatewayv2_api" "asu_nlq_chatbot_websocket_api_gateway" {
  name                       = "asu_nlq_chatbot_websocket_api_gateway_${var.random_suffix}"
  protocol_type              = "WEBSOCKET"
  route_selection_expression = "$request.body.action"

}

#Defines the websocket API gateway integration with the websocket opener lambda function
resource "aws_apigatewayv2_integration" "asu_nlq_chatbot_websocket_integration" {
  api_id           = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.asu_nlq_chatbot_orchestration_lambda.invoke_arn

}

#Defines the sendMessage route for the websocket API gateway
resource "aws_apigatewayv2_route" "asu_nlq_chatbot_sendMessage_route" {
  api_id    = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.id
  route_key = "sendMessage"
  target    = "integrations/${aws_apigatewayv2_integration.asu_nlq_chatbot_websocket_integration.id}"
  
}

#Defines the sendMessage route response for the websocket API gateway
resource "aws_apigatewayv2_route_response" "asu_nlq_chatbot_default_route_response" {
  api_id             = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.id
  route_id           = aws_apigatewayv2_route.asu_nlq_chatbot_sendMessage_route.id
  route_response_key = "$default"
}

#Defines the websocket api stage
resource "aws_apigatewayv2_stage" "asu_nlq_chatbot_websocket_api_gateway_stage" {
  api_id = aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.id
  name   = "prod"
  auto_deploy = true
  
}

# Grant API Gateway permission to invoke the Lambda function
resource "aws_lambda_permission" "asu_nlq_chatbot_api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.asu_nlq_chatbot_orchestration_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.asu_nlq_chatbot_websocket_api_gateway.execution_arn}/*/*"
}