# 🧪 Testing for Local Environment

This directory contains tests for the local environment components of the Job Analytics Platform.

## 📋 Test Structure

- `conftest.py` - Shared test fixtures and configuration
- `test_*.py` - Test modules for various components

## 🔍 Running Tests

Run all tests:

```bash
cd 01_local
pytest tests/
```

Run specific test modules:

```bash
cd 01_local
pytest tests/test_dlt_pipeline.py
pytest tests/test_data_saver.py
```

Run tests with coverage report:

```bash
cd 01_local
pytest tests/ --cov=src --cov-report=term-missing
```

## 🚀 Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **Data Quality Tests**: Validate data transformations and schema compliance

## 📊 Test Coverage

- Aim for at least 80% coverage for critical components

## 🧹 Codebase Consolidation Checklist

- [ ] Remove duplicate or outdated tests
- [ ] Ensure all tests have docstrings and clear names
- [ ] Add/Update fixtures as needed

---

See the README.md in `src/` for details on the code being tested.
