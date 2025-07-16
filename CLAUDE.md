# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Vietnam Address Converter is a Python package that converts old Vietnamese addresses to the new administrative format following Vietnam's 2024-2025 administrative reform where 63 provinces were merged into 34. The package provides address normalization and conversion functionality with comprehensive mapping data.

## Development Commands

### Package Management
- `make install-dev` - Install package with development dependencies
- `make install` - Install package in development mode
- `make setup-dev` - Full development environment setup

### Code Quality
- `make lint` - Run flake8 linting (max line length 88)
- `make format` - Format code with black
- `make type-check` - Run mypy type checking
- `make check-all` - Run all quality checks (lint, type-check, test)

### Testing
- `make test` - Run pytest tests with coverage
- `pytest tests/` - Run tests directly
- `pytest tests/ -v` - Run tests with verbose output
- `pytest tests/ -m "not slow"` - Skip slow tests

### Building and Distribution
- `make build` - Build package for distribution
- `make clean` - Clean build artifacts
- `make version` - Show current version

### Alternative Commands
- `python -m build` - Build package
- `flake8 vn_address_converter --max-line-length=88 --extend-ignore=E203,W503`
- `black vn_address_converter`
- `mypy vn_address_converter`

## Code Architecture

### Core Components

**vn_address_converter/converter.py** - Main conversion logic
- `Address` TypedDict: Represents Vietnamese addresses with optional fields
- `AddressLevel` Enum: Defines administrative levels (province, district, ward)
- `convert_to_new_address()`: Main conversion function that maps old addresses to new format
- `normalize_alias()`: Normalizes address component names by removing prefixes
- `_get_ward_mapping()`: Loads and caches mapping data with normalized aliases

**vn_address_converter/data/ward_mapping.json** - Complete mapping data from old to new administrative divisions

### Data Processing Pipeline

**pipelines/** directory contains data extraction and processing scripts from the original development (historical):
- `extract_tables.py` - Extracts mapping data from HTML tables
- `llm_table_extractor.py` - Uses LLM to process table data
- `convert_to_new_format.py` - Converts extracted data to final format

### Key Design Patterns

1. **Lazy Loading**: Ward mapping data is loaded once and cached globally in `WARD_MAPPING`
2. **Normalization**: Address components are normalized by removing administrative prefixes (e.g., "Phường", "Quận") using `normalize_alias()`
3. **Alias Mapping**: Multiple normalized forms are stored for fuzzy matching (original name + normalized alias)
4. **Error Handling**: Raises ValueError for unmapped addresses with specific error messages

### Testing Strategy

Tests use parametrized pytest with real-world address examples covering:
- Case-insensitive matching
- Alias resolution
- Edge cases from different provinces
- Both formal and informal address formats
- Error handling for missing/invalid addresses

## Important Notes

- The main converter file has a typo in the filename (`convereter.py` instead of `converter.py`)
- The package uses TypedDict for type safety without runtime overhead
- All mapping data is stored in JSON format for easy updates
- The converter returns `district=None` as districts are eliminated in the new format
- Coverage target is set to 80% minimum
- The mapping data structure has a typo in the JSON key: `new_provine_name` instead of `new_province_name`