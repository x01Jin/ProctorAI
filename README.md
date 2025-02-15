# ProctorAI

An AI-powered proctoring system for monitoring and detecting potential academic misconduct.

## Setup Instructions

1. Clone the repository

```bash
git clone [repository-url]
cd ProctorAI
```

1. Install dependencies

```bash
pip install -r requirements.txt
```

1. Configure environment

- Copy the example environment file:

```bash
cp .env.example .env
```

- Edit `.env` with your credentials:
  - Set your Roboflow API key
  - Configure database settings
  - Adjust other settings as needed

1. Database Setup

- Ensure XAMPP MySQL service is running
- Import the database schema:

```bash
mysql -u root -p proctorai < proctorai.sql
```

## Configuration

### Environment Variables

The application uses environment variables for configuration. These can be set in the `.env` file:

```ini
# Application Environment
APP_ENV=development

# Roboflow Configuration
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_PROJECT=your_project_name
ROBOFLOW_MODEL_VERSION=2

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=proctorai
```

### Settings Management

The application uses a settings system that supports:

- Environment-based configuration
- Secure credential storage
- UI-based settings management
- Automatic settings validation

Settings can be managed through:

1. Environment variables (preferred for sensitive data)
2. The settings dialog in the application
3. Direct modification of `app_settings.json` (not recommended)

## Running the Application

Start the application:

```bash
python main.py
```

The application will:

1. Load environment variables
2. Initialize required directories
3. Validate settings
4. Launch the main window

## Development Notes

- Default configuration uses XAMPP MySQL server
- Store sensitive information in `.env`, not in code
- Test changes in development environment first
- Use the settings dialog for configuration changes
- Check logs in `~/.proctorai/logs` for troubleshooting

## Security Best Practices

1. Never commit sensitive credentials
2. Keep the `.env` file secure and private
3. Use strong database passwords
4. Regularly update dependencies
5. Monitor application logs for issues

## Troubleshooting

1. Settings Issues

   - Check `.env` file exists and is properly configured
   - Verify database connection settings
   - Ensure Roboflow API key is valid

2. Database Connection

   - Verify XAMPP MySQL is running
   - Check database credentials
   - Ensure database exists and is properly initialized

3. Camera Issues

   - Check camera permissions
   - Verify camera is not in use by other applications
   - Test with different camera indices

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Create a pull request

Please ensure all sensitive data is properly handled and no credentials are committed to the repository.
