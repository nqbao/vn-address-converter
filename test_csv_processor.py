#!/usr/bin/env python3
"""
Script to process addresses from tests.csv file.
Parses each old address and converts it to new format, showing error cases.
"""

import csv
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vn_address_converter import parse_address, convert_to_new_address
from vn_address_converter.models import MappingMissingError


def process_csv_file(csv_path: str):
    """Process addresses from CSV file and show only error cases."""
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found")
        return
    
    success_count = 0
    error_count = 0
    copy_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since row 1 is header
            old_address = row['old_address'].strip()
            expected_new_address = row['new_address'].strip()
            
            try:
                # Step 1: Parse the old address
                try:
                    parsed_address = parse_address(old_address)
                except Exception as e:
                    print(f"Row {row_num}: Parse Error - {e}")
                    print(f"  Address: {old_address}")
                    error_count += 1
                    continue
                
                # Step 2: Convert to new address format
                try:
                    converted_address = convert_to_new_address(parsed_address)
                    converted_str = converted_address.format()
                    
                    # Check if it's a copy (no district)
                    if converted_address is not parsed_address and all([
                        converted_address.street_address == parsed_address.street_address,
                        converted_address.ward == parsed_address.ward,
                        converted_address.district == parsed_address.district,
                        converted_address.province == parsed_address.province
                    ]):
                        copy_count += 1
                    else:
                        success_count += 1
                    
                except MappingMissingError as e:
                    print(f"Row {row_num}: Mapping Error - {e.level.value} '{e.value}' not found")
                    print(f"  Address: {old_address}")
                    error_count += 1
                    
                except ValueError as e:
                    print(f"Row {row_num}: Validation Error - {e}")
                    print(f"  Address: {old_address}")
                    error_count += 1
                    
                except Exception as e:
                    print(f"Row {row_num}: Unexpected Error - {e}")
                    print(f"  Address: {old_address}")
                    error_count += 1
                    
            except Exception as e:
                print(f"Row {row_num}: Processing Error - {e}")
                print(f"  Address: {old_address}")
                error_count += 1
    
    # Print summary only if there are any results
    total = success_count + error_count + copy_count
    if total > 0:
        print(f"\nProcessed {total} addresses: {success_count} converted, {copy_count} copied, {error_count} errors")


if __name__ == "__main__":
    csv_file = "tests/tests.csv"
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    process_csv_file(csv_file)