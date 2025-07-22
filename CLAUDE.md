# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vietnam Address Converter is a Python package that converts old Vietnamese addresses to the new administrative format following Vietnam's 2024-2025 administrative reform where 63 provinces were merged into 34. The package provides address normalization and conversion functionality with comprehensive mapping data.

## Development Commands

### Package Management
- `make install-dev` - Install package with development dependencies
- `make install` - Install package in development mode
- `make setup-dev` - Full development environment setup

### Testing
- `make test` - Run pytest tests with coverage
- `pytest tests/` - Run tests directly
- `pytest tests/ -v` - Run tests with verbose output
- `pytest tests/ -m "not slow"` - Skip slow tests
- `pytest tests/test_basic.py::test_convert_address_table -k "address2" -v` - Run specific test

### Code Quality
- `make lint` - Run flake8 linting
- `make format` - Format code with black
- `make type-check` - Run mypy type checking
- `make check-all` - Run all checks (lint, type-check, test)

### Building and Distribution
- `make build` - Build package for distribution
- `make clean` - Clean build artifacts
- `make version` - Show current version

## Code Architecture

### Object-Oriented Mapping System

The core architecture uses a layered object-oriented approach for address mapping:

**vn_address_converter/mapping.py** - Mapping classes and database
- `AdministrativeDatabase`: Singleton database with lazy loading of mapping data
- `ProvinceMapping`: Encapsulates province data and district lookup methods
- `DistrictMapping`: Encapsulates district data and ward lookup methods  
- `WardMapping`: Encapsulates ward data with conversion methods (`get_new_province()`, `get_new_ward()`)

**Lookup Chain Pattern**:
```python
db = get_administrative_database()                    # Singleton instance
province_map = db.lookup_province(province)           # Returns ProvinceMapping
district_map = province_map.lookup_district(district) # Returns DistrictMapping  
ward_map = district_map.lookup_ward(ward)             # Returns WardMapping
new_province = ward_map.get_new_province()            # Conversion method
new_ward = ward_map.get_new_ward()                    # Conversion method
```

### Core Components

**vn_address_converter/models.py** - Data models
- `Address` dataclass: Represents Vietnamese addresses with optional fields and `format()` method
- `AddressLevel` Enum: Defines administrative levels (province, district, ward)
- `MappingMissingError`: Custom exception for missing mappings with specific error messages

**vn_address_converter/converter.py** - Main conversion logic
- `convert_to_new_address()`: Main conversion function using the object-oriented lookup chain
- Uses the administrative database singleton for efficient mapping access

**vn_address_converter/parser.py** - Address parsing
- `parse_address()`: Parses address strings with support for multiple separators (comma, semicolon, pipe, hyphen)
- Context-aware component type detection

**vn_address_converter/aliases.py** - Address normalization
- `normalize_alias()`: Normalizes address component names by removing prefixes
- `get_aliases()`: Generates multiple normalized forms for fuzzy matching

**vn_address_converter/data/** - Mapping data
- `ward_mapping.json`: Complete hierarchical mapping from old to new administrative divisions
- `manual_aliases.json`: Additional manual aliases for edge cases

### Key Design Patterns

1. **Lazy Loading with Singleton**: Mapping data loaded once and cached in `AdministrativeDatabase` singleton
2. **Object-Oriented Encapsulation**: Each administrative level (province/district/ward) is its own class with specific methods
3. **Hierarchical Lookup Chain**: Natural progression from province → district → ward with type safety
4. **Alias Resolution**: Multiple normalized forms stored for fuzzy matching (original name + normalized alias)
5. **Backward Compatibility**: All mapping classes implement `__getitem__` and `__contains__` for dict-like access
6. **Legacy Mapping Support**: Special handling for `legacy_district_mapping` in province data

### Data Flow Architecture

1. **Input**: Raw address string or `Address` object
2. **Parsing**: Address string parsed into components using context-aware detection
3. **Normalization**: Components normalized by removing administrative prefixes
4. **Hierarchical Lookup**: Province → District → Ward using object chain
5. **Alias Resolution**: Multiple alias types (automatic + manual) for flexible matching
6. **Conversion**: Ward mapping provides new province and ward names
7. **Output**: New `Address` object with `district=None` (eliminated in reform)

### Testing Strategy

Tests use parametrized pytest with real-world address examples covering:
- Case-insensitive matching and alias resolution
- Edge cases from different provinces and non-standard formats
- Different separators (semicolon, pipe, hyphen) with automatic detection
- Error handling for missing/invalid addresses at each administrative level
- Backward compatibility with dict-like access patterns

## Important Notes

- The mapping data has a legacy typo: `new_provine_name` instead of `new_province_name`
- Districts are eliminated in the new format, so converted addresses always have `district=None`
- The `AdministrativeDatabase` is a singleton accessed via `get_administrative_database()`
- All mapping classes provide backward compatibility through `__getitem__` and `__contains__`
- Coverage target is 80% minimum with HTML and XML reports generated
- Use pytest markers: `slow`, `integration`, `unit`, `performance`