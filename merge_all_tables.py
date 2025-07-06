#!/usr/bin/env python3
"""
Script to merge all table mapping files into a single consolidated format.
"""

import json
import os
from pathlib import Path

def load_json_file(file_path):
    """Load JSON file and return parsed data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return None

def merge_tables():
    """Merge all table mapping files into the required format."""
    
    # Load the HTML table data to get table titles
    html_data = load_json_file('data/extracted_tables_html.json')
    if not html_data:
        print("Error: Could not load extracted_tables_html.json")
        return
    
    # Create a mapping of table_index to heading_text
    table_titles = {}
    for table_info in html_data:
        if 'table_index' in table_info and 'heading_text' in table_info:
            table_titles[table_info['table_index']] = table_info['heading_text']
    
    # Initialize the result dictionary
    merged_result = {}
    
    # Process tables 2 to 35
    for table_num in range(2, 36):
        table_file = f'data/table_{table_num}_mapping.json'
        
        # Load the table mapping data
        table_data = load_json_file(table_file)
        if not table_data:
            print(f"Skipping table {table_num} - no data found")
            continue
        
        # Get the table title from the HTML data
        table_title = table_titles.get(table_num, f"Table {table_num}")
        
        # Initialize the table structure
        merged_result[table_title] = {}
        
        # Process each mapping in the table
        for old_key, new_name in table_data.items():
            # Parse the old_key format: "old_huyen|old_xa"
            if '|' in old_key:
                old_huyen, old_xa = old_key.split('|', 1)
                
                # Initialize huyen dictionary if not exists
                if old_huyen not in merged_result[table_title]:
                    merged_result[table_title][old_huyen] = {}
                
                # Add the mapping
                merged_result[table_title][old_huyen][old_xa] = new_name
            else:
                print(f"Warning: Invalid key format in table {table_num}: {old_key}")
        
        print(f"Processed table {table_num}: {table_title} with {len(table_data)} mappings")
    
    # Save the merged result
    output_file = 'data/merged_tables.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_result, f, ensure_ascii=False, indent=2)
    
    print(f"\nMerged data saved to {output_file}")
    print(f"Total tables processed: {len(merged_result)}")
    
    # Print summary
    total_mappings = 0
    for table_name, table_data in merged_result.items():
        table_count = sum(len(xa_mappings) for xa_mappings in table_data.values())
        total_mappings += table_count
        print(f"  {table_name}: {table_count} mappings")
    
    print(f"Total mappings: {total_mappings}")

if __name__ == "__main__":
    merge_tables()
