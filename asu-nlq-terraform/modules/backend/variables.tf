variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "template_name" {
  description = "The name of the json database template to be used for the backend."
  type        = string
}

variable "database_name" {
  description = "The name of the database file used."
  type        = string
}

variable "random_suffix" {
  description = "A random suffix to be appended to the database name."
  type        = string
}