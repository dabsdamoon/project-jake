# JAKE Test Suite

This directory contains all test files for the JAKE system.

## Test Files

### 1. test_jake.py
**Purpose**: Unit tests for individual JAKE components
**Requirements**: Python, JAKE dependencies
**Server Required**: ❌ No

Tests individual agents directly without requiring the API server:
- JAKECreator - Character generation
- JAKEChatter - Conversation handling
- JAKEChecker - Quest validation
- JAKESummarizer - Memory extraction
- JAKEOrchestrator - Full workflow

**Run directly:**
```bash
python tests/test_jake.py
```

### 2. test_api_simple.sh
**Purpose**: API endpoint integration tests
**Requirements**: bash, curl, jq
**Server Required**: ✅ Yes

Shell-based tests for all 9 API endpoints with fail-fast error handling:
- Health check
- Character creation & retrieval
- Chat functionality (first message & continuation)
- Quest management (create & list)
- Conversation history
- User character listing

**Run directly:**
```bash
./tests/test_api_simple.sh [PORT]
```

## Running All Tests

Use the unified test runner in the project root:

```bash
# Run all tests (requires API server running)
./run_tests.sh

# Run on custom port
./run_tests.sh 8001

# Run only unit tests (no API server needed)
./run_tests.sh --unit-only

# Run only API tests (requires server)
./run_tests.sh --api-only

# Show help
./run_tests.sh --help
```

## Test Execution Order

The unified test runner (`run_tests.sh`) executes tests in this order:

1. **Unit Tests** - Tests individual components without API server
2. **API Health Check** - Verifies server is running
3. **API Endpoint Tests** - Validates all 9 endpoints

## CI/CD Integration

For continuous integration pipelines:

```bash
# In your CI config
./start_server.sh &          # Start server in background
sleep 10                      # Wait for startup
./run_tests.sh               # Run all tests
```

## Test Requirements

**For Unit Tests:**
- Python 3.11+
- JAKE dependencies (from environment.yml)
- OpenAI API key in .env

**For API Tests:**
- All unit test requirements
- Running JAKE API server
- curl and jq (for shell script)
