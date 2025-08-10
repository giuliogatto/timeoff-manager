# Backend Tests

This directory contains comprehensive tests for the Timeoff Manager backend API.

## 🧪 Test Coverage

### ✅ **Working Tests (28/38 - 74%)**

#### **Authentication Tests** ✅
- User registration (success, duplicate email)
- User login (success, invalid credentials, unvalidated account)
- Account confirmation (success, invalid token, already validated)

#### **Main Application Tests** ✅
- Root endpoint
- Health check
- API documentation endpoints

#### **Profile Tests** ✅
- Get profile (unauthorized, success, manager)

#### **Leave Requests Tests** ✅
- Get leave requests (unauthorized, user view, manager view)
- Create timeoff request
- Create request (unauthorized, invalid type)
- Update request status (unauthorized, not manager, invalid status, not found, already processed)

### ❌ **Failing Tests (10/38 - 26%)**

#### **Google OAuth Tests** ❌
- All Google OAuth tests are failing due to environment variable handling issues
- These tests require proper mocking of external Google API calls

#### **Leave Requests Tests** ❌
- Create permission request (datetime validation issue)
- Missing dates/datetimes validation (status code mismatch)
- Update request status manager (ID mismatch in test)

## 🚀 Running Tests

### Quick Tests (No Coverage)
```bash
cd backend
./run_tests_quick.sh
```

### Full Tests with Coverage
```bash
cd backend
./run_tests.sh
```

### Individual Test Files
```bash
# Authentication tests
docker exec timeoff-manager-api python -m pytest tests/test_authentication.py -v

# Leave requests tests
docker exec timeoff-manager-api python -m pytest tests/test_leave_requests.py -v

# Profile tests
docker exec timeoff-manager-api python -m pytest tests/test_profile.py -v

# Main application tests
docker exec timeoff-manager-api python -m pytest tests/test_main.py -v
```

### Specific Test
```bash
docker exec timeoff-manager-api python -m pytest tests/test_authentication.py::TestAuthentication::test_login_success -v
```

## 🏗️ Test Architecture

### **Test Database**
- Uses SQLite in-memory database for fast, isolated tests
- Each test gets a fresh database session
- Tables are created and destroyed for each test

### **Authentication**
- Custom test middleware that uses the test database session
- JWT tokens are generated for test users
- Separate fixtures for regular users and managers

### **Fixtures**
- `db_session`: Fresh database session for each test
- `client`: Test client with overridden dependencies
- `test_user`: Regular user with validated account
- `test_manager`: Manager user with validated account
- `auth_headers`: Authentication headers for regular user
- `manager_headers`: Authentication headers for manager

## 📋 Test Categories

### **Unit Tests**
- Individual endpoint functionality
- Database operations
- Authentication logic

### **Integration Tests**
- End-to-end API calls
- Database state verification
- Authentication flow

### **Error Handling Tests**
- Invalid input validation
- Unauthorized access
- Database errors

## 🔧 Test Configuration

### **pytest.ini**
- Test discovery patterns
- Verbose output
- Warning handling
- Custom markers

### **conftest.py**
- Global test fixtures
- Database setup/teardown
- Authentication middleware override
- Test app configuration

## 📊 Coverage Report

After running tests with coverage, view the report:
```bash
# HTML report
open htmlcov/index.html

# Terminal report
docker exec timeoff-manager-api python -m pytest tests/ --cov=. --cov-report=term-missing
```

## 🐛 Known Issues

1. **Google OAuth Tests**: Need proper environment variable mocking
2. **Permission Request Validation**: Datetime validation logic needs adjustment
3. **Missing Fields Validation**: Status codes should be 422 for validation errors
4. **Manager ID Mismatch**: Test fixture ID assignment issue

## 🎯 Next Steps

1. Fix Google OAuth test mocking
2. Adjust validation error status codes
3. Fix test fixture ID consistency
4. Add more edge case tests
5. Improve test coverage to >90%
