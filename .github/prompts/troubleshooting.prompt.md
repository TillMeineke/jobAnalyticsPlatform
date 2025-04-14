# Troubleshooting Guide

This guide contains common errors encountered during development and their solutions.

## Environment Setup

### Python Dependencies

**Error**: Module not found errors (e.g., `ModuleNotFoundError: No module named 'selenium'`)

**Solution**:

```bash
pip install -r requirements.txt
```

### Webdriver Issues

**Error**: Webdriver executable not found or Firefox/Gecko not installed

**Solution**:

1. Ensure Firefox is installed on your system
2. Install the geckodriver:

   ```bash
   pip install webdriver-manager
   ```

   This package will handle downloading the appropriate geckodriver version.

## Selenium Troubleshooting

### Browser Selection

- **Chrome**: Uses `webdriver.Chrome()` with the ChromeDriverManager
- **Firefox**: Uses `webdriver.Firefox()` with the GeckoDriverManager
- **Safari**: Only works on macOS and requires enabling developer mode
- **Edge**: Uses `webdriver.Edge()` with EdgeDriverManager

### Common Selenium Errors

**Error**: `ElementNotInteractableException`

**Solution**: Use WebDriverWait to ensure element is ready before interacting:

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

element = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "my-element"))
)
element.click()
```

**Error**: `StaleElementReferenceException`

**Solution**: Re-locate the element after page changes:

```python
def safe_click(driver, element_finder, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            element = element_finder()
            element.click()
            return True
        except StaleElementReferenceException:
            if attempt == max_attempts - 1:
                raise
```

## Docker Issues

**Error**: Cannot connect to the Docker daemon

**Solution**:

```bash
# Check if Docker is running
docker info

# If not running, start Docker:
# On Mac/Windows: Start Docker Desktop
# On Linux:
sudo systemctl start docker
```

## Database Issues

**Error**: Cannot connect to PostgreSQL database

**Solution**:

```bash
# Check if PostgreSQL container is running
docker ps | grep postgres

# If not listed, start the services:
cd 01_local
docker-compose up -d
```

## Path/Import Issues

**Error**: Module import errors despite files existing

**Solution**: Make sure the package structure is properly set up with `__init__.py` files and run from the project root:

```bash
# Run scripts from project root
cd /path/to/jobAnalyticsPlatform
python -m src.tests.test_stepstone_scraper
```

## Testing

**Error**: Tests failing with unexpected errors

**Solution**: Use verbose mode to see more details:

```bash
pytest -v src/tests/test_stepstone_scraper.py
```
