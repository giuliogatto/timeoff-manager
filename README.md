# Timeoff Manager

A comprehensive time-off management system with FastAPI backend, Vue.js frontend, and MySQL database.

## 🚀 Quick Start

### Using the Main Docker Compose (Recommended)

The main `docker-compose.yml` file orchestrates all services from the root directory.
Tested with the following:
Docker version 28.1.1, build 4eba377
Docker Compose version v2.35.1-desktop.1
On MAC OS Sonoma 14.7.1


#### Option 1: Using Convenience Scripts (Recommended)
```bash
# Start all services
./start.sh

# Stop all services
./stop.sh

# View logs
./logs.sh
```

#### Option 2: Direct Docker Compose Commands
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart all services
docker-compose restart
```

### Individual Service Management

You can also manage services individually:

```bash
# Data services (MySQL + phpMyAdmin)
cd data && docker-compose up -d

# Backend service (FastAPI)
cd backend && docker-compose up -d

# Frontend service (Vue.js)
cd frontend && docker-compose up -d
```

## 📋 Services

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | Vue.js application with i18n support |
| **Backend** | 8000 | FastAPI REST API with WebSocket support |
| **MySQL** | 3306 | Database server |
| **phpMyAdmin** | 8080 | Database management interface |

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **phpMyAdmin**: http://localhost:8080

## 🔧 Features

### Frontend
- ✅ Vue 3 with Composition API
- ✅ Internationalization (English/Italian)
- ✅ Real-time notifications via WebSocket
- ✅ Responsive design
- ✅ Pinia state management

### Backend
- ✅ FastAPI with automatic API documentation
- ✅ JWT authentication
- ✅ Google OAuth integration
- ✅ WebSocket support for real-time notifications
- ✅ Role-based access control (User/Manager)
- ✅ Email confirmation via Brevo

### Database
- ✅ MySQL 8.0 with persistent storage
- ✅ Automatic migrations
- ✅ phpMyAdmin for database management

## 👥 User Roles

### Manager
- View all leave requests
- Approve/reject requests
- Receive notifications for new requests
- Access to all features

### User
- Create leave requests
- View own requests
- Receive notifications for status changes
- Limited access to features

## 🔐 Authentication

### Local Authentication
- Email/password registration and login
- Email confirmation required
- Password hashing with bcrypt

### Google OAuth
- One-click login with Google account
- Automatic account creation
- No email confirmation required

#### Setting Up Google OAuth

To enable Google OAuth login, you need to create a Google OAuth application and obtain the necessary credentials:

##### Step 1: Access Google Cloud Console
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Create a new project or select an existing one

##### Step 2: Enable Required APIs
1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Google+ API" or "Google Identity"
3. Enable the **Google+ API** (provides access to user profile information)

##### Step 3: Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace)
3. Fill in the required information:
   - **App name**: "Timeoff Manager" (or your preferred name)
   - **User support email**: Your email address
   - **Developer contact information**: Your email address
4. Add scopes: `openid`, `email`, `profile`
5. Add test users if needed (for external apps)

##### Step 4: Create OAuth 2.0 Credentials
1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. **Application type**: Choose **Web application**
4. **Name**: "Timeoff Manager Backend" (or any descriptive name)

##### Step 5: Configure Authorized Origins and Redirects

**Authorized JavaScript origins** (for frontend requests):
- `http://localhost:3000` (for local development)
- `https://yourdomain.com` (for production - replace with your actual domain)

**Authorized redirect URIs** (for backend callbacks):
- `http://localhost:8000/google/callback` (for local development)
- `https://yourdomain.com/google/callback` (for production - replace with your actual domain)

##### Step 6: Get Your Credentials
After creating the OAuth client, you'll see:
- **Client ID** (this is your `GOOGLE_CLIENT_ID`)
- **Client Secret** (this is your `GOOGLE_CLIENT_SECRET`)

##### Step 7: Configure Your Application
Add the credentials to your `.env` file:
```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

##### Testing Your Setup
1. Start your application: `./start.sh`
2. Go to http://localhost:3000
3. Click the "Login with Google" button
4. You should be redirected to Google's OAuth consent screen
5. After authorization, you should be redirected back to your application

##### Troubleshooting
- **"Google OAuth not configured" error**: Check that your environment variables are properly set
- **Redirect URI mismatch**: Ensure the redirect URI in Google Console exactly matches your callback URL
- **"Invalid client" error**: Verify your Client ID and Client Secret are correct
- **CORS issues**: Make sure your frontend can communicate with your backend

##### Production Considerations
When deploying to production:
1. Update the redirect URIs in Google Console to use your production domain
2. Use HTTPS for all OAuth endpoints
3. Consider using environment-specific OAuth clients (separate for dev/staging/prod)
4. Monitor OAuth usage in Google Cloud Console

**Security Notes**:
- Never commit your `.env` file to version control
- Keep your Client Secret secure - it should never be exposed in client-side code
- Use HTTPS in production - Google OAuth requires secure connections for production use

## 📝 Environment Variables

Create a `.env` file in the root directory:

```env
# Database
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_PASS=your_mysql_password

# JWT
JWT_SECRET_KEY=your_jwt_secret_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Email (Brevo)
BREVO_TOKEN=your_brevo_api_token

# Frontend
VITE_BACKEND_URL=http://localhost:8000/
```

## 🗄️ Database Schema

### Tables
- `units` - Departments/units
- `users` - User accounts with roles
- `leave_requests` - Time-off and permission requests

### Default Data
- Admin user: `admin@example.com` / `password`
- Default unit: "Default Office"

## 🔄 Development

### Hot Reload
All services support hot reload for development:
- Frontend: Vite dev server with HMR
- Backend: Uvicorn with auto-reload
- Database: Persistent volume for data

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f timeoff-manager-api
docker-compose logs -f timeoff-manager-frontend
docker-compose logs -f timeoff-manager-data
```

## 🧪 Testing

### Manual Testing

1. **Start all services**: `docker-compose up -d`
2. **Access frontend**: http://localhost:3000
3. **Login as admin**: `admin@example.com` / `password`
4. **Create test requests** and test the workflow

### Backend Tests

The backend includes comprehensive automated tests using pytest. All tests run inside the Docker container to ensure consistency.

#### Prerequisites
- Backend service must be running: `docker-compose up -d` (from root) or `cd backend && docker-compose up -d`
- Test dependencies are automatically installed in the container

#### Running Tests

##### Quick Tests (Recommended for Development)
```bash
# From the backend directory
./run_tests_quick.sh

# Or manually
docker exec timeoff-manager-api python -m pytest tests/ -v --tb=no
```

##### Full Tests with Coverage Report
```bash
# From the backend directory
./run_tests.sh

# Or manually
docker exec timeoff-manager-api python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

##### Individual Test Files
```bash
# Test specific modules
docker exec timeoff-manager-api python -m pytest tests/test_authentication.py -v
docker exec timeoff-manager-api python -m pytest tests/test_leave_requests.py -v
docker exec timeoff-manager-api python -m pytest tests/test_profile.py -v
docker exec timeoff-manager-api python -m pytest tests/test_main.py -v

# Test specific test methods
docker exec timeoff-manager-api python -m pytest tests/test_leave_requests.py::TestLeaveRequests::test_create_timeoff_request -v
```

##### Test with Detailed Output
```bash
# Show full traceback for failures
docker exec timeoff-manager-api python -m pytest tests/ -v --tb=long

# Show print statements (for debugging)
docker exec timeoff-manager-api python -m pytest tests/ -v -s
```

#### Test Coverage

Current test coverage includes:
- ✅ **Authentication** (7 tests): Registration, login, email confirmation
- ✅ **Leave Requests** (15 tests): CRUD operations, role-based access, validation
- ✅ **Profile** (3 tests): User profile retrieval
- ✅ **Main API** (4 tests): Health checks, documentation endpoints

**Total: 29 tests with 84%+ coverage**

#### Test Architecture

- **Database**: Uses in-memory SQLite for fast, isolated tests
- **Authentication**: JWT tokens generated for test users
- **Fixtures**: Reusable test data (users, managers, units)
- **Mocking**: External API calls (Google OAuth) are mocked
- **Isolation**: Each test runs in a clean database state

#### Test Categories

| Category | Tests | Description |
|----------|-------|-------------|
| **Unit Tests** | 25 | Individual function/endpoint testing |
| **Integration Tests** | 4 | End-to-end workflow testing |
| **Authentication** | 7 | Login, registration, JWT validation |
| **Authorization** | 8 | Role-based access control |
| **Validation** | 6 | Input validation and error handling |

#### Test Configuration

- **Framework**: pytest with async support
- **Database**: SQLite in-memory for speed
- **Coverage**: pytest-cov with HTML reports
- **Markers**: @pytest.mark.slow, @pytest.mark.integration
- **Configuration**: `pytest.ini` in backend directory

#### Known Issues & Next Steps

- ⚠️ Google OAuth tests removed due to external API dependencies
- 🔄 WebSocket tests not yet implemented
- 📈 Target: 90%+ test coverage
- 🧪 Add more edge case tests
- 🔍 Improve test data factories

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, 3306, 8080 are available
2. **Database connection**: Check if MySQL container is running
3. **WebSocket issues**: Verify backend is running and accessible
4. **Frontend not loading**: Check if Node.js dependencies are installed

### Reset Everything
```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Rebuild and start
docker-compose up -d --build
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Todo

### Frontend
1. Add Tailwind
2. Add a component library
3. Use Typescript

### CD & CI
1. Implement a CD & CI pipeline with build, test and deploy steps

## 📄 License

This project is licensed under the MIT License.
