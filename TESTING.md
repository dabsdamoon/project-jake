# JAKE Testing Guide

Quick reference for testing the JAKE system.

## 🚀 Quick Start

### Run All Tests (Recommended)

```bash
# 1. Start the server
./start_server.sh

# 2. In another terminal, run all tests
./run_tests.sh
```

That's it! The unified test runner will:
1. Run unit tests (individual components)
2. Check if API server is running
3. Run API endpoint tests (all 9 endpoints)

## 📋 Test Options

```bash
# Run all tests (default)
./run_tests.sh

# Run only unit tests (no server needed)
./run_tests.sh --unit-only

# Run only API tests (requires server)
./run_tests.sh --api-only

# Run on custom port
./run_tests.sh 8001

# Show help
./run_tests.sh --help
```

## 🧪 Individual Test Scripts

All test scripts are in the `tests/` directory:

### 1. Unit Tests
```bash
python tests/test_jake.py
```
- Tests individual agents
- No API server required
- Fast execution

### 2. API Endpoint Tests
```bash
./tests/test_api_simple.sh [PORT]
```
- Tests all 9 API endpoints
- Requires: curl, jq
- Fails fast on errors

## 📊 Expected Results

### Successful Test Run
```
================================================================
                    JAKE TEST SUITE
================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 1: Unit Tests (Testing Individual Components)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Running unit tests with tests/test_jake.py...
✓ Unit tests passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 2: API Server Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ API server is running and healthy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Step 3: API Endpoint Tests
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ API endpoint tests passed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Test Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Results:
  Total Tests: 3
  Passed: 3
  Failed: 0

================================================================
  🎉 ALL TESTS PASSED! JAKE is working perfectly!
================================================================
```

## 🔧 Troubleshooting

### Server Not Running
```bash
# Error: API server is not responding

# Solution:
./start_server.sh
```

### Port Already in Use
```bash
# Use a different port
./start_server.sh 8001
./run_tests.sh 8001
```

### Missing Dependencies
```bash
# For jq (required by shell tests)
brew install jq  # macOS
apt-get install jq  # Linux

# For Python dependencies
conda env update -f environment.yml
```

## 📖 More Information

- **Detailed Testing Guide**: [documentation/API_TESTING.md](./documentation/API_TESTING.md)
- **Test Scripts Documentation**: [tests/README.md](./tests/README.md)
- **Getting Started**: [documentation/GETTING_STARTED.md](./documentation/GETTING_STARTED.md)

## 🎯 CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run JAKE Tests
  run: |
    ./start_server.sh &
    sleep 10
    ./run_tests.sh
```

## 💡 Tips

- Run `./run_tests.sh --unit-only` during development (faster, no server needed)
- Use `./run_tests.sh --api-only` when testing API changes
- Individual test scripts are in `tests/` directory
- All tests exit with proper status codes for CI/CD integration
