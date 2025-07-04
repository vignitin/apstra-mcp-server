# Apstra MCP Server - Testing Guide

## Overview

This document describes the comprehensive testing framework for the Apstra MCP Server blueprint creation functionality, including automatic cleanup mechanisms to prevent test blueprint accumulation.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_config.py             # Test configuration and constants
├── test_unit.py               # Unit tests with mocked dependencies
├── test_functional.py         # Functional tests against real server
├── test_cleanup.py            # Standalone cleanup utility
└── run_tests.py               # Test runner with auto-cleanup
```

## Test Types

### 1. Unit Tests (`test_unit.py`)
- **Mock-based testing** - No real server calls
- Tests all blueprint creation functions with mocked responses
- Fast execution, no cleanup required
- **Coverage:**
  - Authentication success/failure
  - Template retrieval
  - Datacenter blueprint creation
  - Freeform blueprint creation
  - Blueprint deletion
  - Blueprint listing

### 2. Functional Tests (`test_functional.py`)
- **Real server integration** - Tests against 10.87.2.74
- End-to-end blueprint lifecycle testing
- **Automatic cleanup** at multiple levels
- **Coverage:**
  - Real authentication
  - Real blueprint creation
  - Real blueprint deletion
  - End-to-end lifecycle

## Cleanup Mechanisms

### 1. Individual Test Cleanup
```python
def tearDown(self):
    """Clean up after each test"""
    if hasattr(self, 'test_blueprints_created') and self.test_blueprints_created:
        for bp_id in self.test_blueprints_created:
            delete_blueprint(bp_id, self.test_server)
```

### 2. Class-Level Cleanup
```python
@classmethod
def tearDownClass(cls):
    """Clean up created blueprints after all tests"""
    # Clean up tracked blueprints + scan for additional test blueprints
```

### 3. Pattern-Based Cleanup
Automatically removes blueprints containing:
- `test-*`
- `demo-*`  
- `e2e-test*`
- `unittest-*`
- `functional-*`

### 4. Pre/Post Test Cleanup
The test runner performs cleanup before and after test execution.

## Running Tests

### Using Test Management Script
```bash
# Run all tests with cleanup
python test.py run

# Run specific test types
python test.py unit
python test.py functional

# Manual cleanup
python test.py clean

# Run demo
python test.py demo
```

### Direct Test Execution
```bash
# All tests with automatic cleanup
python tests/run_tests.py

# Unit tests only
python -m unittest tests.test_unit -v

# Functional tests only  
python -m unittest tests.test_functional -v

# Manual cleanup
python tests/test_cleanup.py
```

## Cleanup Utility Features

### Automatic Detection
- Scans all blueprints on server
- Identifies test blueprints by naming patterns
- Safe - only removes blueprints with test keywords

### Manual Pattern Cleanup
```bash
python tests/test_cleanup.py --pattern "specific-pattern"
```

### Force Cleanup
```bash
python tests/test_cleanup.py --force
```

## Test Configuration

### Server Settings (`test_config.py`)
```python
TEST_SERVER = "10.87.2.74"
TEST_USERNAME = "admin" 
TEST_PASSWORD = "Apstramarvis@123"
```

### Blueprint Naming
- Test blueprints use timestamped names
- Pattern: `test-{type}-{timestamp}`
- Examples: `test-datacenter-1751648231`, `e2e-test-1751648173`

## Safety Features

1. **Authentication Check** - Tests skip if server unreachable
2. **Blueprint Tracking** - Multiple tracking mechanisms for cleanup
3. **Pattern Matching** - Only removes blueprints with test keywords
4. **Error Handling** - Graceful failure if cleanup fails
5. **Verification** - Post-cleanup verification of removal

## Test Results Interpretation

### Expected Results
- **Unit Tests**: Should always pass (mocked)
- **Functional Tests**: 
  - ✅ Datacenter blueprint creation: PASS
  - ⚠️ Freeform blueprint creation: SKIP (version dependent)
  - ✅ Authentication, templates, deletion: PASS

### Cleanup Success Indicators
```
✓ Deleted tracked blueprint {id}
✓ All test blueprints successfully removed!
✓ Post-test cleanup completed successfully
```

## Troubleshooting

### If Tests Fail to Clean Up
1. Run manual cleanup: `python test.py clean`
2. Check server connectivity
3. Verify authentication credentials
4. Use force cleanup for specific patterns

### If Server Has Leftover Test Blueprints
```bash
# List all blueprints to identify test ones
python -c "from apstra_core import get_bp; print(get_bp())"

# Force cleanup specific pattern
python tests/test_cleanup.py --pattern "test-"
```

### Common Issues
1. **Network timeout**: Increase timeout in test_config.py
2. **Authentication failure**: Check credentials in test_config.py
3. **Blueprint stuck**: May need manual deletion via GUI

## Best Practices

1. **Always run cleanup** after manual testing
2. **Use timestamped names** for any manual test blueprints
3. **Include test keywords** in blueprint names for auto-cleanup
4. **Run pre-test cleanup** before important test sessions
5. **Monitor server state** regularly to prevent accumulation

## Integration with CI/CD

The test suite is designed for automated environments:
- Automatic pre/post cleanup
- Clear success/failure indicators  
- Safe cleanup patterns
- No manual intervention required

```bash
# CI/CD friendly command
python tests/run_tests.py && echo "Tests completed with cleanup"
```