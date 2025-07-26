#!/usr/bin/env python3
"""
Simple command-line script to convert Vietnamese addresses from old to new format.
Usage: python convert_address.py "old address string"
"""

import sys
from vn_address_converter import convert_to_new_address

def main():
    if len(sys.argv) != 2:
        print("Usage: python convert_address.py \"address string\"")
        sys.exit(1)
    
    old_address = sys.argv[1]
    
    try:
        new_address = convert_to_new_address(old_address)
        print(new_address.format())
    except Exception as e:
        print(f"Error converting address: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()