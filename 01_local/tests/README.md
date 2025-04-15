# 🧪 Tests

This directory contains tests for the Job Analytics Platform.

## 📂 Test Organization

```
tests/
├── unit/                  # Unit tests
│   ├── scrapers/         # Scraper component tests
│   ├── transformers/     # Data transformation tests
│   └── validators/       # Data validation tests
├── integration/          # Integration tests
│   ├── pipeline/        # End-to-end pipeline tests
│   └── api/            # API endpoint tests
└── data/               # Test data fixtures
```

## 🚀 Running Tests

```bash
cd 01_local
make test              # Run all tests
make test-unit        # Run only unit tests
make test-integration # Run only integration tests
```

## 📊 Test Coverage

Coverage reports are generated in `coverage/` directory.

## 🔍 Test Patterns

### Unit Tests

- One test file per source file
- Use fixtures for input data
- Mock external dependencies

### Integration Tests

- Test complete data flows
- Validate data quality
- Check pipeline metrics

## 📈 Quality Metrics

- Unit test coverage: >80%
- Integration test coverage: >60%
- Max test duration: 5 minutes
