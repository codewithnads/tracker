# Tracker API Testing Guide

## Running Tests

### All Tests
```bash
pytest test_app.py -v
```

### With Coverage Report
```bash
pytest test_app.py --cov=app --cov=fb_manager --cov=formatter --cov-report=html
```

### Specific Test Class
```bash
pytest test_app.py::TestRootEndpoint -v
```

### Specific Test
```bash
pytest test_app.py::TestRootEndpoint::test_root_endpoint_returns_200 -v
```

## Test Structure

### 1. **TestRootEndpoint**
   - Tests GET / endpoint
   - Validates JSON response
   - Checks endpoint listing

### 2. **TestWakeEndpoint**
   - Tests GET /wake-up endpoint
   - Validates success message

### 3. **TestRecordsEndpoint**
   - Tests GET /records with valid/invalid auth
   - Tests authentication headers

### 4. **TestUpdateRecordsEndpoint**
   - Tests POST /update-records
   - Tests success/failure scenarios
   - Tests default user handling

### 5. **TestAddRecordEndpoint**
   - Tests POST /add-record
   - Tests record skipping logic

### 6. **TestAPIDocumentation**
   - Tests /apidocs endpoint availability

### 7. **TestErrorHandling**
   - Tests 404 errors
   - Tests method not allowed (405)

### 8. **TestCORS**
   - Tests CORS headers

## Coverage Report

Current coverage:
- **app.py**: 61%
- **fb_manager.py**: 25%
- **formatter.py**: 4%
- **Overall**: 21%

To improve coverage:
1. Add more integration tests with real Firebase connections
2. Test error handling in fb_manager functions
3. Test all formatter edge cases

## Manual API Testing

### Root Endpoint
```bash
curl http://localhost:5000/
```

### Wake Endpoint
```bash
curl http://localhost:5000/wake-up
```

### Records (requires auth)
```bash
curl "http://localhost:5000/records?uname=nam&key=271016" \
  -H "user: YourUsername"
```

### Add Record
```bash
curl -X POST http://localhost:5000/add-record \
  -H "Content-Type: application/json" \
  -H "user: YourUsername" \
  -d '{"address": "+1234567890", "body": "Test message"}'
```

### Update Records
```bash
curl -X POST http://localhost:5000/update-records \
  -H "Content-Type: application/json" \
  -H "user: YourUsername" \
  -d '{"Bank~Account~Key": {"amount": 1000}}'
```

## CI/CD Integration

This test suite can be integrated with GitHub Actions:

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest test_app.py -v --cov=app
```
