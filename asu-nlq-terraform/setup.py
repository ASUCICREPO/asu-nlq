#!/usr/bin/env python3
"""
Setup Tool - Terraform Variables Configuration

This tool updates the knowledge_base_id in the terraform.tfvars file.
It reads the existing file, prompts for a new knowledge base ID, and updates the file.

Usage:
    python setup.py
"""

import os
import sys
from pathlib import Path


class TerraformSetup:
    def __init__(self):
        self.tfvars_file = Path("terraform.tfvars")
    
    def run(self):
        """Main entry point for the setup tool."""
        try:
            print("="*60)
            print("TERRAFORM SETUP - KNOWLEDGE BASE ID UPDATER")
            print("="*60)
            
            # Check if file exists
            if not self.tfvars_file.exists():
                print(f"Error: {self.tfvars_file} not found in current directory.")
                sys.exit(1)
            
            # Read current file
            current_content = self._read_tfvars_file()
            current_kb_id = self._extract_current_kb_id(current_content)
            
            if current_kb_id:
                print(f"\nCurrent knowledge_base_id: {current_kb_id}")
            else:
                print("\nNo knowledge_base_id found in file.")
            
            # Get new knowledge base ID from user
            new_kb_id = self._get_new_knowledge_base_id()
            
            # Update the file
            updated_content = self._update_knowledge_base_id(current_content, new_kb_id)
            self._write_tfvars_file(updated_content)
            
            print(f"\n✅ Successfully updated knowledge_base_id to: {new_kb_id}")
            print(f"📁 File updated: {self.tfvars_file.absolute()}")
            
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    
    def _read_tfvars_file(self):
        """Read the terraform.tfvars file and return its content."""
        try:
            with open(self.tfvars_file, 'r') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read {self.tfvars_file}: {e}")
    
    def _extract_current_kb_id(self, content):
        """Extract the current knowledge_base_id value from the file content."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('knowledge_base_id'):
                # Extract value between quotes
                if '=' in line:
                    value_part = line.split('=', 1)[1].strip()
                    # Remove quotes and any comments
                    if '#' in value_part:
                        value_part = value_part.split('#')[0].strip()
                    # Remove surrounding quotes
                    value_part = value_part.strip('"\'')
                    return value_part
        return None
    
    def _get_new_knowledge_base_id(self):
        """Prompt user for new knowledge base ID."""
        while True:
            new_id = input("\nEnter new knowledge_base_id: ").strip()
            if new_id:
                # Confirm the input
                print(f"\nYou entered: {new_id}")
                confirm = input("Is this correct? (y/n): ").strip().lower()
                if confirm in ('y', 'yes'):
                    return new_id
                else:
                    print("Let's try again...")
                    continue
            else:
                print("Knowledge base ID cannot be empty. Please try again.")
    
    def _update_knowledge_base_id(self, content, new_kb_id):
        """Update the knowledge_base_id in the file content."""
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.strip().startswith('knowledge_base_id'):
                # Preserve any comments on the line
                if '#' in line:
                    # Split at the first # to preserve comments
                    var_part, comment_part = line.split('#', 1)
                    # Reconstruct the line with new value
                    updated_line = f'knowledge_base_id = "{new_kb_id}" #{comment_part}'
                else:
                    # No comment, just update the value
                    updated_line = f'knowledge_base_id = "{new_kb_id}"'
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def _write_tfvars_file(self, content):
        """Write the updated content back to the terraform.tfvars file."""
        try:
            with open(self.tfvars_file, 'w') as f:
                f.write(content)
        except Exception as e:
            raise Exception(f"Failed to write {self.tfvars_file}: {e}")
    
    def preview_changes(self):
        """Preview what changes would be made without actually updating the file."""
        if not self.tfvars_file.exists():
            print(f"Error: {self.tfvars_file} not found in current directory.")
            return
        
        current_content = self._read_tfvars_file()
        current_kb_id = self._extract_current_kb_id(current_content)
        
        print("\n" + "="*60)
        print("PREVIEW MODE - CURRENT TERRAFORM.TFVARS CONTENT")
        print("="*60)
        print(current_content)
        print("\n" + "="*60)
        
        if current_kb_id:
            print(f"Current knowledge_base_id: {current_kb_id}")
        else:
            print("No knowledge_base_id found in file.")


def main():
    """Main entry point."""
    # Check for preview mode
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        setup = TerraformSetup()
        setup.preview_changes()
    else:
        setup = TerraformSetup()
        setup.run()


if __name__ == "__main__":
    main()