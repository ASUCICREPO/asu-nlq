variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "random_suffix" {
  description = "A random suffix to be appended to the database name."
  type        = string
}

variable frontend_build_zip_path {
  description = "The path to the frontend build zip file."
  type        = string
}