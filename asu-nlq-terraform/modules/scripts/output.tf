output "frontend_build_zip_path" {
  description = "Path to the frontend build zip file"
  value       = "${path.root}/frontend/zips/build.zip"
  depends_on  = [null_resource.prepare_orchestration_lambda_files]
}