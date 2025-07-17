# Makefile for vn-address-converter package

# Package name
PACKAGE_NAME = vn-address-converter
PYTHON = python3
PIP = pip3

# Directories
SRC_DIR = vn_address_converter
DIST_DIR = dist
BUILD_DIR = build
TEST_DIR = tests

# Colors for output
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m # No Color

.PHONY: help clean install install-dev test lint format type-check build upload upload-test version bump-patch bump-minor bump-major

# Default target
help:
	@echo "$(GREEN)Available targets:$(NC)"
	@echo "  $(YELLOW)help$(NC)          - Show this help message"
	@echo "  $(YELLOW)clean$(NC)         - Clean build artifacts"
	@echo "  $(YELLOW)install$(NC)       - Install package in development mode"
	@echo "  $(YELLOW)install-dev$(NC)   - Install package with development dependencies"
	@echo "  $(YELLOW)test$(NC)          - Run tests"
	@echo "  $(YELLOW)lint$(NC)          - Run linting (flake8)"
	@echo "  $(YELLOW)format$(NC)        - Format code with black"
	@echo "  $(YELLOW)type-check$(NC)    - Run type checking with mypy"
	@echo "  $(YELLOW)check-all$(NC)     - Run all checks (lint, type-check, test)"
	@echo "  $(YELLOW)build$(NC)         - Build package"
	@echo "  $(YELLOW)upload$(NC)        - Upload package to PyPI"
	@echo "  $(YELLOW)upload-test$(NC)   - Upload package to Test PyPI"
	@echo "  $(YELLOW)version$(NC)       - Show current version"
	@echo "  $(YELLOW)bump-patch$(NC)    - Bump patch version"
	@echo "  $(YELLOW)bump-minor$(NC)    - Bump minor version"
	@echo "  $(YELLOW)bump-major$(NC)    - Bump major version"

# Clean build artifacts
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -rf $(DIST_DIR)
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	@echo "$(GREEN)Clean completed!$(NC)"

# Install package in development mode
install:
	@echo "$(GREEN)Installing package in development mode...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)Installation completed!$(NC)"

# Install package with development dependencies
install-dev:
	@echo "$(GREEN)Installing package with development dependencies...$(NC)"
	$(PIP) install -e .[dev]
	@echo "$(GREEN)Development installation completed!$(NC)"

# Create tests directory if it doesn't exist
$(TEST_DIR):
	@mkdir -p $(TEST_DIR)
	@touch $(TEST_DIR)/__init__.py

# Run tests
test: $(TEST_DIR)
	@echo "$(GREEN)Running tests...$(NC)"
	pytest $(TEST_DIR) -v;

streamlit:
	@echo "$(GREEN)Running Streamlit app...$(NC)"
	streamlit run streamlit_app.py

# Run linting
lint:
	@echo "$(GREEN)Running linting...$(NC)"
	flake8 $(SRC_DIR) --max-line-length=88 --extend-ignore=E203,W503

# Format code
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	black $(SRC_DIR)
	@echo "$(GREEN)Code formatting completed!$(NC)"

# Run type checking
type-check:
	@echo "$(GREEN)Running type checking...$(NC)"
	mypy $(SRC_DIR)

# Run all checks
check-all: lint type-check test
	@echo "$(GREEN)All checks completed!$(NC)"

# Build package
build: clean
	@echo "$(GREEN)Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Build completed! Files in $(DIST_DIR):$(NC)"
	@ls -la $(DIST_DIR)

# Upload to PyPI
upload: build
	@echo "$(GREEN)Uploading to PyPI...$(NC)"
	@echo "$(YELLOW)Warning: This will upload to the real PyPI!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	twine upload $(DIST_DIR)/*
	@echo "$(GREEN)Upload completed!$(NC)"

# Upload to Test PyPI
upload-test: build
	@echo "$(GREEN)Uploading to Test PyPI...$(NC)"
	twine upload --repository testpypi $(DIST_DIR)/*
	@echo "$(GREEN)Test upload completed!$(NC)"

# Show current version
version:
	@echo "$(GREEN)Current version:$(NC)"
	@$(PYTHON) -c "import vn_address_converter; print(vn_address_converter.__version__)"

# Bump patch version (0.1.0 -> 0.1.1)
bump-patch:
	@echo "$(GREEN)Bumping patch version...$(NC)"
	@$(PYTHON) -c "import re; \
	content = open('$(SRC_DIR)/__init__.py').read(); \
	version_match = re.search(r'__version__ = \"(\d+)\.(\d+)\.(\d+)\"', content); \
	if version_match: \
		major, minor, patch = version_match.groups(); \
		new_version = f'{major}.{minor}.{int(patch)+1}'; \
		new_content = re.sub(r'__version__ = \"[\d\.]+\"', f'__version__ = \"{new_version}\"', content); \
		open('$(SRC_DIR)/__init__.py', 'w').write(new_content); \
		print(f'Version bumped to {new_version}'); \
	else: \
		print('Version not found')"

# Bump minor version (0.1.0 -> 0.2.0)
bump-minor:
	@echo "$(GREEN)Bumping minor version...$(NC)"
	@$(PYTHON) -c "import re; \
	content = open('$(SRC_DIR)/__init__.py').read(); \
	version_match = re.search(r'__version__ = \"(\d+)\.(\d+)\.(\d+)\"', content); \
	if version_match: \
		major, minor, patch = version_match.groups(); \
		new_version = f'{major}.{int(minor)+1}.0'; \
		new_content = re.sub(r'__version__ = \"[\d\.]+\"', f'__version__ = \"{new_version}\"', content); \
		open('$(SRC_DIR)/__init__.py', 'w').write(new_content); \
		print(f'Version bumped to {new_version}'); \
	else: \
		print('Version not found')"

# Bump major version (0.1.0 -> 1.0.0)
bump-major:
	@echo "$(GREEN)Bumping major version...$(NC)"
	@$(PYTHON) -c "import re; \
	content = open('$(SRC_DIR)/__init__.py').read(); \
	version_match = re.search(r'__version__ = \"(\d+)\.(\d+)\.(\d+)\"', content); \
	if version_match: \
		major, minor, patch = version_match.groups(); \
		new_version = f'{int(major)+1}.0.0'; \
		new_content = re.sub(r'__version__ = \"[\d\.]+\"', f'__version__ = \"{new_version}\"', content); \
		open('$(SRC_DIR)/__init__.py', 'w').write(new_content); \
		print(f'Version bumped to {new_version}'); \
	else: \
		print('Version not found')"

# Install required build tools
install-build-tools:
	@echo "$(GREEN)Installing build tools...$(NC)"
	$(PIP) install build twine
	@echo "$(GREEN)Build tools installed!$(NC)"

# Full development setup
setup-dev: install-build-tools install-dev
	@echo "$(GREEN)Development environment setup completed!$(NC)"
	@echo "$(YELLOW)Available commands:$(NC)"
	@make help
