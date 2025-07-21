# Business Logic Anomaly Detector

A comprehensive automated security testing tool designed to detect business logic vulnerabilities in web applications through intelligent request replay and response analysis.

## 🎯 Overview

The Business Logic Anomaly Detector is an advanced security testing platform that identifies potential vulnerabilities by analyzing differences between original and modified HTTP requests. It specializes in detecting:

- **Unauthorized Access**: Authentication and authorization bypasses
- **Privilege Escalation**: Role-based access control violations  
- **Parameter Tampering**: Input validation and business logic flaws
- **Sequence Manipulation**: Workflow and state management vulnerabilities

## ✨ Key Features

### 🔍 **Intelligent Detection Engine**
- Advanced anomaly detection algorithms with confidence scoring
- Machine learning-based pattern recognition
- Risk assessment and vulnerability classification
- Real-time analysis with detailed reporting

### 🎨 **Professional Web Interface**
- Modern, responsive React-based dashboard
- Real-time monitoring and status updates
- Interactive data visualizations and charts
- Comprehensive flow management system

### 📊 **Advanced Analytics & Reporting**
- Executive summary reports with risk scoring
- Detailed technical findings with recommendations
- Timeline analysis and trend detection
- Comparative analysis across multiple flows
- Export capabilities (HTML, JSON, PDF)

### 🚀 **Enterprise-Ready Architecture**
- RESTful API with comprehensive endpoints
- Scalable database design with SQLite/PostgreSQL support
- Modular architecture for easy extension
- Docker containerization support
- Production deployment ready

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Database      │
│   (React)       │◄──►│   (Flask)       │◄──►│   (SQLite)      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Flow Mgmt     │    │ • Flows         │
│ • Flow Mgmt     │    │ • Recording     │    │ • Requests      │
│ • Recording     │    │ • Payload Gen   │    │ • Test Cases    │
│ • Replay        │    │ • Replay Exec   │    │ • Responses     │
│ • Analysis      │    │ • Analysis      │    │ • Anomalies     │
│ • Reports       │    │ • Reporting     │    │ • Sessions      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm/pnpm/yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd business-logic-anomaly-detector
   ```

2. **Set up the backend**
   ```bash
   cd anomaly_detector_api
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   cd ../anomaly_detector_frontend
   npm install
   npm run build
   ```

4. **Copy frontend build to backend**
   ```bash
   cp -r dist/* ../anomaly_detector_api/src/static/
   ```

5. **Start the application**
   ```bash
   cd ../anomaly_detector_api
   python src/main.py
   ```

6. **Access the application**
   - Open your browser to `http://localhost:5000`
   - The API is available at `http://localhost:5000/api`

## 📖 Usage Guide

### 1. Create a Testing Flow

1. Navigate to the **Flows** section
2. Click **"Create New Flow"**
3. Enter flow details:
   - **Name**: Descriptive name for your test
   - **Description**: Purpose and scope of testing
   - **Target Domain**: Domain to be tested (e.g., `api.example.com`)

### 2. Record HTTP Requests

1. Select your created flow
2. Go to **Recording** section
3. Click **"Start Recording"**
4. Add requests manually or import from tools like Burp Suite/OWASP ZAP
5. Stop recording when complete

### 3. Generate Test Payloads

1. Navigate to **Payload Generator**
2. Select requests to generate payloads for
3. Choose payload categories:
   - **String**: Boundary testing, injection attempts
   - **Auth**: Authentication bypass, token manipulation
   - **Parameter**: Value tampering, type confusion
   - **Sequence**: Workflow manipulation, state bypass

### 4. Execute Replay Testing

1. Go to **Replay Interface**
2. Select flow and test cases to execute
3. Monitor real-time progress
4. Review execution results

### 5. Analyze Results

1. Visit **Analysis Results** section
2. Review detected anomalies by severity
3. Filter by vulnerability type or confidence score
4. Examine detailed findings and recommendations

### 6. Generate Reports

1. Access **Reports** section
2. Select flow for reporting
3. Choose report format:
   - **HTML**: Professional formatted report
   - **JSON**: Machine-readable data export
   - **Executive Summary**: High-level overview
4. Download or view reports

## 🔧 API Documentation

### Authentication
Currently, the API does not require authentication for development/testing purposes. For production deployment, implement appropriate authentication mechanisms.

### Base URL
```
http://localhost:5000/api
```

### Core Endpoints

#### Flows Management
```http
GET    /api/flows              # List all flows
POST   /api/flows              # Create new flow
GET    /api/flows/{id}         # Get specific flow
PUT    /api/flows/{id}         # Update flow
DELETE /api/flows/{id}         # Delete flow
```

#### Recording
```http
GET    /api/recording/status   # Get recording status
POST   /api/recording/start    # Start recording
POST   /api/recording/stop     # Stop recording
POST   /api/recording/request  # Add request to recording
```

#### Payload Generation
```http
POST   /api/payloads/generate/request/{id}  # Generate payloads for request
POST   /api/payloads/generate/flow/{id}     # Generate payloads for flow
GET    /api/payloads/rules                  # Get payload generation rules
```

#### Replay Execution
```http
POST   /api/replay/flow/{id}           # Replay entire flow
POST   /api/replay/testcase/{id}       # Replay specific test case
GET    /api/replay/status/{id}         # Get replay status
```

#### Analysis
```http
POST   /api/analysis/flow/{id}         # Analyze flow results
GET    /api/analysis/anomalies/{id}    # Get anomalies for flow
POST   /api/analysis/rules             # Update detection rules
```

#### Reporting
```http
GET    /api/reports/summary/{id}       # Get report summary
GET    /api/reports/html/{id}          # Generate HTML report
GET    /api/reports/json/{id}          # Generate JSON report
GET    /api/reports/executive/{id}     # Get executive summary
GET    /api/reports/analytics/{id}     # Get detailed analytics
```

### Request/Response Examples

#### Create Flow
```http
POST /api/flows
Content-Type: application/json

{
  "name": "E-commerce API Security Test",
  "description": "Comprehensive security testing of shopping cart functionality",
  "target_domain": "api.shop.example.com"
}
```

#### Add Request to Recording
```http
POST /api/recording/request
Content-Type: application/json

{
  "method": "POST",
  "url": "https://api.shop.example.com/cart/add",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
  },
  "body": {
    "product_id": 123,
    "quantity": 2,
    "user_id": 456
  }
}
```

## 🔬 Advanced Configuration

### Database Configuration

By default, the system uses SQLite for simplicity. For production deployments, configure PostgreSQL:

```python
# In src/config.py
DATABASE_URL = "postgresql://user:password@localhost:5432/anomaly_detector"
```

### Payload Generation Rules

Customize payload generation by modifying rules in `src/payload_generation.py`:

```python
# Add custom payload rules
custom_rules = {
    'category': 'custom',
    'type': 'business_logic',
    'patterns': [
        {'field': 'price', 'values': [-1, 0, 999999]},
        {'field': 'quantity', 'values': [-1, 0, 1000000]}
    ]
}
```

### Detection Algorithms

Enhance detection algorithms in `src/analysis.py`:

```python
# Custom anomaly detection logic
def detect_custom_anomaly(self, original, replayed, test_case):
    # Implement custom detection logic
    if custom_condition_met(original, replayed):
        return AnomalyInfo(
            type='custom_anomaly',
            severity='High',
            description='Custom business logic violation detected',
            confidence_score=0.85
        )
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
cd anomaly_detector_api
PYTHONPATH=/path/to/anomaly_detector_api python tests/test_simplified.py
PYTHONPATH=/path/to/anomaly_detector_api python tests/test_api_endpoints.py

# Run specific test categories
python tests/test_simplified.py TestRiskScorer
python tests/test_api_endpoints.py TestAPIValidation
```

### Test Coverage

The test suite covers:
- ✅ Risk scoring algorithms (3 tests)
- ✅ Trend analysis (3 tests)
- ✅ Data visualization processing (4 tests)
- ✅ Chart configuration generation (2 tests)
- ✅ Enhanced reporting (3 tests)
- ✅ API endpoint validation (20 tests)

## 🚀 Deployment

### Development Deployment

```bash
# Start development server
cd anomaly_detector_api
source venv/bin/activate
python src/main.py
```

### Production Deployment

1. **Using Docker** (Recommended)
   ```bash
   # Build Docker image
   docker build -t anomaly-detector .
   
   # Run container
   docker run -p 5000:5000 -e FLASK_ENV=production anomaly-detector
   ```

2. **Using WSGI Server**
   ```bash
   # Install production server
   pip install gunicorn
   
   # Run with Gunicorn
   gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
   ```

3. **Environment Variables**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=postgresql://user:pass@localhost/db
   export SECRET_KEY=your-secret-key-here
   ```

### Cloud Deployment

The application is ready for deployment on:
- **AWS**: EC2, ECS, or Lambda
- **Google Cloud**: App Engine, Cloud Run, or Compute Engine
- **Azure**: App Service, Container Instances, or Virtual Machines
- **Heroku**: Direct deployment with Procfile

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Enable HTTPS/TLS encryption
- [ ] Implement authentication and authorization
- [ ] Configure rate limiting
- [ ] Set up input validation and sanitization
- [ ] Enable security headers (HSTS, CSP, etc.)
- [ ] Configure CORS appropriately
- [ ] Set up logging and monitoring
- [ ] Regular security updates and patches

### Data Protection

- All sensitive data should be encrypted at rest
- Implement proper session management
- Use secure password hashing (bcrypt, Argon2)
- Regular security audits and penetration testing

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style

- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript/React code
- Add docstrings for all functions and classes
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [User Guide](docs/user-guide.md)
- [API Reference](docs/api-reference.md)
- [Developer Guide](docs/developer-guide.md)

### Getting Help
- Create an issue for bug reports
- Use discussions for questions and feature requests
- Check existing documentation and FAQ

### Troubleshooting

**Common Issues:**

1. **Port already in use**
   ```bash
   # Find and kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **Database connection errors**
   ```bash
   # Reset database
   rm src/database/anomaly_detector.db
   python src/database.py  # Recreate tables
   ```

3. **Frontend build issues**
   ```bash
   # Clear cache and rebuild
   cd anomaly_detector_frontend
   rm -rf node_modules dist
   npm install
   npm run build
   ```

## 🎯 Roadmap

### Version 2.0 Features
- [ ] Machine learning-based anomaly detection
- [ ] Integration with CI/CD pipelines
- [ ] Multi-tenant support
- [ ] Advanced reporting dashboards
- [ ] Plugin architecture for custom detectors
- [ ] Real-time collaboration features

### Performance Improvements
- [ ] Async request processing
- [ ] Database query optimization
- [ ] Caching layer implementation
- [ ] Load balancing support

---

**Built with ❤️ for the security community**

For more information, visit our [documentation](docs/) or contact the development team.

