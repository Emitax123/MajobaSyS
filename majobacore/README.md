# MajobaCore

A secure and modular Django project with proper settings configuration for different environments.

## Features

- ✅ **Modular Settings**: Separate configurations for development, production, and testing
- ✅ **Security First**: Production-ready security configurations
- ✅ **Environment Variables**: Secure configuration management with python-decouple
- ✅ **REST API**: Django REST Framework with token authentication
- ✅ **Custom User Model**: Extended user model with additional fields
- ✅ **CORS Support**: Configured for frontend integration
- ✅ **Static Files**: WhiteNoise for production static file serving
- ✅ **Logging**: Comprehensive logging configuration
- ✅ **Caching**: Redis support for production
- ✅ **Database**: PostgreSQL support for production

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd majobacore

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements\development.txt

# Copy environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

### 2. Configure Environment

Edit the `.env` file with your settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=majobacore.settings.development
```

### 3. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if any)
python manage.py loaddata initial_data.json
```

### 4. Run Development Server

```bash
# Option 1: Use management command
python manage.py runserver

# Option 2: Use batch script (Windows)
run_dev.bat

# Option 3: Specify settings explicitly
python manage.py runserver --settings=majobacore.settings.development
```

## Project Structure

```
majobacore/
├── majobacore/                 # Main project package
│   ├── settings/              # Modular settings
│   │   ├── __init__.py
│   │   ├── base.py           # Base settings
│   │   ├── development.py    # Development settings
│   │   ├── production.py     # Production settings
│   │   └── testing.py        # Testing settings
│   ├── utils/                # Utility modules
│   │   ├── __init__.py
│   │   └── security.py       # Security utilities
│   ├── management/           # Custom management commands
│   │   └── commands/
│   │       └── generate_secret_key.py
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/                    # Custom user app
├── manager/                  # Manager app
├── requirements/             # Requirements files
│   ├── base.txt             # Base requirements
│   ├── development.txt      # Development requirements
│   └── production.txt       # Production requirements
├── static/                  # Static files
├── media/                   # Media files
├── templates/               # Templates
├── logs/                    # Log files
├── .env.example            # Environment variables example
├── .gitignore              # Git ignore file
├── manage.py               # Django management script
├── setup_dev.bat           # Development setup script
└── run_dev.bat             # Quick run script
```

## Settings Modules

### Development Settings (`majobacore.settings.development`)
- Debug mode enabled
- SQLite database
- Console email backend
- CORS allow all origins
- Debug toolbar enabled

### Production Settings (`majobacore.settings.production`)
- Debug mode disabled
- PostgreSQL database
- Security headers enabled
- SSL redirect enabled
- SMTP email backend
- Redis caching

### Testing Settings (`majobacore.settings.testing`)
- In-memory database
- Faster password hashers
- Disabled migrations
- Dummy cache backend

## Environment Variables

Key environment variables (see `.env.example` for complete list):

```env
# Django Core
SECRET_KEY=your-secret-key
DEBUG=True/False
DJANGO_SETTINGS_MODULE=majobacore.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (Production)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Management Commands

### Generate Secret Key
```bash
python manage.py generate_secret_key
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile

### Admin
- `/admin/` - Django admin interface

## Security Features

### Production Security
- ✅ HTTPS redirect
- ✅ HSTS headers
- ✅ Secure cookies
- ✅ XSS protection
- ✅ CSRF protection
- ✅ Content type sniffing protection
- ✅ Clickjacking protection
- ✅ Rate limiting
- ✅ Security headers middleware

### Authentication
- ✅ Token-based authentication
- ✅ Custom user model
- ✅ Password validation
- ✅ Session security

## Deployment

### Preparation
1. Set environment variables for production
2. Configure PostgreSQL database
3. Set up Redis for caching
4. Configure email backend
5. Set up static file serving
6. Configure logging

### Environment Setup
```bash
# Set production settings
export DJANGO_SETTINGS_MODULE=majobacore.settings.production

# Install production requirements
pip install -r requirements/production.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate
```

### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 3 majobacore.wsgi:application
```

## Development Tools

### Code Quality
```bash
# Install development tools
pip install -r requirements/development.txt

# Run tests
python manage.py test

# Code formatting
black .
isort .

# Linting
flake8
```

### Debugging
- Django Debug Toolbar (development only)
- Comprehensive logging
- Error tracking ready for Sentry

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please create an issue in the repository.
