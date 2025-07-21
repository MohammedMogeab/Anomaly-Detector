
# User Guide

Welcome to the Business Logic Anomaly Detector! This comprehensive guide will help you master the platform and conduct effective security testing of web applications.

## 🎯 Getting Started

### What is Business Logic Anomaly Detection?

Business logic vulnerabilities are security flaws that occur when an application's workflow can be manipulated to perform unintended actions. Unlike traditional vulnerabilities (like SQL injection), these flaws exploit the intended functionality of an application in unexpected ways.

**Common Examples:**
- Bypassing payment processes by manipulating order workflows
- Accessing admin functions through parameter tampering
- Escalating privileges by modifying user roles
- Skipping authentication steps in multi-step processes

### How the Detector Works

The Business Logic Anomaly Detector uses a sophisticated approach:

1. **Record** legitimate HTTP requests from your application
2. **Generate** modified versions of these requests (test payloads)
3. **Replay** both original and modified requests
4. **Analyze** differences in responses to identify anomalies
5. **Report** potential vulnerabilities with risk assessments

## 🏠 Dashboard Overview

When you first access the application at `http://localhost:5000`, you'll see the main dashboard with:

### Key Metrics
- **Total Flows**: Number of testing flows created
- **Active Recordings**: Currently recording sessions
- **Anomalies Detected**: Total security issues found
- **Risk Score**: Overall security posture assessment

### Quick Actions
- **Create New Flow**: Start a new testing session
- **Start Recording**: Begin capturing HTTP requests
- **View Latest Results**: Check recent analysis results
- **Generate Report**: Create comprehensive security reports

### Recent Activity
- Timeline of recent testing activities
- Latest anomalies discovered
- System status and health indicators

## 📊 Flow Management

Flows are the foundation of your testing activities. Each flow represents a complete security testing session for a specific application or feature.

### Creating a New Flow

1. **Navigate to Flows Section**
   - Click "Flows" in the sidebar navigation

2. **Click "Create New Flow"**
   - Fill in the flow details form

3. **Flow Configuration**
   ```
   Name: E-commerce Checkout Process
   Description: Security testing of the complete purchase workflow including cart management, payment processing, and order confirmation
   Target Domain: shop.example.com
   ```

4. **Best Practices for Flow Names**
   - Use descriptive names that indicate the testing scope
   - Include the application feature being tested
   - Add version numbers for iterative testing

### Managing Existing Flows

**View Flow Details:**
- Click on any flow to see detailed information
- Review request count, creation date, and status
- Access flow-specific actions and reports

**Flow Actions:**
- **Select**: Make this flow active for recording/testing
- **Edit**: Modify flow details and configuration
- **Clone**: Create a copy for similar testing scenarios
- **Delete**: Remove flow and all associated data
- **Export**: Download flow data for backup or sharing

### Flow Organization Tips

- **Group by Application**: Create separate flows for different applications
- **Separate by Feature**: Use individual flows for distinct features (login, checkout, admin panel)
- **Version Control**: Create new flows for different application versions
- **Environment Separation**: Maintain separate flows for dev/staging/production testing

## 🎙️ Recording HTTP Requests

The recording feature captures HTTP requests that will serve as the baseline for your security testing.

### Starting a Recording Session

1. **Select Active Flow**
   - Ensure you have selected the correct flow for recording

2. **Navigate to Recording Section**
   - Click "Recording" in the sidebar

3. **Start Recording**
   - Click "Start Recording" button
   - The status indicator will show "Recording Active"

### Adding Requests

#### Manual Request Addition

1. **Click "Add Request"**
2. **Fill in Request Details:**
   ```
   Method: POST
   URL: https://shop.example.com/api/cart/add
   Headers: {
     "Content-Type": "application/json",
     "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs...",
     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
   }
   Body: {
     "product_id": 12345,
     "quantity": 2,
     "user_id": 67890
   }
   ```

3. **Validate and Save**
   - Review the request details
   - Click "Add Request" to save

#### Import from Security Tools

**From Burp Suite:**
1. In Burp Suite, right-click on requests in Proxy/Target
2. Select "Copy as curl command"
3. Use the "Import from cURL" feature in the recorder
4. Paste the cURL command and convert to request

**From OWASP ZAP:**
1. Export requests from ZAP as HAR file
2. Use the "Import HAR" feature in the recorder
3. Select specific requests to import

**From Browser Developer Tools:**
1. Open Network tab in browser developer tools
2. Perform actions in the application
3. Right-click on requests and "Copy as cURL"
4. Import using the cURL import feature

### Recording Best Practices

**Comprehensive Coverage:**
- Record complete user workflows, not just individual requests
- Include both successful and error scenarios
- Capture requests with different user roles and permissions

**Authentication Handling:**
- Record requests with valid authentication tokens
- Include requests that require different privilege levels
- Capture session management requests (login, logout, refresh)

**Parameter Variety:**
- Record requests with different parameter values
- Include edge cases (empty values, special characters)
- Capture requests with various data types

**Request Quality:**
- Ensure headers are complete and accurate
- Verify request bodies are properly formatted
- Test that recorded requests work when replayed

### Stopping Recording

1. **Click "Stop Recording"**
2. **Review Captured Requests**
   - Verify all important requests were captured
   - Check request details for accuracy
3. **Save Recording Session**
   - The requests are automatically saved to the active flow

## 🎯 Payload Generation

Payload generation creates modified versions of your recorded requests to test for business logic vulnerabilities.

### Understanding Payload Categories

#### String Payloads
**Purpose**: Test string handling and boundary conditions
**Examples**:
- Extremely long strings (buffer overflow attempts)
- Empty strings and null values
- Special characters and encoding issues
- SQL injection and XSS payloads in string fields

#### Authentication Payloads
**Purpose**: Test authentication and authorization mechanisms
**Examples**:
- Modified JWT tokens with different user IDs
- Expired or invalid authentication tokens
- Missing authentication headers
- Token manipulation and privilege escalation attempts

#### Parameter Payloads
**Purpose**: Test parameter validation and business logic
**Examples**:
- Negative values in quantity/price fields
- Extremely large numbers
- Type confusion (string instead of number)
- Hidden parameter manipulation

#### Sequence Payloads
**Purpose**: Test workflow and state management
**Examples**:
- Skipping required steps in multi-step processes
- Repeating steps that should only occur once
- Accessing steps out of order
- State manipulation and race conditions

### Generating Payloads

#### For Individual Requests

1. **Navigate to Payload Generator**
2. **Select Request**
   - Choose a specific request from your flow
3. **Choose Payload Categories**
   - Select one or more categories (String, Auth, Parameter, Sequence)
4. **Configure Generation Options**
   ```
   String Payloads:
   ✓ Boundary testing (long strings, empty values)
   ✓ Injection attempts (SQL, XSS, Command injection)
   ✓ Encoding tests (Unicode, URL encoding)
   
   Auth Payloads:
   ✓ Token manipulation
   ✓ Privilege escalation
   ✓ Session hijacking attempts
   
   Parameter Payloads:
   ✓ Value tampering
   ✓ Type confusion
   ✓ Range violations
   
   Sequence Payloads:
   ✓ Workflow manipulation
   ✓ State bypass attempts
   ✓ Race conditions
   ```

5. **Generate Payloads**
   - Click "Generate Payloads"
   - Review the generated test cases

#### For Entire Flows

1. **Select "Generate for Flow"**
2. **Choose Requests**
   - Select which requests to generate payloads for
   - Prioritize critical business logic endpoints
3. **Batch Configuration**
   - Apply consistent payload categories across requests
   - Set generation limits to manage test volume
4. **Generate and Review**
   - Generate payloads for all selected requests
   - Review the complete test case collection

### Payload Customization

#### Custom Payload Rules

You can create custom payload generation rules:

```json
{
  "category": "business_logic",
  "type": "price_manipulation",
  "description": "Test price manipulation vulnerabilities",
  "rules": [
    {
      "field_pattern": "price|cost|amount",
      "test_values": [-1, 0, 0.01, 999999.99],
      "description": "Test negative and extreme price values"
    }
  ]
}
```

#### Advanced Configuration

**Field-Specific Rules:**
- Target specific parameter names or patterns
- Apply different test values based on field types
- Configure severity levels for different test types

**Context-Aware Generation:**
- Consider request context (user role, session state)
- Generate payloads based on application workflow
- Adapt tests based on response patterns

### Payload Review and Management

**Review Generated Payloads:**
- Examine each generated test case
- Understand what vulnerability each payload tests for
- Modify or remove payloads that aren't relevant

**Payload Organization:**
- Group payloads by vulnerability type
- Prioritize high-impact test cases
- Create payload templates for reuse

**Quality Assurance:**
- Verify payloads are syntactically correct
- Test that payloads will execute properly
- Ensure payloads target the intended vulnerability types

## 🔄 Replay Execution

The replay engine executes your test cases by sending both original and modified requests, then analyzes the differences.

### Understanding Replay Process

1. **Original Request Execution**
   - Send the original, unmodified request
   - Record response (status, headers, body, timing)

2. **Modified Request Execution**
   - Send the payload-modified request
   - Record response details

3. **Response Comparison**
   - Compare status codes, content length, response time
   - Analyze response content for anomalies
   - Calculate confidence scores for detected issues

### Starting Replay Execution

#### Single Test Case Replay

1. **Navigate to Replay Interface**
2. **Select Test Case**
   - Choose a specific test case to execute
3. **Configure Execution**
   ```
   Execution Options:
   ✓ Include response body analysis
   ✓ Enable timing analysis
   ✓ Capture full headers
   ✓ Follow redirects
   
   Timing Settings:
   - Request timeout: 30 seconds
   - Delay between requests: 1 second
   - Max retries: 3
   ```

4. **Execute Test Case**
   - Click "Execute Test Case"
   - Monitor real-time progress

#### Flow-Wide Replay

1. **Select "Replay Flow"**
2. **Choose Test Cases**
   - Select all or specific test cases to execute
   - Filter by payload category or priority
3. **Batch Execution Settings**
   ```
   Batch Configuration:
   - Concurrent requests: 5
   - Request rate limit: 10 requests/second
   - Failure threshold: 10% (stop if too many failures)
   - Progress reporting: Every 10 requests
   ```

4. **Start Batch Execution**
   - Monitor overall progress
   - View real-time results as they complete

### Monitoring Execution

**Real-Time Progress:**
- Progress bar showing completion percentage
- Current request being executed
- Success/failure counts
- Estimated time remaining

**Live Results:**
- Anomalies detected in real-time
- Response time statistics
- Error rates and failure analysis
- Performance metrics

**Execution Logs:**
- Detailed request/response logs
- Error messages and debugging information
- Timing and performance data
- Network-related issues

### Handling Execution Issues

**Common Problems:**

1. **Network Timeouts**
   - Increase timeout values
   - Check network connectivity
   - Verify target application availability

2. **Authentication Failures**
   - Refresh authentication tokens
   - Verify session validity
   - Update authentication headers

3. **Rate Limiting**
   - Reduce concurrent request count
   - Increase delays between requests
   - Implement exponential backoff

4. **Application Errors**
   - Check application logs
   - Verify request format and parameters
   - Test with original requests first

**Troubleshooting Steps:**
1. Test original requests manually
2. Verify network connectivity
3. Check authentication status
4. Review request formatting
5. Examine application logs
6. Adjust execution parameters

## 🔍 Analysis Results

The analysis engine examines response differences to identify potential security vulnerabilities.

### Understanding Anomaly Types

#### Status Code Anomalies
**Description**: Unexpected HTTP status codes in responses
**Examples**:
- Original request returns 401 (Unauthorized), modified request returns 200 (Success)
- Authentication bypass detected
- Authorization control failure

**Risk Assessment**:
- High risk if authentication/authorization bypass
- Medium risk for unexpected access patterns
- Low risk for minor status variations

#### Content Length Anomalies
**Description**: Significant differences in response content size
**Examples**:
- Modified request returns much more data (information disclosure)
- Empty responses when content expected (denial of service)
- Unexpected content variations

**Risk Assessment**:
- High risk for information disclosure
- Medium risk for data manipulation
- Low risk for minor content variations

#### Response Time Anomalies
**Description**: Unusual response timing patterns
**Examples**:
- Extremely slow responses (potential DoS)
- Unusually fast responses (caching bypass)
- Timing-based information disclosure

**Risk Assessment**:
- Medium risk for timing attacks
- Low to medium risk for performance issues
- High risk if timing reveals sensitive information

#### Business Logic Anomalies
**Description**: Application-specific logic violations
**Examples**:
- Price manipulation successful
- Quantity limits bypassed
- Workflow steps skipped
- Privilege escalation achieved

**Risk Assessment**:
- Critical risk for financial manipulation
- High risk for privilege escalation
- Medium to high risk for workflow bypass

### Viewing Analysis Results

#### Results Dashboard

1. **Navigate to Analysis Results**
2. **Overview Statistics**
   ```
   Summary:
   - Total Test Cases: 150
   - Anomalies Detected: 23
   - Critical Issues: 3
   - High Risk Issues: 8
   - Medium Risk Issues: 10
   - Low Risk Issues: 2
   
   Risk Score: 7.2/10 (High Risk)
   ```

3. **Severity Breakdown**
   - Visual charts showing anomaly distribution
   - Trend analysis over time
   - Comparison with previous tests

#### Detailed Anomaly Review

**Anomaly List View:**
- Sortable table of all detected anomalies
- Filter by severity, type, or confidence score
- Quick actions for each anomaly

**Individual Anomaly Details:**
```
Anomaly ID: ANO-2025-001
Type: Unauthorized Access
Severity: Critical
Confidence Score: 0.92

Description:
Authentication bypass detected in user profile endpoint. Modified request with invalid token successfully accessed user data.

Original Request:
GET /api/user/profile
Authorization: Bearer invalid_token_here
Response: 401 Unauthorized

Modified Request:
GET /api/user/profile
Authorization: Bearer modified_token_here
Response: 200 OK (User data returned)

Recommendation:
Implement proper token validation and ensure all authentication checks are performed consistently.
```

### Filtering and Searching

**Filter Options:**
- **Severity**: Critical, High, Medium, Low, Info
- **Type**: Unauthorized Access, Parameter Tampering, etc.
- **Confidence**: High (>0.8), Medium (0.5-0.8), Low (<0.5)
- **Vulnerability Status**: Confirmed, Potential, False Positive
- **Date Range**: Last 24 hours, Week, Month, Custom

**Search Functionality:**
- Search by anomaly description
- Filter by request URL patterns
- Find specific parameter names
- Search response content patterns

### Anomaly Management

**Marking False Positives:**
1. Review anomaly details carefully
2. Verify if the behavior is actually expected
3. Mark as "False Positive" if not a real issue
4. Add notes explaining why it's not a vulnerability

**Confirming Vulnerabilities:**
1. Manually verify the vulnerability exists
2. Test exploitation scenarios
3. Mark as "Confirmed Vulnerability"
4. Add exploitation details and impact assessment

**Adding Notes and Comments:**
- Document investigation findings
- Add remediation suggestions
- Include references to similar issues
- Track remediation progress

## 📊 Reporting and Analytics

Generate comprehensive reports for technical teams and management stakeholders.

### Report Types

#### Executive Summary
**Audience**: Management, executives, decision makers
**Content**:
- High-level risk assessment
- Key findings and recommendations
- Business impact analysis
- Remediation priorities

**Format**: Clean, visual presentation with charts and graphs

#### Technical Report
**Audience**: Developers, security engineers, technical teams
**Content**:
- Detailed vulnerability descriptions
- Proof-of-concept examples
- Technical remediation steps
- Code-level recommendations

**Format**: Comprehensive technical documentation

#### Compliance Report
**Audience**: Compliance officers, auditors
**Content**:
- Regulatory compliance status
- Security control effectiveness
- Risk management metrics
- Audit trail documentation

**Format**: Structured compliance framework alignment

### Generating Reports

#### HTML Reports

1. **Navigate to Reports Section**
2. **Select Flow for Reporting**
3. **Choose "Generate HTML Report"**
4. **Configure Report Options**
   ```
   Report Configuration:
   ✓ Include executive summary
   ✓ Detailed technical findings
   ✓ Risk assessment charts
   ✓ Remediation recommendations
   ✓ Appendix with raw data
   
   Branding Options:
   - Company logo
   - Custom color scheme
   - Report title and subtitle
   ```

5. **Generate and Download**
   - Click "Generate Report"
   - Download professional HTML report
   - Share with stakeholders

#### JSON Data Export

1. **Select "Generate JSON Report"**
2. **Configure Data Export**
   ```
   Export Options:
   ✓ Complete anomaly data
   ✓ Request/response details
   ✓ Analysis metadata
   ✓ Risk scoring data
   ✓ Trend analysis
   ```

3. **Download JSON File**
   - Machine-readable format
   - Integration with other tools
   - Custom analysis and visualization

#### Executive Dashboard

**Real-Time Metrics:**
- Current risk score and trend
- Recent anomaly discoveries
- Testing coverage statistics
- Remediation progress tracking

**Visual Analytics:**
- Risk distribution charts
- Anomaly timeline graphs
- Severity trend analysis
- Comparative flow analysis

### Advanced Analytics

#### Trend Analysis
- Track security posture over time
- Identify improvement or degradation patterns
- Compare different application versions
- Monitor remediation effectiveness

#### Comparative Analysis
- Compare multiple flows or applications
- Benchmark security across different systems
- Identify common vulnerability patterns
- Prioritize remediation efforts

#### Risk Scoring
- Automated risk calculation based on multiple factors
- Customizable risk scoring algorithms
- Business impact weighting
- Confidence-adjusted scoring

### Report Customization

**Custom Templates:**
- Create organization-specific report templates
- Include company branding and styling
- Customize content sections and layout
- Define standard reporting formats

**Automated Reporting:**
- Schedule regular report generation
- Email reports to stakeholders
- Integration with ticketing systems
- Automated remediation tracking

## 🔧 Advanced Features

### Custom Detection Rules

Create custom anomaly detection rules for your specific application:

```python
# Custom detection rule example
def detect_price_manipulation(original_response, modified_response, test_case):
    """Detect successful price manipulation attempts."""
    
    if test_case.category == 'parameter' and 'price' in test_case.description.lower():
        # Check if modified request with negative price succeeded
        if (original_response.status_code == 400 and 
            modified_response.status_code == 200):
            return AnomalyInfo(
                type='price_manipulation',
                severity='Critical',
                description='Negative price value accepted by application',
                confidence_score=0.95,
                is_potential_vulnerability=True,
                vulnerability_type='parameter_tampering'
            )
    return None
```

### Integration with CI/CD

Integrate anomaly detection into your development pipeline:

```yaml
# GitHub Actions example
name: Security Testing
on: [push, pull_request]

jobs:
  security-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Anomaly Detection
        run: |
          # Start application
          docker-compose up -d
          
          # Run security tests
          python scripts/automated_testing.py
          
          # Generate report
          python scripts/generate_report.py
          
          # Fail if critical issues found
          python scripts/check_results.py
```

### API Integration

Use the REST API for custom integrations:

```python
import requests

# Create flow via API
flow_data = {
    "name": "Automated Security Test",
    "description": "CI/CD security testing",
    "target_domain": "api.myapp.com"
}

response = requests.post("http://localhost:5000/api/flows", json=flow_data)
flow_id = response.json()["flow_id"]

# Add requests programmatically
request_data = {
    "method": "POST",
    "url": "https://api.myapp.com/users",
    "headers": {"Content-Type": "application/json"},
    "body": '{"username": "test", "role": "user"}'
}

requests.post(f"http://localhost:5000/api/recording/request", json=request_data)

# Generate and execute tests
requests.post(f"http://localhost:5000/api/payloads/generate/flow/{flow_id}")
requests.post(f"http://localhost:5000/api/replay/flow/{flow_id}")

# Get results
results = requests.get(f"http://localhost:5000/api/analysis/anomalies/{flow_id}")
```

## 🎓 Best Practices

### Testing Strategy

**Comprehensive Coverage:**
- Test all user roles and permission levels
- Include both positive and negative test cases
- Cover complete business workflows
- Test edge cases and boundary conditions

**Iterative Testing:**
- Start with core functionality
- Gradually expand test coverage
- Regular testing throughout development
- Continuous monitoring in production

**Risk-Based Approach:**
- Prioritize high-value targets
- Focus on critical business logic
- Test financial and sensitive operations first
- Consider business impact in testing decisions

### Security Considerations

**Safe Testing:**
- Use dedicated test environments
- Avoid testing on production systems
- Implement proper access controls
- Monitor for unintended side effects

**Data Protection:**
- Use synthetic test data
- Avoid real user credentials
- Implement data masking
- Secure test result storage

### Performance Optimization

**Efficient Testing:**
- Optimize payload generation
- Use parallel execution wisely
- Implement smart retry logic
- Monitor resource usage

**Scalability:**
- Design for large-scale testing
- Implement proper caching
- Use database optimization
- Plan for growth

## 🆘 Troubleshooting

### Common Issues and Solutions

**Issue: No anomalies detected**
- Verify payload generation is working
- Check if requests are executing successfully
- Review detection rule configuration
- Ensure baseline requests are representative

**Issue: Too many false positives**
- Adjust confidence thresholds
- Refine detection rules
- Improve baseline request quality
- Add application-specific filters

**Issue: Performance problems**
- Reduce concurrent request count
- Optimize database queries
- Implement request caching
- Monitor system resources

**Issue: Authentication failures**
- Refresh authentication tokens
- Verify session management
- Check token expiration handling
- Update authentication headers

### Getting Help

- Review the [FAQ](faq.md) for common questions
- Check the [troubleshooting guide](troubleshooting.md)
- Contact support team
- Join the community forum

---

**Happy Testing!** 🛡️

You're now equipped to conduct comprehensive business logic security testing. Remember to start small, iterate frequently, and always prioritize the security of your testing environment.

