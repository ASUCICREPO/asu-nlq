variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "random_suffix" {
  description = "A random suffix to be appended to the database name."
  type        = string
}