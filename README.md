# Timeoff Manager

A comprehensive time-off management system with FastAPI backend, Vue.js frontend, and MySQL database.

## 🚀 Quick Start

### Using the Main Docker Compose (Recommended)

The main `docker-compose.yml` file orchestrates all services from the root directory:

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

1. **Start all services**: `docker-compose up -d`
2. **Access frontend**: http://localhost:3000
3. **Login as admin**: `admin@example.com` / `password`
4. **Create test requests** and test the workflow

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

## 📄 License

This project is licensed under the MIT License.
