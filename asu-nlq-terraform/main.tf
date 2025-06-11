

provider "aws" {
  region = var.aws_region_provider # Ensure this matches the requirements for the services (model access etc)
}

# Generates a random suffix for the deployment to ensure uniqueness
resource "random_id" "random_suffix" {
  byte_length = 4
}

# module "frontend" {
#   source     = "./modules/frontend"
#   aws_region = var.aws_region
#   websocket_api_endpoint = "${module.backend.websocket_api_endpoint}"

# }


module "backend" {
  source            = "./modules/backend"
  aws_region        = var.aws_region
  template_name     = var.template_name
  database_name     = var.database_name
  random_suffix     = random_id.random_suffix.hex

}

# Prepare the frontend files for deployment
resource "null_resource" "prepare_orchestration_lambda_files" {
  provisioner "local-exec" {
    command = ""
  }

  depends_on = [ module.backend ]
}

module "frontend" {
  source     = "./modules/frontend"
  aws_region = var.aws_region
  websocket_api_endpoint = "${module.backend.websocket_api_endpoint}"

  depends_on = [ null_resource.prepare_orchestration_lambda_files, module.backend]

}


