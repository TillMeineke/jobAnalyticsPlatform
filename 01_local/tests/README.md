# 🧪 Testing for Local Environment

This directory contains tests for the local environment components of the Job Analytics Platform.

## 📋 Test Structure

- `conftest.py` - Shared test fixtures and configuration
- `test_*.py` - Test modules for various components

## 🔍 Running Tests

You can run the tests using the following commands:

```bash
# Run all tests
cd 01_local
pytest tests/

# Run specific test modules
pytest tests/test_dlt_pipeline.py
pytest tests/test_data_saver.py

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

## 🚀 Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **Data Quality Tests**: Validate data transformations and schema compliance

## 📊 Test Coverage

The goal is to maintain at least 80% test coverage for critical components:

- Data scrapers
- Pipeline components
- Data transformations

## 📘 Writing Tests

When adding new components, please include corresponding test files following these guidelines:

1. Use descriptive test function names
2. Include docstrings explaining the test purpose
3. Arrange tests in logical sections
4. Use appropriate fixtures from `conftest.py`
5. Mock external dependencies when needed
