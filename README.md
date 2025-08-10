# Timeoff Manager API

A comprehensive FastAPI-based timeoff management system with user authentication, role-based access control, and Google OAuth integration.

## 🚀 Features

- **User Authentication**: Local authentication with email confirmation
- **Google OAuth**: Seamless Google login integration
- **Role-Based Access**: Manager and User roles with different permissions
- **Leave Request Management**: Support for timeoff (day-based) and permission (hour-based) requests
- **Manager Approval System**: Managers can approve/reject leave requests
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **JWT Authentication**: Secure token-based authentication
- **Email Integration**: Brevo email service for account confirmation

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Google Cloud Console account (for OAuth)
- Brevo account (for email service)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd timeoff-manager
```

### 2. Environment Variables Setup

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_PASS=your_secure_mysql_password

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_change_in_production

# Email Service (Brevo)
BREVO_TOKEN=your_brevo_api_token

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
```

### 3. Google OAuth Setup

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it

#### Step 2: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Set application type to "Web application"
4. Add authorized redirect URIs:
   - Development: `http://localhost:8000/google/callback`
   - Production: `https://yourdomain.com/google/callback`
5. Copy the Client ID and Client Secret to your `.env` file

#### Step 3: Configure OAuth Consent Screen
1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in the required information:
   - App name: "Timeoff Manager"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes: `openid`, `email`, `profile`
5. Add test users if needed

### 4. Brevo Email Setup (Optional)

1. Sign up at [Brevo](https://www.brevo.com/)
2. Go to "SMTP & API" → "API Keys"
3. Create a new API key
4. Copy the key to your `.env` file as `BREVO_TOKEN`

### 5. Start the Services

#### Start Database and phpMyAdmin
```bash
cd data
docker-compose up -d
```

#### Start the API
```bash
cd backend
docker-compose up -d
```

### 6. Verify Installation

Check if services are running:
```bash
# Check API health
curl http://localhost:8000/health

# Check database (phpMyAdmin)
# Open http://localhost:8080 in your browser
# Login with: root / your_root_password
```

## 📚 API Documentation

Once the services are running, you can access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **phpMyAdmin**: http://localhost:8080

## 🔐 Authentication Endpoints

### Local Authentication

#### Register User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

#### Confirm Registration
```bash
curl -X POST "http://localhost:8000/register_confirm" \
  -H "Content-Type: application/json" \
  -d '{"token": "confirmation_token_from_email"}'
```

### Google OAuth

#### Get OAuth URL
```bash
curl -X GET "http://localhost:8000/google/auth-url"
```

#### OAuth Flow
1. Redirect user to the `auth_url` from the response
2. User authenticates with Google
3. Google redirects to `/google/callback?code=...`
4. Backend exchanges code for user info and returns JWT token

## 📝 Leave Request Management

### Create Leave Request
```bash
# Timeoff (day-based)
curl -X POST "http://localhost:8000/leave_requests" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "request_type": "timeoff",
    "start_date": "2025-01-15",
    "end_date": "2025-01-17",
    "reason": "Personal vacation"
  }'

# Permission (hour-based)
curl -X POST "http://localhost:8000/leave_requests" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "request_type": "permission",
    "start_datetime": "2025-01-20T10:00:00",
    "end_datetime": "2025-01-20T12:00:00",
    "reason": "Doctor appointment"
  }'
```

### Get Leave Requests
```bash
# Users see only their requests
# Managers see all requests
curl -X GET "http://localhost:8000/leave_requests" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Request Status (Managers Only)
```bash
curl -X PUT "http://localhost:8000/leave_requests/{request_id}/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer MANAGER_JWT_TOKEN" \
  -d '{
    "status": "approved",
    "review_comment": "Approved for vacation"
  }'
```

## 👥 User Management

### Get User Profile
```bash
curl -X GET "http://localhost:8000/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `name`: User's full name
- `email`: Unique email address
- `password_hash`: Hashed password (null for Google users)
- `auth_provider`: 'local' or 'google'
- `role`: 'user' or 'manager'
- `unit_id`: Foreign key to units table
- `validated`: Boolean for email confirmation
- `confirmation_token`: Token for email confirmation
- `created_at`, `updated_at`: Timestamps

### Leave Requests Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `request_type`: 'timeoff' or 'permission'
- `start_date`, `end_date`: For timeoff requests
- `start_datetime`, `end_datetime`: For permission requests
- `reason`: Request reason
- `status`: 'pending', 'approved', or 'rejected'
- `reviewed_by`: Manager who reviewed
- `reviewed_at`: Review timestamp
- `created_at`, `updated_at`: Timestamps

### Units Table
- `id`: Primary key
- `name`: Unit/department name

## 🔧 Development

### Project Structure
```
timeoff-manager/
├── backend/
│   ├── api/
│   │   ├── authentication.py    # Local auth endpoints
│   │   ├── google_oauth.py      # Google OAuth endpoints
│   │   ├── leave_requests.py    # Leave request management
│   │   └── profile.py           # User profile endpoints
│   ├── models/
│   │   └── leave_requests.py    # Database models
│   ├── middleware/
│   │   └── auth.py              # JWT authentication middleware
│   ├── database.py              # Database configuration
│   ├── main.py                  # FastAPI application
│   └── docker-compose.yml       # Backend services
├── data/
│   ├── migrations/              # Database migrations
│   └── docker-compose.yml       # Database services
└── README.md
```

### Adding New Features
1. Create new API endpoints in `backend/api/`
2. Add database models in `backend/models/`
3. Update migrations in `data/migrations/`
4. Test with the interactive API docs

## 🚀 Production Deployment

### Environment Variables
Update your `.env` file for production:
```bash
# Use strong, unique passwords
MYSQL_ROOT_PASSWORD=very_secure_production_password
MYSQL_PASS=very_secure_production_password

# Use a strong JWT secret
JWT_SECRET_KEY=very_long_random_string_for_production

# Update Google OAuth redirect URIs
GOOGLE_CLIENT_ID=your_production_client_id
GOOGLE_CLIENT_SECRET=your_production_client_secret

# Configure production email service
BREVO_TOKEN=your_production_brevo_token
```

### Security Considerations
1. Use HTTPS in production
2. Set strong passwords and secrets
3. Configure proper CORS settings
4. Set up proper logging and monitoring
5. Regular database backups
6. Keep dependencies updated

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check if database is running
docker ps | grep mysql

# Check database logs
docker logs timeoff-manager-data
```

#### OAuth Configuration Issues
- Verify Google OAuth credentials are correct
- Check redirect URIs match exactly
- Ensure Google+ API is enabled
- Verify environment variables are set

#### Email Service Issues
- Check Brevo API key is valid
- Verify email templates are configured
- Check network connectivity

### Logs
```bash
# API logs
docker logs timeoff-manager-api

# Database logs
docker logs timeoff-manager-data

# phpMyAdmin logs
docker logs timeoff-manager-phpmyadmin
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the troubleshooting section above
