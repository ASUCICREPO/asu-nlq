#!/usr/bin/env python3
"""
Schema Manager - Database Schema Definition Tool

This tool manages database schema definition files for natural language query chatbot systems.
It provides full CRUD operations for tables and columns with an interactive command-line interface.

Usage:
    python schema_manager.py          # Create new schema file
    python schema_manager.py --edit   # Edit existing schema file
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SchemaManager:
    def __init__(self):
        self.target_file = Path("../asu-nlq-terraform/S3/asu_facts_table_definition_template.json")
        self.schema_data = {"tables": []}
        self.changes_made = False
        self.modified_tables = set()
    
    def run(self):
        """Main entry point for the schema manager."""
        try:
            edit_mode = "--edit" in sys.argv
            
            if edit_mode:
                self._handle_edit_mode()
            else:
                self._handle_create_mode()
            
            self._main_menu()
            
            if self.changes_made:
                self._save_schema()
                self._print_final_summary()
            else:
                print("\nNo changes made. Exiting.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\nError: {e}")
            sys.exit(1)
    
    def _handle_edit_mode(self):
        """Handle editing existing schema file."""
        if not self.target_file.exists():
            raise FileNotFoundError("No existing schema file found. Run without --edit to create a new file.")
        
        with open(self.target_file, 'r') as f:
            self.schema_data = json.load(f)
        
        print(f"Loaded existing schema with {len(self.schema_data['tables'])} tables.")
    
    def _handle_create_mode(self):
        """Handle creating new schema file."""
        if self.target_file.exists():
            raise FileExistsError("Schema file already exists. Use --edit to modify existing file.")
        
        print("Creating new schema file...")
        # Ensure target directory exists
        self.target_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _main_menu(self):
        """Display and handle the main menu."""
        while True:
            print("\n" + "="*60)
            print("SCHEMA MANAGER - MAIN MENU")
            print("="*60)
            print(f"Current tables: {len(self.schema_data['tables'])}")
            
            if self.schema_data['tables']:
                for i, table in enumerate(self.schema_data['tables'], 1):
                    print(f"  {i}. {table['table_name']} ({len(table['columns'])} columns)")
            
            print("\nOptions:")
            print("1. Add new table")
            print("2. View/Edit existing table")
            print("3. Delete table")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                self._add_table()
            elif choice == '2':
                self._select_table_to_edit()
            elif choice == '3':
                self._delete_table()
            elif choice == '4':
                break
            else:
                print("Invalid option. Please select 1-4.")
    
    def _add_table(self):
        """Add a new table to the schema."""
        print("\n" + "-"*40)
        print("ADD NEW TABLE")
        print("-"*40)
        
        table_name = input("Enter table name: ").strip()
        if not table_name:
            print("Table name cannot be empty.")
            return
        
        # Check if table already exists
        if any(table['table_name'] == table_name for table in self.schema_data['tables']):
            print(f"Table '{table_name}' already exists.")
            return
        
        description = input("Enter table description: ").strip()
        if not description:
            print("Table description cannot be empty.")
            return
        
        new_table = {
            "table_name": table_name,
            "description": description,
            "columns": []
        }
        
        # Add columns
        print("\nNow add columns to this table:")
        self._add_columns_to_table(new_table)
        
        if new_table['columns']:  # Only add if it has columns
            self.schema_data['tables'].append(new_table)
            self.changes_made = True
            self.modified_tables.add(table_name)
            print(f"\nTable '{table_name}' added successfully!")
        else:
            print("\nTable not added - no columns were created.")
    
    def _select_table_to_edit(self):
        """Select a table to view or edit."""
        if not self.schema_data['tables']:
            print("\nNo tables exist yet. Add a table first.")
            return
        
        print("\n" + "-"*40)
        print("SELECT TABLE TO VIEW/EDIT")
        print("-"*40)
        
        for i, table in enumerate(self.schema_data['tables'], 1):
            print(f"{i}. {table['table_name']}")
        
        try:
            choice = int(input(f"\nSelect table (1-{len(self.schema_data['tables'])}): ").strip())
            if 1 <= choice <= len(self.schema_data['tables']):
                self._table_menu(self.schema_data['tables'][choice - 1])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def _delete_table(self):
        """Delete a table from the schema."""
        if not self.schema_data['tables']:
            print("\nNo tables exist to delete.")
            return
        
        print("\n" + "-"*40)
        print("DELETE TABLE")
        print("-"*40)
        
        for i, table in enumerate(self.schema_data['tables'], 1):
            print(f"{i}. {table['table_name']}")
        
        try:
            choice = int(input(f"\nSelect table to delete (1-{len(self.schema_data['tables'])}): ").strip())
            if 1 <= choice <= len(self.schema_data['tables']):
                table_name = self.schema_data['tables'][choice - 1]['table_name']
                confirm = input(f"Are you sure you want to delete '{table_name}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    del self.schema_data['tables'][choice - 1]
                    self.changes_made = True
                    self.modified_tables.add(f"{table_name} (DELETED)")
                    print(f"Table '{table_name}' deleted successfully!")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def _table_menu(self, table: Dict[str, Any]):
        """Display and handle the table-specific menu."""
        while True:
            print("\n" + "-"*50)
            print(f"TABLE: {table['table_name']}")
            print("-"*50)
            print(f"Description: {table['description']}")
            print(f"Columns: {len(table['columns'])}")
            
            if table['columns']:
                for i, col in enumerate(table['columns'], 1):
                    print(f"  {i}. {col['column_name']} ({col['data_type']})")
            
            print("\nOptions:")
            print("1. Add column")
            print("2. Edit column")
            print("3. Delete column")
            print("4. Edit table name/description")
            print("5. Back to main menu")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self._add_columns_to_table(table)
            elif choice == '2':
                self._edit_column(table)
            elif choice == '3':
                self._delete_column(table)
            elif choice == '4':
                self._edit_table_info(table)
            elif choice == '5':
                break
            else:
                print("Invalid option. Please select 1-5.")
    
    def _add_columns_to_table(self, table: Dict[str, Any]):
        """Add columns to a table."""
        while True:
            column = self._create_column()
            if column:
                table['columns'].append(column)
                self.changes_made = True
                self.modified_tables.add(table['table_name'])
                print(f"Column '{column['column_name']}' added successfully!")
            
            if not self._ask_yes_no("Add another column?"):
                break
    
    def _create_column(self) -> Optional[Dict[str, Any]]:
        """Create a single column with all required fields."""
        print("\n" + "-"*30)
        print("ADD NEW COLUMN")
        print("-"*30)
        
        column_name = input("Enter column name: ").strip()
        if not column_name:
            print("Column name cannot be empty.")
            return None
        
        data_type = input("Enter data type (e.g., VARCHAR(50), INTEGER): ").strip()
        if not data_type:
            print("Data type cannot be empty.")
            return None
        
        description = input("Enter column description: ").strip()
        if not description:
            print("Column description cannot be empty.")
            return None
        
        # Get possible values
        possible_values = []
        print("\nEnter possible values for this column:")
        while True:
            value = input("Enter possible value (or press Enter to finish): ").strip()
            if not value:
                break
            possible_values.append(value)
        
        if not possible_values:
            print("At least one possible value is required.")
            return None
        
        return {
            "column_name": column_name,
            "data_type": data_type,
            "description": description,
            "possible_values": possible_values
        }
    
    def _edit_column(self, table: Dict[str, Any]):
        """Edit an existing column."""
        if not table['columns']:
            print("\nNo columns exist to edit.")
            return
        
        print("\n" + "-"*40)
        print("SELECT COLUMN TO EDIT")
        print("-"*40)
        
        for i, col in enumerate(table['columns'], 1):
            print(f"{i}. {col['column_name']}")
        
        try:
            choice = int(input(f"\nSelect column (1-{len(table['columns'])}): ").strip())
            if 1 <= choice <= len(table['columns']):
                self._column_edit_menu(table, table['columns'][choice - 1])
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def _column_edit_menu(self, table: Dict[str, Any], column: Dict[str, Any]):
        """Menu for editing a specific column."""
        while True:
            print("\n" + "-"*40)
            print(f"EDIT COLUMN: {column['column_name']}")
            print("-"*40)
            print(f"Data Type: {column['data_type']}")
            print(f"Description: {column['description']}")
            print(f"Possible Values: {', '.join(column['possible_values'])}")
            
            print("\nWhat would you like to edit?")
            print("1. Column name")
            print("2. Data type")
            print("3. Description")
            print("4. Possible values")
            print("5. Done editing this column")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                new_name = input(f"Enter new column name (current: {column['column_name']}): ").strip()
                if new_name:
                    column['column_name'] = new_name
                    self.changes_made = True
                    self.modified_tables.add(table['table_name'])
            elif choice == '2':
                new_type = input(f"Enter new data type (current: {column['data_type']}): ").strip()
                if new_type:
                    column['data_type'] = new_type
                    self.changes_made = True
                    self.modified_tables.add(table['table_name'])
            elif choice == '3':
                new_desc = input(f"Enter new description (current: {column['description']}): ").strip()
                if new_desc:
                    column['description'] = new_desc
                    self.changes_made = True
                    self.modified_tables.add(table['table_name'])
            elif choice == '4':
                self._edit_possible_values(table, column)
            elif choice == '5':
                break
            else:
                print("Invalid option. Please select 1-5.")
    
    def _edit_possible_values(self, table: Dict[str, Any], column: Dict[str, Any]):
        """Edit possible values for a column."""
        while True:
            print("\n" + "-"*30)
            print("EDIT POSSIBLE VALUES")
            print("-"*30)
            print("Current values:")
            for i, value in enumerate(column['possible_values'], 1):
                print(f"  {i}. {value}")
            
            print("\nOptions:")
            print("1. Add new value")
            print("2. Remove value")
            print("3. Done editing values")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == '1':
                new_value = input("Enter new possible value: ").strip()
                if new_value and new_value not in column['possible_values']:
                    column['possible_values'].append(new_value)
                    self.changes_made = True
                    self.modified_tables.add(table['table_name'])
                    print(f"Added value: {new_value}")
                elif new_value in column['possible_values']:
                    print("Value already exists.")
            elif choice == '2':
                if len(column['possible_values']) <= 1:
                    print("Cannot remove the last possible value.")
                    continue
                try:
                    idx = int(input(f"Select value to remove (1-{len(column['possible_values'])}): ")) - 1
                    if 0 <= idx < len(column['possible_values']):
                        removed = column['possible_values'].pop(idx)
                        self.changes_made = True
                        self.modified_tables.add(table['table_name'])
                        print(f"Removed value: {removed}")
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == '3':
                break
            else:
                print("Invalid option. Please select 1-3.")
    
    def _delete_column(self, table: Dict[str, Any]):
        """Delete a column from a table."""
        if not table['columns']:
            print("\nNo columns exist to delete.")
            return
        
        print("\n" + "-"*40)
        print("DELETE COLUMN")
        print("-"*40)
        
        for i, col in enumerate(table['columns'], 1):
            print(f"{i}. {col['column_name']}")
        
        try:
            choice = int(input(f"\nSelect column to delete (1-{len(table['columns'])}): ").strip())
            if 1 <= choice <= len(table['columns']):
                col_name = table['columns'][choice - 1]['column_name']
                confirm = input(f"Are you sure you want to delete column '{col_name}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    del table['columns'][choice - 1]
                    self.changes_made = True
                    self.modified_tables.add(table['table_name'])
                    print(f"Column '{col_name}' deleted successfully!")
                else:
                    print("Deletion cancelled.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")
    
    def _edit_table_info(self, table: Dict[str, Any]):
        """Edit table name and description."""
        print("\n" + "-"*40)
        print("EDIT TABLE INFORMATION")
        print("-"*40)
        print(f"Current name: {table['table_name']}")
        print(f"Current description: {table['description']}")
        
        new_name = input(f"\nEnter new table name (press Enter to keep current): ").strip()
        if new_name:
            old_name = table['table_name']
            table['table_name'] = new_name
            self.changes_made = True
            # Update the modified_tables set
            if old_name in self.modified_tables:
                self.modified_tables.remove(old_name)
            self.modified_tables.add(new_name)
        
        new_desc = input(f"Enter new description (press Enter to keep current): ").strip()
        if new_desc:
            table['description'] = new_desc
            self.changes_made = True
            self.modified_tables.add(table['table_name'])
    
    def _ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question and return boolean result."""
        while True:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer in ('y', 'yes'):
                return True
            elif answer in ('n', 'no'):
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def _save_schema(self):
        """Save the schema to the target file."""
        with open(self.target_file, 'w') as f:
            json.dump(self.schema_data, f, indent=2)
        print(f"\nSchema saved to: {self.target_file}")
    
    def _print_final_summary(self):
        """Print a summary of modified tables for easy copy/paste."""
        print("\n" + "="*80)
        print("FINAL SUMMARY - MODIFIED TABLES")
        print("="*80)
        
        for table in self.schema_data['tables']:
            if table['table_name'] in self.modified_tables or any('DELETED' in name for name in self.modified_tables):
                print(f"\nTable: {table['table_name']}")
                print(f"Description: {table['description']}")
                print("Columns:")
                for column in table['columns']:
                    print(f"  - {column['column_name']}: {column['description']}")
        
        # Show deleted tables
        deleted_tables = [name for name in self.modified_tables if 'DELETED' in name]
        if deleted_tables:
            print("\nDeleted Tables:")
            for table_name in deleted_tables:
                print(f"  - {table_name}")


def main():
    """Main entry point."""
    manager = SchemaManager()
    manager.run()


if __name__ == "__main__":
    main()