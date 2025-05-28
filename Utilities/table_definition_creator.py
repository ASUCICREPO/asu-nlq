#!/usr/bin/env python3
"""
table_definition_creator.py

This script reads a table definition template and guides the user through
creating a complete table definition following the specified schema.
"""

import json
import sys
from typing import Dict, Any, List, Union


def load_template(filename: str) -> Dict[str, Any]:
    """Load the table definition template from JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Template file '{filename}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in template file: {e}")
        sys.exit(1)


def get_user_input(prompt: str, datatype: str, optional: bool = False, 
                   example: str = None, possible_values: List = None) -> Any:
    """Get user input with type validation and optional field handling."""
    
    # Build the prompt with example if provided
    full_prompt = prompt
    if example:
        full_prompt += f" (example: {example})"
    if optional:
        full_prompt += " [OPTIONAL - press Enter to skip]"
    full_prompt += ": "
    
    while True:
        user_input = input(full_prompt).strip()
        
        # Handle optional fields
        if optional and user_input == "":
            return None
        
        # Handle required fields
        if not optional and user_input == "":
            print("This field is required. Please provide a value.")
            continue
        
        # Type conversion and validation
        try:
            if datatype.lower() == "string":
                if possible_values and user_input not in possible_values:
                    print(f"Invalid value. Must be one of: {possible_values}")
                    continue
                return user_input
            
            elif datatype.lower() == "number":
                return int(user_input) if user_input.isdigit() else float(user_input)
            
            elif datatype.lower() == "boolean":
                if user_input.lower() in ['true', 't', 'yes', 'y', '1']:
                    return True
                elif user_input.lower() in ['false', 'f', 'no', 'n', '0']:
                    return False
                else:
                    print("Please enter a boolean value (true/false, yes/no, 1/0)")
                    continue
            
            elif datatype.lower() == "array":
                if user_input:
                    # For simple arrays, split by comma
                    return [item.strip() for item in user_input.split(',') if item.strip()]
                return []
            
            else:
                return user_input
                
        except ValueError:
            print(f"Invalid input for {datatype}. Please try again.")
            continue


def collect_column_data(template_column: Dict[str, Any]) -> Dict[str, Any]:
    """Collect data for a single column definition."""
    print("\n--- Column Definition ---")
    column_data = {}
    
    for field_name, field_def in template_column.items():
        if isinstance(field_def, dict) and 'datatype' in field_def:
            description = field_def.get('description', '')
            datatype = field_def.get('datatype')
            optional = field_def.get('optional', True)
            example = field_def.get('example')
            possible_values = field_def.get('possible_values')
            
            value = get_user_input(
                f"{field_name} - {description}",
                datatype,
                optional,
                example,
                possible_values
            )
            
            if value is not None:
                column_data[field_name] = value
    
    return column_data


def collect_index_data(template_index: Dict[str, Any]) -> Dict[str, Any]:
    """Collect data for a single index definition."""
    print("\n--- Index Definition ---")
    index_data = {}
    
    for field_name, field_def in template_index.items():
        if isinstance(field_def, dict) and 'datatype' in field_def:
            description = field_def.get('description', '')
            datatype = field_def.get('datatype')
            optional = field_def.get('optional', True)
            example = field_def.get('example')
            
            value = get_user_input(
                f"{field_name} - {description}",
                datatype,
                optional,
                example
            )
            
            if value is not None:
                index_data[field_name] = value
    
    return index_data


def collect_relationship_data(template_relationship: Dict[str, Any]) -> Dict[str, Any]:
    """Collect data for a single relationship definition."""
    print("\n--- Relationship Definition ---")
    relationship_data = {}
    
    for field_name, field_def in template_relationship.items():
        if isinstance(field_def, dict) and 'datatype' in field_def:
            description = field_def.get('description', '')
            datatype = field_def.get('datatype')
            optional = field_def.get('optional', True)
            example = field_def.get('example')
            
            value = get_user_input(
                f"{field_name} - {description}",
                datatype,
                optional,
                example
            )
            
            if value is not None:
                relationship_data[field_name] = value
    
    return relationship_data


def collect_array_data(field_name: str, template_item: Dict[str, Any], 
                      collector_func) -> List[Dict[str, Any]]:
    """Collect data for array fields (columns, indexes, relationships)."""
    items = []
    
    while True:
        print(f"\n=== Adding {field_name[:-1]} (currently have {len(items)}) ===")
        print("Press Enter without typing anything to finish adding items.")
        
        if input("Add another item? (Enter to finish, any key to continue): ").strip() == "":
            break
            
        item_data = collector_func(template_item)
        if item_data:
            items.append(item_data)
    
    return items if items else None


def sanitize_filename(filename: str) -> str:
    """Sanitize a string to be safe for use as a filename."""
    # Replace problematic characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = "table"
    
    return filename


def main():
    """Main function to orchestrate the table definition creation."""
    print("=== Database Table Definition Creator ===")
    print("This tool will help you create a complete table definition.")
    print("Required fields must be filled. Optional fields can be skipped by pressing Enter.\n")
    
    # Load template
    template = load_template("../Assets/table_definition_template.json")
    
    # Initialize output data
    output_data = {}
    table_name = None
    
    # Process each top-level field in the template
    for field_name, field_def in template.items():
        if not isinstance(field_def, dict) or 'datatype' not in field_def:
            continue
            
        description = field_def.get('description', '')
        datatype = field_def.get('datatype')
        optional = field_def.get('optional', True)
        example = field_def.get('example')
        
        print(f"\n=== {field_name.upper()} ===")
        
        # Handle special array fields with complex objects
        if field_name == "columns" and datatype == "Array":
            print("Now collecting column definitions...")
            template_column = field_def['example'][0] if field_def.get('example') else {}
            columns = collect_array_data(field_name, template_column, collect_column_data)
            if columns:
                output_data[field_name] = columns
        
        elif field_name == "indexes" and datatype == "Array":
            print("Now collecting index definitions...")
            template_index = field_def['example'][0] if field_def.get('example') else {}
            indexes = collect_array_data(field_name, template_index, collect_index_data)
            if indexes:
                output_data[field_name] = indexes
        
        elif field_name == "relationships" and datatype == "Array":
            print("Now collecting relationship definitions...")
            template_relationship = field_def['example'][0] if field_def.get('example') else {}
            relationships = collect_array_data(field_name, template_relationship, collect_relationship_data)
            if relationships:
                output_data[field_name] = relationships
        
        else:
            # Handle simple fields
            value = get_user_input(
                f"{field_name} - {description}",
                datatype,
                optional,
                example
            )
            
            if value is not None:
                output_data[field_name] = value
                
                # Capture table name for filename
                if field_name == "table_name":
                    table_name = value
    
    # Create output filename with table name prefix
    if table_name:
        sanitized_name = sanitize_filename(table_name)
        output_filename = f"{sanitized_name}_output.json"
    else:
        output_filename = "output.json"
    
    # Save output
    try:
        with open(output_filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\n✅ Table definition saved to '{output_filename}'")
        print(f"Created definition for table: {output_data.get('table_name', 'Unknown')}")
        
        # Show summary
        column_count = len(output_data.get('columns', []))
        index_count = len(output_data.get('indexes', []))
        relationship_count = len(output_data.get('relationships', []))
        
        print(f"Summary: {column_count} columns, {index_count} indexes, {relationship_count} relationships")
        
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()