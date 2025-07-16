# TODO: Additional Functions for VN Address Converter

## Address Validation & Verification
- [ ] `validate_address()` - Verify address components exist in mapping data
- [ ] `get_address_suggestions()` - Return similar addresses when exact match fails
- [ ] `is_valid_address()` - Boolean check for address validity

## Batch Processing
- [ ] `convert_addresses_batch()` - Process multiple addresses efficiently
- [ ] `convert_from_csv()` - Read/write CSV files with address conversion
- [ ] `convert_from_json()` - Handle JSON input/output

## Geographic & Administrative Utilities
- [ ] `list_provinces()` - Get all available provinces
- [ ] `list_districts_by_province()` - Get districts for a province
- [ ] `list_wards_by_district()` - Get wards for a district
- [ ] `get_address_hierarchy()` - Return full administrative structure

## Reverse Lookup & Search
- [ ] `find_old_address()` - Convert new format back to old format
- [ ] `search_addresses()` - Fuzzy search for addresses
- [ ] `get_address_history()` - Show conversion mapping details

## Format & Export Options
- [ ] `format_address()` - Format address for display (single line, multi-line)
- [ ] `export_mapping_data()` - Export current mapping as CSV/JSON
- [ ] `get_conversion_stats()` - Statistics about conversions performed

## Priority Recommendations
**High Priority:**
- Address validation functions
- Batch processing capabilities

**Medium Priority:**
- Geographic utilities
- Format & export options

**Low Priority:**
- Reverse lookup functions
- Search capabilities