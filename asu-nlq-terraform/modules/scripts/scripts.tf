# Prepare the frontend files for deployment
resource "null_resource" "prepare_orchestration_lambda_files" {
  # Trigger rebuild only when the WebSocket endpoint changes
  triggers = {
    websocket_endpoint = var.websocket_api_endpoint
  }

  # Main provisioner - handles build process with rollback on failure
  provisioner "local-exec" {
    command = <<-EOT
      set -e  # Exit on any error
      
      # Function to perform rollback
      rollback() {
        echo "Build failed, performing rollback..."
        
        # Restore original constants file
        if [ -f "./frontend/src/Utilities/constants_backup.jsx" ]; then
          cp "./frontend/src/Utilities/constants_backup.jsx" "./frontend/src/Utilities/constants.jsx"
          echo "Restored constants.jsx from backup"
        fi
        
        # Remove build artifacts
        if [ -d "./frontend/build" ]; then
          rm -rf "./frontend/build"
          echo "Removed build directory"
        fi
        
        # Remove node_modules
        if [ -d "./frontend/node_modules" ]; then
          rm -rf "./frontend/node_modules"
          echo "Removed node_modules directory"
        fi
        
        # Remove zip file
        if [ -f "./frontend/zips/build.zip" ]; then
          rm -f "./frontend/zips/build.zip"
          echo "Removed build.zip"
        fi
        
        echo "Rollback completed"
        exit 1
      }
      
      echo "Starting frontend build process..."
      
      # Step 1: Verify backup file exists
      if [ ! -f "./frontend/src/Utilities/constants_backup.jsx" ]; then
        echo "Error: constants_backup.jsx not found"
        rollback
      fi
      
      # Step 2: Restore constants file from backup and update with endpoint
      echo "Updating constants file with WebSocket endpoint..."
      cp "./frontend/src/Utilities/constants_backup.jsx" "./frontend/src/Utilities/constants.jsx" || rollback
      
      # Replace the token with the actual endpoint (with /prod suffix)
      sed -i.tmp 's|"REPLACE_TOKEN"|"${var.websocket_api_endpoint}/prod"|g' "./frontend/src/Utilities/constants.jsx" || rollback
      rm -f "./frontend/src/Utilities/constants.jsx.tmp" || rollback
      
      echo "Constants file updated successfully"
      
      # Step 3: Install dependencies
      echo "Installing npm dependencies..."
      cd "./frontend" || rollback
      npm install || rollback
      
      echo "Dependencies installed successfully"
      
      # Step 4: Build the application
      echo "Building application..."
      npm run build || rollback
      
      echo "Application built successfully"
      
      # Step 5: Create zips directory if it doesn't exist
      mkdir -p "./zips" || rollback
      
      # Step 6: Create zip archive
      echo "Creating deployment archive..."
      cd "./build" || rollback
      
      # Remove existing build.zip if it exists
      if [ -f "../zips/build.zip" ]; then
        rm -f "../zips/build.zip" || rollback
      fi
      
      # Create new zip file
      zip -r "../zips/build.zip" . || rollback
      
      echo "Deployment archive created successfully at ./frontend/zips/build.zip"
      echo "Frontend build process completed successfully"
    EOT
    
    # Set working directory to the Terraform root
    working_dir = path.root
  }

  # Destroy-time provisioner - cleanup on destroy
  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      echo "Cleaning up frontend build artifacts..."
      
      # Restore original constants file
      if [ -f "./frontend/src/Utilities/constants_backup.jsx" ]; then
        cp "./frontend/src/Utilities/constants_backup.jsx" "./frontend/src/Utilities/constants.jsx"
        echo "Restored constants.jsx from backup"
      fi
      
      # Remove build directory
      if [ -d "./frontend/build" ]; then
        rm -rf "./frontend/build"
        echo "Removed build directory"
      fi
      
      # Remove node_modules
      if [ -d "./frontend/node_modules" ]; then
        rm -rf "./frontend/node_modules"
        echo "Removed node_modules directory"
      fi
      
      # Remove zip file
      if [ -f "./frontend/zips/build.zip" ]; then
        rm -f "./frontend/zips/build.zip"
        echo "Removed build.zip"
      fi
      
      echo "Frontend cleanup completed"
    EOT
    
    working_dir = path.root
  }

  # Ensure this runs after the backend module is complete
  depends_on = [var.websocket_api_endpoint]
}