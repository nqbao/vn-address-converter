#!/usr/bin/env python3
"""
Script to process addresses from tests.csv file.
Parses each old address and converts it to new format, showing error cases.
"""

import csv
import sys
import os
import random
from collections import defaultdict
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vn_address_converter import parse_address, convert_to_new_address
from vn_address_converter.models import MappingMissingError


def process_csv_file(csv_path: str, max_errors: int = 100):
    """Process addresses from CSV file and show only error cases."""
    
    if not os.path.exists(csv_path):
        print(f"Error: CSV file '{csv_path}' not found")
        return
    
    success_count = 0
    error_count = 0
    copy_count = 0
    validation_error_count = 0
    
    # Collect errors by type
    error_examples = defaultdict(list)  # error_type -> list of (row_num, address, error_msg)
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        # Check if this is a single-column CSV with just "address"
        has_single_address_column = (
            'address' in reader.fieldnames and 
            len(reader.fieldnames) == 1
        )
        
        # Check if this is a two-column CSV with old_address and new_address
        has_validation_columns = (
            'old_address' in reader.fieldnames and 
            'new_address' in reader.fieldnames
        )
        
        if not has_single_address_column and not has_validation_columns:
            print(f"Error: CSV must have either 'address' column only, or both 'old_address' and 'new_address' columns")
            print(f"Found columns: {reader.fieldnames}")
            return
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 since row 1 is header
            if has_single_address_column:
                old_address = row['address'].strip()
                expected_new_address = None  # No validation for single column
            else:
                old_address = row['old_address'].strip()
                expected_new_address = row['new_address'].strip()
            
            try:
                # Step 1: Parse the old address
                try:
                    parsed_address = parse_address(old_address)
                except Exception as e:
                    error_type = "Parse Error"
                    error_examples[error_type].append((row_num, old_address, str(e)))
                    error_count += 1
                    if error_count >= max_errors:
                        break
                    continue
                
                # Step 2: Convert to new address format
                try:
                    converted_address = convert_to_new_address(parsed_address)
                    converted_str = converted_address.format()
                    
                    # Only validate if we have expected result (two-column mode)
                    if expected_new_address and converted_str != expected_new_address:
                        error_type = "Validation Mismatch"
                        error_msg = f"Expected: '{expected_new_address}', Got: '{converted_str}'"
                        error_examples[error_type].append((row_num, old_address, error_msg))
                        validation_error_count += 1
                        continue

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
                    error_type = "Mapping Error"
                    error_msg = f"{e.level.value} '{e.value}' not found"
                    error_examples[error_type].append((row_num, old_address, error_msg))
                    error_count += 1
                    if error_count >= max_errors:
                        break
                    
                except ValueError as e:
                    error_type = "Validation Error"
                    error_examples[error_type].append((row_num, old_address, str(e)))
                    error_count += 1
                    if error_count >= max_errors:
                        break
                    
                except Exception as e:
                    error_type = "Unexpected Error"
                    error_examples[error_type].append((row_num, old_address, str(e)))
                    error_count += 1
                    if error_count >= max_errors:
                        break
                    
            except Exception as e:
                error_type = "Processing Error"
                error_examples[error_type].append((row_num, old_address, str(e)))
                error_count += 1
                if error_count >= max_errors:
                    break
            
            # Check if we should stop due to parse errors
            if error_count >= max_errors:
                break
    
    # Print grouped errors with random examples
    if error_examples:
        print("\n" + "="*80)
        print("ERROR SUMMARY BY TYPE")
        print("="*80)
        
        for error_type, examples in error_examples.items():
            print(f"\n{error_type} ({len(examples)} occurrences):")
            print("-" * (len(error_type) + 20))
            
            # Show up to 10 random examples
            sample_size = min(10, len(examples))
            sample_examples = random.sample(examples, sample_size) if len(examples) > 10 else examples
            
            for row_num, address, error_msg in sample_examples:
                print(f"  Row {row_num}: {address}")
                print(f"    → {error_msg}")
            
            if len(examples) > 10:
                print(f"    ... and {len(examples) - 10} more similar errors")
    
    # Check if we stopped early
    if error_count >= max_errors:
        print(f"\n⚠️  Processing stopped early after reaching {max_errors} errors")
    
    # Print summary
    total = success_count + error_count + copy_count + validation_error_count
    if total > 0:
        print(f"\n{'='*80}")
        print("PROCESSING SUMMARY")
        print("="*80)
        print(f"Total processed: {total} addresses")
        print(f"✅ Successfully converted: {success_count}")
        print(f"📋 Copied (no changes): {copy_count}")
        print(f"❌ Errors: {error_count}")
        print(f"⚠️  Validation failures: {validation_error_count}")
        
        if error_examples:
            print(f"\nError types found: {len(error_examples)}")
            for error_type, examples in error_examples.items():
                print(f"  • {error_type}: {len(examples)} cases")


if __name__ == "__main__":
    csv_file = "tests/tests.csv"
    max_errors = 1000000
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            max_errors = int(sys.argv[2])
        except ValueError:
            print(f"Error: max_errors must be an integer, got '{sys.argv[2]}'")
            sys.exit(1)
    
    print(f"Processing CSV file: {csv_file}")
    print(f"Max errors before stopping: {max_errors}")
    print()
    
    process_csv_file(csv_file, max_errors)
