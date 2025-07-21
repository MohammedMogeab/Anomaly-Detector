# Installation Guide

This guide provides step-by-step instructions for installing and setting up the Business Logic Anomaly Detector in various environments.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.11 or higher
- **Node.js**: 20.0 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free disk space
- **Network**: Internet connection for package installation

### Recommended Requirements
- **CPU**: 4+ cores
- **Memory**: 16GB RAM
- **Storage**: 10GB free disk space (for logs and database)
- **Database**: PostgreSQL 13+ for production deployments

## 🐧 Linux Installation (Ubuntu/Debian)

### 1. Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Python 3.11
```bash
# Add deadsnakes PPA for Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-venv python3.11-dev python3-pip -y

# Verify installation
python3.11 --version
```

### 3. Install Node.js 20
```bash
# Install Node.js using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version
```

### 4. Install Additional Dependencies
```bash
# Install build tools and libraries
sudo apt install build-essential curl git wget unzip -y

# Install SQLite (for development)
sudo apt install sqlite3 libsqlite3-dev -y

# Install PostgreSQL (for production)
sudo apt install postgresql postgresql-contrib libpq-dev -y
```

### 5. Clone and Setup Application
```bash
# Clone repository (replace with actual repository URL)
git clone <repository-url>
cd business-logic-anomaly-detector

# Setup backend
cd anomaly_detector_api
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
cd ../anomaly_detector_frontend
npm install
npm run build

# Copy frontend build to backend
cp -r dist/* ../anomaly_detector_api/src/static/

# Return to backend directory
cd ../anomaly_detector_api
```

### 6. Initialize Database
```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database tables
python src/database.py
```

### 7. Start Application
```bash
# Start development server
python src/main.py

# Application will be available at http://localhost:5000
```

## 🍎 macOS Installation

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python 3.11
```bash
# Install Python 3.11
brew install python@3.11

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/bin:$PATH"

# Verify installation
python3.11 --version
```

### 3. Install Node.js 20
```bash
# Install Node.js
brew install node@20

# Link Node.js 20
brew link node@20 --force

# Verify installation
node --version
npm --version
```

### 4. Install Additional Dependencies
```bash
# Install Git (if not already installed)
brew install git

# Install SQLite
brew install sqlite

# Install PostgreSQL (optional, for production)
brew install postgresql@15
```

### 5. Clone and Setup Application
```bash
# Clone repository
git clone <repository-url>
cd business-logic-anomaly-detector

# Setup backend
cd anomaly_detector_api
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
cd ../anomaly_detector_frontend
npm install
npm run build

# Copy frontend build to backend
cp -r dist/* ../anomaly_detector_api/src/static/

# Return to backend directory
cd ../anomaly_detector_api
```

### 6. Initialize Database and Start
```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database
python src/database.py

# Start application
python src/main.py
```

## 🪟 Windows Installation

### 1. Install Python 3.11
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run the installer with "Add Python to PATH" checked
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

### 2. Install Node.js 20
1. Download Node.js 20 from [nodejs.org](https://nodejs.org/)
2. Run the installer
3. Verify installation:
   ```cmd
   node --version
   npm --version
   ```

### 3. Install Git
1. Download Git from [git-scm.com](https://git-scm.com/)
2. Run the installer with default settings

### 4. Clone and Setup Application
```cmd
# Clone repository
git clone <repository-url>
cd business-logic-anomaly-detector

# Setup backend
cd anomaly_detector_api
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup frontend
cd ..\anomaly_detector_frontend
npm install
npm run build

# Copy frontend build to backend (PowerShell)
Copy-Item -Recurse -Force dist\* ..\anomaly_detector_api\src\static\

# Return to backend directory
cd ..\anomaly_detector_api
```

### 5. Initialize Database and Start
```cmd
# Activate virtual environment
venv\Scripts\activate

# Initialize database
python src\database.py

# Start application
python src\main.py
```

## 🐳 Docker Installation

### 1. Install Docker
Follow the official Docker installation guide for your operating system:
- [Docker for Linux](https://docs.docker.com/engine/install/)
- [Docker Desktop for macOS](https://docs.docker.com/desktop/mac/install/)
- [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

### 2. Create Dockerfile
```dockerfile
# Create Dockerfile in project root
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Copy application files
COPY . .

# Build frontend
WORKDIR /app/anomaly_detector_frontend
RUN npm install && npm run build

# Copy frontend build to backend
RUN cp -r dist/* ../anomaly_detector_api/src/static/

# Setup backend
WORKDIR /app/anomaly_detector_api
RUN pip install --no-cache-dir -r requirements.txt

# Initialize database
RUN python src/database.py

# Expose port
EXPOSE 5000

# Start application
CMD ["python", "src/main.py"]
```

### 3. Build and Run Docker Container
```bash
# Build Docker image
docker build -t anomaly-detector .

# Run container
docker run -p 5000:5000 anomaly-detector

# Run with volume for persistent data
docker run -p 5000:5000 -v $(pwd)/data:/app/data anomaly-detector
```

### 4. Docker Compose (Optional)
```yaml
# Create docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: anomaly_detector
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

```bash
# Start with Docker Compose
docker-compose up -d
```

## ☁️ Cloud Deployment

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS AMI
   - Select t3.medium or larger instance type
   - Configure security group to allow HTTP (80) and HTTPS (443)

2. **Connect and Setup**
   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Follow Linux installation steps above
   # Install nginx for reverse proxy
   sudo apt install nginx -y
   ```

3. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/anomaly-detector
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable Site and Start Services**
   ```bash
   sudo ln -s /etc/nginx/sites-available/anomaly-detector /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   sudo systemctl enable nginx
   ```

### Google Cloud Platform Deployment

1. **Create Compute Engine Instance**
   ```bash
   gcloud compute instances create anomaly-detector \
       --image-family=ubuntu-2204-lts \
       --image-project=ubuntu-os-cloud \
       --machine-type=e2-medium \
       --tags=http-server,https-server
   ```

2. **Setup Application**
   ```bash
   # SSH to instance
   gcloud compute ssh anomaly-detector
   
   # Follow Linux installation steps
   ```

### Azure App Service Deployment

1. **Create App Service**
   ```bash
   az webapp create \
       --resource-group myResourceGroup \
       --plan myAppServicePlan \
       --name anomaly-detector \
       --runtime "PYTHON|3.11"
   ```

2. **Deploy Application**
   ```bash
   # Configure deployment
   az webapp deployment source config-zip \
       --resource-group myResourceGroup \
       --name anomaly-detector \
       --src anomaly-detector.zip
   ```

## 🔧 Configuration

### Environment Variables

Create `.env` file in the backend directory:

```bash
# .env file
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///anomaly_detector.db
CORS_ORIGINS=*
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216
```

### Database Configuration

#### SQLite (Development)
```python
# Default configuration - no changes needed
DATABASE_URL = "sqlite:///anomaly_detector.db"
```

#### PostgreSQL (Production)
```bash
# Install PostgreSQL client
pip install psycopg2-binary

# Update DATABASE_URL
DATABASE_URL = "postgresql://username:password@localhost:5432/anomaly_detector"
```

### Production Optimizations

1. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
   ```

2. **Enable Logging**
   ```python
   # In src/config.py
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

3. **Configure Reverse Proxy**
   - Use Nginx or Apache for static file serving
   - Enable HTTPS with SSL certificates
   - Configure rate limiting and security headers

## 🧪 Verify Installation

### 1. Check Application Status
```bash
# Test API endpoints
curl http://localhost:5000/api/flows
curl http://localhost:5000/api/recording/status
```

### 2. Run Test Suite
```bash
cd anomaly_detector_api
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

PYTHONPATH=$(pwd) python tests/test_simplified.py
PYTHONPATH=$(pwd) python tests/test_api_endpoints.py
```

### 3. Access Web Interface
1. Open browser to `http://localhost:5000`
2. Verify all sections load correctly:
   - Dashboard
   - Flows
   - Recording
   - Payload Generator
   - Replay Interface
   - Analysis Results
   - Reports

## 🔍 Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   ```bash
   # Linux/macOS
   lsof -ti:5000 | xargs kill -9
   
   # Windows
   netstat -ano | findstr :5000
   taskkill /PID <PID> /F
   ```

2. **Python module not found**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   
   # Reinstall requirements
   pip install -r requirements.txt
   ```

3. **Database connection errors**
   ```bash
   # Reset SQLite database
   rm src/database/anomaly_detector.db
   python src/database.py
   ```

4. **Frontend build issues**
   ```bash
   cd anomaly_detector_frontend
   rm -rf node_modules dist
   npm install
   npm run build
   ```

5. **Permission denied errors (Linux)**
   ```bash
   # Fix file permissions
   chmod +x src/main.py
   chown -R $USER:$USER .
   ```

### Getting Help

- Check the [FAQ](docs/faq.md) for common questions
- Review [troubleshooting guide](docs/troubleshooting.md)
- Create an issue on the project repository
- Contact the development team

## 📚 Next Steps

After successful installation:

1. Read the [User Guide](user-guide.md) to learn how to use the application
2. Review the [API Documentation](api-reference.md) for integration
3. Check the [Developer Guide](developer-guide.md) for customization
4. Set up monitoring and logging for production deployments

---

**Installation complete!** 🎉

Your Business Logic Anomaly Detector is now ready to use. Access the web interface at `http://localhost:5000` and start your first security testing flow.

