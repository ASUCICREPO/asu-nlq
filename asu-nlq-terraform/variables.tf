variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
}

variable "aws_region_provider" {
  description = "The AWS region where resources will be created. For the provider"
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

variable "knowledge_base_id" {
  description = "The ID of the knowledge base to be used in the backend."
  type        = string
}