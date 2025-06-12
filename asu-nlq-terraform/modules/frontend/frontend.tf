####################################################################################################
# This section defines the S3 bucket for storing the frontend files
####################################################################################################
# Defines the S3 bucket for storing database descriptions and schemas
resource "aws_s3_bucket" "asu_nlq_frontend_store_bucket" {
  bucket        = "asu-nlq-frontend-store-bucket-${var.random_suffix}"
  force_destroy = true
}

# Upload the frontend file zip to S3
resource "aws_s3_object" "asu_nlq_frontend_store_upload" {
  bucket       = aws_s3_bucket.asu_nlq_frontend_store_bucket.id
  key          = "build.zip"
  source       = "${path.root}/frontend/zips/build.zip"
  depends_on   = [aws_s3_bucket.asu_nlq_frontend_store_bucket]
  content_type = "application/zip"
}

# Add this resource to create a delay
resource "time_sleep" "wait_for_s3_upload" {
  depends_on = [aws_s3_object.asu_nlq_frontend_store_upload]
  create_duration = "30s"  # Wait 30 seconds after S3 upload
}

####################################################################################################
# This section creates the amplify deployment
####################################################################################################
module "amplify" {
  source  = "JetBrains/amplify/aws"
  version = "0.4.0"
  
  name            = "asu-nlq-frontend"
  deployment_name = "main"
  
  aws_s3_bucket_store = {
    bucket_name   = aws_s3_bucket.asu_nlq_frontend_store_bucket.id
    bucket_path   = ""
    zip_file_name = "build.zip"
    region        = var.aws_region
  }

  username = ""
  password = "N@wY@rk321"
  
  tags = {
    environment = "prod"
    project     = "asu-nlq"
  }
  
  depends_on = [time_sleep.wait_for_s3_upload]
}