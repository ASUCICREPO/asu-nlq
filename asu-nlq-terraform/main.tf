

provider "aws" {
  region = var.aws_region_provider # Ensure this matches the requirements for the services (model access etc)
}


module "frontend" {
  source     = "./modules/frontend"
  aws_region = var.aws_region
  websocket_api_endpoint = "${module.backend.websocket_api_endpoint}"

}


module "backend" {
  source            = "./modules/backend"
  aws_region        = var.aws_region
  knowledge_base_id = var.knowledge_base_id
  TEMPERATURE       = var.TEMPERATURE
  ORCHESTRATION_MODEL_ID = var.ORCHESTRATION_MODEL_ID
  CLASSIFICATION_MODEL_ID = var.CLASSIFICATION_MODEL_ID
  NUM_KB_RESULTS = var.NUM_KB_RESULTS
  SOURCE_EXTRACTION_BOT_ID = var.SOURCE_EXTRACTION_BOT_ID

}
