# 🧪 Testing for Cloud Environment

This directory contains tests for the cloud environment components of the Job Analytics Platform.

## 📋 Test Structure

- `conftest.py` - Shared test fixtures and configuration
- `test_*.py` - Test modules for various cloud components

## 🔍 Running Tests

You can run the tests using the following commands:

```bash
# Run all tests
cd 02_cloud
pytest tests/

# Run specific test categories with markers
pytest tests/ -m "aws"
pytest tests/ -m "infrastructure"

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

## 🚀 Test Categories

- **AWS Tests**: Test AWS service interactions
- **Infrastructure Tests**: Test Terraform deployments
- **Integration Tests**: Test cloud component interactions
- **Pipeline Tests**: Test cloud data pipeline operations

## 📊 Test Coverage Goals

The goal is to maintain at least 80% test coverage for critical cloud components:

- AWS resource provisioning
- Cloud pipeline components
- Infrastructure-as-code

## 📘 Writing Tests for Cloud Components

When adding new cloud components, please include corresponding test files following these guidelines:

1. Use mocks for AWS services where appropriate
2. Include thorough testing of IAM policies and permissions
3. Test error handling for network issues
4. Use localstack for local AWS emulation when possible
5. Ensure tests can run in CI/CD environment without AWS credentials
