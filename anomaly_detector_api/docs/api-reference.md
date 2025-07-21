# API Reference

Complete reference documentation for the Business Logic Anomaly Detector REST API.

## 📋 Overview

The Business Logic Anomaly Detector provides a comprehensive REST API for programmatic access to all platform functionality. This API enables integration with CI/CD pipelines, custom tooling, and automated security testing workflows.

### Base URL
```
http://localhost:5000/api
```

### Authentication
Currently, the API does not require authentication for development/testing purposes. For production deployments, implement appropriate authentication mechanisms such as:
- API Keys
- JWT Tokens
- OAuth 2.0
- Basic Authentication

### Content Type
All API endpoints accept and return JSON data unless otherwise specified.

```http
Content-Type: application/json
Accept: application/json
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Operation completed successfully"
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "code": 400,
  "details": {
    // Additional error details
  }
}
```

#### List Response
```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

## 🔄 Flow Management

Flows represent complete security testing sessions for specific applications or features.

### List Flows

Retrieve all testing flows with optional filtering and pagination.

```http
GET /api/flows
```

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Items per page (default: 20, max: 100)
- `sort_by` (string, optional): Sort field (`name`, `created_at`, `updated_at`)
- `sort_order` (string, optional): Sort direction (`asc`, `desc`)
- `search` (string, optional): Search in flow names and descriptions

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/flows?page=1&per_page=10&sort_by=created_at&sort_order=desc"
```

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "flow_id": 1,
      "name": "E-commerce API Security Test",
      "description": "Comprehensive security testing of shopping cart functionality",
      "target_domain": "api.shop.example.com",
      "request_count": 15,
      "created_at": "2025-01-20T10:30:00Z",
      "updated_at": "2025-01-20T14:45:00Z",
      "status": "active"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 10,
  "has_next": false,
  "has_prev": false
}
```

### Create Flow

Create a new testing flow.

```http
POST /api/flows
```

**Request Body:**
```json
{
  "name": "E-commerce API Security Test",
  "description": "Comprehensive security testing of shopping cart functionality",
  "target_domain": "api.shop.example.com"
}
```

**Validation Rules:**
- `name`: Required, 1-255 characters
- `description`: Required, 1-1000 characters
- `target_domain`: Required, valid domain format

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/flows" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Banking API Security Test",
    "description": "Security testing of banking transaction endpoints",
    "target_domain": "api.bank.example.com"
  }'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow_id": 2,
    "name": "Banking API Security Test",
    "description": "Security testing of banking transaction endpoints",
    "target_domain": "api.bank.example.com",
    "request_count": 0,
    "created_at": "2025-01-20T15:00:00Z",
    "updated_at": "2025-01-20T15:00:00Z",
    "status": "created"
  },
  "message": "Flow created successfully"
}
```

### Get Flow Details

Retrieve detailed information about a specific flow.

```http
GET /api/flows/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/flows/1"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow_id": 1,
    "name": "E-commerce API Security Test",
    "description": "Comprehensive security testing of shopping cart functionality",
    "target_domain": "api.shop.example.com",
    "request_count": 15,
    "test_case_count": 45,
    "anomaly_count": 8,
    "last_execution": "2025-01-20T14:30:00Z",
    "risk_score": 6.5,
    "created_at": "2025-01-20T10:30:00Z",
    "updated_at": "2025-01-20T14:45:00Z",
    "status": "completed"
  }
}
```

### Update Flow

Update an existing flow's details.

```http
PUT /api/flows/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Request Body:**
```json
{
  "name": "Updated Flow Name",
  "description": "Updated description",
  "target_domain": "updated.domain.com"
}
```

### Delete Flow

Delete a flow and all associated data.

```http
DELETE /api/flows/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Request:**
```bash
curl -X DELETE "http://localhost:5000/api/flows/1"
```

**Example Response:**
```json
{
  "success": true,
  "message": "Flow deleted successfully"
}
```

### Select Active Flow

Set a flow as the active flow for recording and testing operations.

```http
POST /api/flows/{flow_id}/select
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

## 🎙️ Recording Management

Recording functionality captures HTTP requests for security testing.

### Get Recording Status

Check the current recording status and active flow information.

```http
GET /api/recording/status
```

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/recording/status"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "is_recording": true,
    "active_flow_id": 1,
    "active_flow_name": "E-commerce API Security Test",
    "session_start_time": "2025-01-20T15:30:00Z",
    "requests_recorded": 12,
    "last_request_time": "2025-01-20T15:45:00Z"
  }
}
```

### Start Recording

Begin a new recording session for the active flow.

```http
POST /api/recording/start
```

**Request Body:**
```json
{
  "flow_id": 1
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/recording/start" \
  -H "Content-Type: application/json" \
  -d '{"flow_id": 1}'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "rec_2025012015300001",
    "flow_id": 1,
    "started_at": "2025-01-20T15:30:00Z"
  },
  "message": "Recording started successfully"
}
```

### Stop Recording

Stop the current recording session.

```http
POST /api/recording/stop
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/recording/stop"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "rec_2025012015300001",
    "duration_seconds": 900,
    "requests_recorded": 15,
    "stopped_at": "2025-01-20T15:45:00Z"
  },
  "message": "Recording stopped successfully"
}
```

### Add Request to Recording

Add an HTTP request to the current recording session.

```http
POST /api/recording/request
```

**Request Body:**
```json
{
  "method": "POST",
  "url": "https://api.shop.example.com/cart/add",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs...",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  "body": {
    "product_id": 12345,
    "quantity": 2,
    "user_id": 67890
  }
}
```

**Validation Rules:**
- `method`: Required, valid HTTP method
- `url`: Required, valid URL format
- `headers`: Optional, object with string values
- `body`: Optional, any valid JSON

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/recording/request" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "url": "https://api.shop.example.com/products/12345",
    "headers": {
      "Authorization": "Bearer token123",
      "Accept": "application/json"
    }
  }'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "request_id": 101,
    "flow_id": 1,
    "method": "GET",
    "url": "https://api.shop.example.com/products/12345",
    "recorded_at": "2025-01-20T15:35:00Z"
  },
  "message": "Request added successfully"
}
```

### Get Recorded Requests

Retrieve all requests recorded for a specific flow.

```http
GET /api/recording/requests/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Query Parameters:**
- `page` (integer, optional): Page number
- `per_page` (integer, optional): Items per page
- `method` (string, optional): Filter by HTTP method
- `url_pattern` (string, optional): Filter by URL pattern

## 🎯 Payload Generation

Generate test payloads for security testing based on recorded requests.

### Generate Payloads for Request

Generate test payloads for a specific request.

```http
POST /api/payloads/generate/request/{request_id}
```

**Path Parameters:**
- `request_id` (integer): Unique request identifier

**Request Body:**
```json
{
  "categories": ["string", "auth", "parameter", "sequence"],
  "options": {
    "string_payloads": {
      "include_boundary_tests": true,
      "include_injection_tests": true,
      "max_string_length": 10000
    },
    "auth_payloads": {
      "include_token_manipulation": true,
      "include_privilege_escalation": true
    },
    "parameter_payloads": {
      "include_type_confusion": true,
      "include_value_tampering": true
    },
    "sequence_payloads": {
      "include_workflow_manipulation": true,
      "include_state_bypass": true
    }
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/payloads/generate/request/101" \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["auth", "parameter"],
    "options": {
      "auth_payloads": {
        "include_token_manipulation": true
      }
    }
  }'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "request_id": 101,
    "payloads_generated": 15,
    "categories": ["auth", "parameter"],
    "test_cases": [
      {
        "test_case_id": 1001,
        "category": "auth",
        "type": "token_manipulation",
        "description": "Modified JWT token with different user ID",
        "confidence_level": "high"
      },
      {
        "test_case_id": 1002,
        "category": "parameter",
        "type": "value_tampering",
        "description": "Modified product_id parameter with negative value",
        "confidence_level": "medium"
      }
    ]
  },
  "message": "Payloads generated successfully"
}
```

### Generate Payloads for Flow

Generate test payloads for all requests in a flow.

```http
POST /api/payloads/generate/flow/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Request Body:**
```json
{
  "request_ids": [101, 102, 103],
  "categories": ["string", "auth", "parameter"],
  "batch_options": {
    "max_payloads_per_request": 20,
    "priority_requests": [101, 102]
  }
}
```

### Get Payload Generation Rules

Retrieve current payload generation rules and configuration.

```http
GET /api/payloads/rules
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "string_rules": [
      {
        "type": "boundary_test",
        "patterns": ["", "A" * 10000, "null", "undefined"],
        "description": "Test string boundary conditions"
      }
    ],
    "auth_rules": [
      {
        "type": "token_manipulation",
        "patterns": ["expired_token", "invalid_signature", "modified_payload"],
        "description": "Test authentication token handling"
      }
    ],
    "parameter_rules": [
      {
        "type": "value_tampering",
        "patterns": ["-1", "0", "999999", "null"],
        "description": "Test parameter validation"
      }
    ]
  }
}
```

### Update Payload Generation Rules

Update payload generation rules and configuration.

```http
PUT /api/payloads/rules
```

**Request Body:**
```json
{
  "string_rules": [
    {
      "type": "custom_boundary",
      "patterns": ["custom_test_value"],
      "description": "Custom string test"
    }
  ]
}
```

## 🔄 Replay Execution

Execute test cases by replaying original and modified requests.

### Replay Flow

Execute all test cases for a specific flow.

```http
POST /api/replay/flow/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Request Body:**
```json
{
  "execution_options": {
    "concurrent_requests": 5,
    "request_timeout": 30,
    "retry_attempts": 3,
    "delay_between_requests": 1000,
    "include_response_body": true,
    "follow_redirects": true
  },
  "filters": {
    "categories": ["auth", "parameter"],
    "severity_levels": ["high", "critical"],
    "test_case_ids": [1001, 1002, 1003]
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:5000/api/replay/flow/1" \
  -H "Content-Type: application/json" \
  -d '{
    "execution_options": {
      "concurrent_requests": 3,
      "request_timeout": 30
    }
  }'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_2025012016000001",
    "flow_id": 1,
    "total_test_cases": 45,
    "estimated_duration": 180,
    "started_at": "2025-01-20T16:00:00Z",
    "status": "running"
  },
  "message": "Flow replay started successfully"
}
```

### Replay Test Case

Execute a specific test case.

```http
POST /api/replay/testcase/{test_case_id}
```

**Path Parameters:**
- `test_case_id` (integer): Unique test case identifier

**Request Body:**
```json
{
  "execution_options": {
    "request_timeout": 30,
    "include_response_body": true,
    "capture_timing": true
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "test_case_id": 1001,
    "execution_id": "exec_tc_2025012016050001",
    "original_response": {
      "status_code": 401,
      "content_length": 45,
      "response_time_ms": 120,
      "headers": {
        "Content-Type": "application/json"
      }
    },
    "modified_response": {
      "status_code": 200,
      "content_length": 1250,
      "response_time_ms": 95,
      "headers": {
        "Content-Type": "application/json"
      }
    },
    "anomalies_detected": 1,
    "executed_at": "2025-01-20T16:05:00Z"
  },
  "message": "Test case executed successfully"
}
```

### Get Replay Status

Check the status of a running replay execution.

```http
GET /api/replay/status/{execution_id}
```

**Path Parameters:**
- `execution_id` (string): Unique execution identifier

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_2025012016000001",
    "flow_id": 1,
    "status": "running",
    "progress": {
      "total_test_cases": 45,
      "completed": 23,
      "failed": 2,
      "remaining": 20,
      "percentage": 51
    },
    "timing": {
      "started_at": "2025-01-20T16:00:00Z",
      "estimated_completion": "2025-01-20T16:03:00Z",
      "elapsed_seconds": 120
    },
    "results": {
      "anomalies_detected": 8,
      "critical_issues": 2,
      "high_issues": 3,
      "medium_issues": 3
    }
  }
}
```

### Stop Replay Execution

Stop a running replay execution.

```http
POST /api/replay/stop/{execution_id}
```

**Path Parameters:**
- `execution_id` (string): Unique execution identifier

## 🔍 Analysis and Results

Analyze replay results and manage detected anomalies.

### Analyze Flow Results

Trigger analysis of replay results for a flow.

```http
POST /api/analysis/flow/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Request Body:**
```json
{
  "analysis_options": {
    "confidence_threshold": 0.7,
    "include_low_severity": false,
    "custom_rules": true,
    "deep_analysis": true
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow_id": 1,
    "analysis_id": "analysis_2025012016100001",
    "anomalies_detected": 12,
    "risk_score": 7.2,
    "analysis_completed_at": "2025-01-20T16:10:00Z"
  },
  "message": "Flow analysis completed successfully"
}
```

### Get Flow Anomalies

Retrieve all anomalies detected for a specific flow.

```http
GET /api/analysis/anomalies/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Query Parameters:**
- `severity` (string, optional): Filter by severity (`critical`, `high`, `medium`, `low`)
- `type` (string, optional): Filter by anomaly type
- `confidence_min` (float, optional): Minimum confidence score (0.0-1.0)
- `status` (string, optional): Filter by status (`new`, `confirmed`, `false_positive`)
- `page` (integer, optional): Page number
- `per_page` (integer, optional): Items per page

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/analysis/anomalies/1?severity=critical&confidence_min=0.8"
```

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "anomaly_id": 2001,
      "test_case_id": 1001,
      "type": "unauthorized_access",
      "severity": "critical",
      "description": "Authentication bypass detected in user profile endpoint",
      "confidence_score": 0.92,
      "is_potential_vulnerability": true,
      "vulnerability_type": "unauthorized_access",
      "original_status": 401,
      "replayed_status": 200,
      "original_content_length": 45,
      "replayed_content_length": 1250,
      "risk_score": 9.2,
      "status": "new",
      "created_at": "2025-01-20T16:05:00Z",
      "request_details": {
        "method": "GET",
        "url": "https://api.shop.example.com/user/profile",
        "modified_headers": {
          "Authorization": "Bearer modified_token"
        }
      }
    }
  ],
  "total": 3,
  "page": 1,
  "per_page": 20
}
```

### Get Anomaly Details

Retrieve detailed information about a specific anomaly.

```http
GET /api/analysis/anomaly/{anomaly_id}
```

**Path Parameters:**
- `anomaly_id` (integer): Unique anomaly identifier

**Example Response:**
```json
{
  "success": true,
  "data": {
    "anomaly_id": 2001,
    "test_case_id": 1001,
    "type": "unauthorized_access",
    "severity": "critical",
    "description": "Authentication bypass detected in user profile endpoint",
    "confidence_score": 0.92,
    "is_potential_vulnerability": true,
    "vulnerability_type": "unauthorized_access",
    "risk_score": 9.2,
    "status": "new",
    "created_at": "2025-01-20T16:05:00Z",
    "original_request": {
      "method": "GET",
      "url": "https://api.shop.example.com/user/profile",
      "headers": {
        "Authorization": "Bearer valid_token"
      }
    },
    "modified_request": {
      "method": "GET",
      "url": "https://api.shop.example.com/user/profile",
      "headers": {
        "Authorization": "Bearer modified_token"
      }
    },
    "original_response": {
      "status_code": 401,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": "{\"error\": \"Unauthorized\"}",
      "content_length": 45,
      "response_time_ms": 120
    },
    "modified_response": {
      "status_code": 200,
      "headers": {
        "Content-Type": "application/json"
      },
      "body": "{\"user_id\": 12345, \"username\": \"john_doe\", \"email\": \"john@example.com\"}",
      "content_length": 1250,
      "response_time_ms": 95
    },
    "recommendations": [
      "Implement proper token validation",
      "Ensure all authentication checks are performed consistently",
      "Add logging for authentication failures"
    ]
  }
}
```

### Update Anomaly Status

Update the status and notes for a specific anomaly.

```http
PUT /api/analysis/anomaly/{anomaly_id}
```

**Path Parameters:**
- `anomaly_id` (integer): Unique anomaly identifier

**Request Body:**
```json
{
  "status": "confirmed",
  "notes": "Verified vulnerability - authentication bypass confirmed in testing",
  "severity": "critical",
  "assigned_to": "security-team@company.com"
}
```

### Get Detection Rules

Retrieve current anomaly detection rules.

```http
GET /api/analysis/rules
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "status_code_rules": [
      {
        "name": "authentication_bypass",
        "description": "Detect authentication bypass attempts",
        "conditions": {
          "original_status": [401, 403],
          "modified_status": [200, 201],
          "confidence_threshold": 0.8
        }
      }
    ],
    "content_length_rules": [
      {
        "name": "information_disclosure",
        "description": "Detect potential information disclosure",
        "conditions": {
          "length_difference_threshold": 500,
          "confidence_threshold": 0.7
        }
      }
    ]
  }
}
```

### Update Detection Rules

Update anomaly detection rules and configuration.

```http
PUT /api/analysis/rules
```

**Request Body:**
```json
{
  "status_code_rules": [
    {
      "name": "custom_bypass_detection",
      "description": "Custom authentication bypass detection",
      "conditions": {
        "original_status": [401],
        "modified_status": [200],
        "confidence_threshold": 0.9
      }
    }
  ]
}
```

## 📊 Reporting and Analytics

Generate comprehensive reports and analytics for security testing results.

### Get Report Summary

Retrieve a summary report for a specific flow.

```http
GET /api/reports/summary/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow": {
      "flow_id": 1,
      "name": "E-commerce API Security Test",
      "description": "Comprehensive security testing of shopping cart functionality",
      "target_domain": "api.shop.example.com",
      "request_count": 15,
      "timestamp": "2025-01-20T10:30:00Z"
    },
    "summary": {
      "total_anomalies": 12,
      "potential_vulnerabilities": 8,
      "risk_score": 7.2,
      "risk_category": "High",
      "severity_breakdown": {
        "Critical": 2,
        "High": 3,
        "Medium": 5,
        "Low": 2
      },
      "type_breakdown": {
        "unauthorized_access": 3,
        "parameter_tampering": 4,
        "privilege_escalation": 2,
        "sequence_manipulation": 3
      },
      "trends": {
        "severity": {
          "counts": {
            "Critical": 2,
            "High": 3,
            "Medium": 5,
            "Low": 2
          },
          "percentages": {
            "Critical": 16.7,
            "High": 25.0,
            "Medium": 41.7,
            "Low": 16.7
          }
        }
      },
      "recommendations": [
        "Immediate security review required - critical vulnerabilities detected",
        "Review and strengthen authentication and authorization controls",
        "Implement robust input validation and parameter verification"
      ]
    },
    "anomalies": [
      {
        "anomaly_id": 2001,
        "type": "unauthorized_access",
        "severity": "critical",
        "description": "Authentication bypass detected in user profile endpoint",
        "confidence_score": 0.92,
        "is_potential_vulnerability": true,
        "created_timestamp": "2025-01-20T16:05:00Z"
      }
    ]
  }
}
```

### Generate HTML Report

Generate a comprehensive HTML report for a flow.

```http
GET /api/reports/html/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Query Parameters:**
- `include_executive_summary` (boolean, optional): Include executive summary (default: true)
- `include_technical_details` (boolean, optional): Include technical details (default: true)
- `include_recommendations` (boolean, optional): Include recommendations (default: true)

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/reports/html/1" \
  -H "Accept: text/html" \
  -o "security_report.html"
```

**Response:**
- Content-Type: `text/html`
- Content-Disposition: `attachment; filename=anomaly_report_flow_1.html`

### Generate JSON Report

Generate a machine-readable JSON report for a flow.

```http
GET /api/reports/json/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Request:**
```bash
curl -X GET "http://localhost:5000/api/reports/json/1" \
  -H "Accept: application/json" \
  -o "security_report.json"
```

**Response:**
- Content-Type: `application/json`
- Content-Disposition: `attachment; filename=anomaly_report_flow_1.json`

### Get Executive Summary

Retrieve an executive summary for dashboard display.

```http
GET /api/reports/executive/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow_name": "E-commerce API Security Test",
    "risk_score": 7.2,
    "risk_category": "High",
    "total_anomalies": 12,
    "critical_issues": 2,
    "vulnerabilities": 8,
    "key_recommendations": [
      "Immediate security review required - critical vulnerabilities detected",
      "Review and strengthen authentication and authorization controls",
      "Implement robust input validation and parameter verification"
    ],
    "last_analyzed": "2025-01-20T16:10:00Z"
  }
}
```

### Get Flow Analytics

Retrieve detailed analytics for a flow.

```http
GET /api/reports/analytics/{flow_id}
```

**Path Parameters:**
- `flow_id` (integer): Unique flow identifier

**Example Response:**
```json
{
  "success": true,
  "data": {
    "flow_id": 1,
    "analytics": {
      "risk_assessment": {
        "score": 7.2,
        "category": "High",
        "factors": {
          "total_anomalies": 12,
          "vulnerabilities": 8,
          "severity_distribution": {
            "Critical": 2,
            "High": 3,
            "Medium": 5,
            "Low": 2
          }
        }
      },
      "trends": {
        "severity": {
          "counts": {
            "Critical": 2,
            "High": 3,
            "Medium": 5,
            "Low": 2
          },
          "percentages": {
            "Critical": 16.7,
            "High": 25.0,
            "Medium": 41.7,
            "Low": 16.7
          },
          "total": 12
        },
        "types": {
          "counts": {
            "unauthorized_access": 3,
            "parameter_tampering": 4,
            "privilege_escalation": 2,
            "sequence_manipulation": 3
          },
          "sorted": [
            ["parameter_tampering", 4],
            ["unauthorized_access", 3],
            ["sequence_manipulation", 3],
            ["privilege_escalation", 2]
          ],
          "most_common": ["parameter_tampering", 4]
        },
        "confidence": {
          "average": 0.78,
          "min": 0.45,
          "max": 0.95,
          "distribution": {
            "high": 6,
            "medium": 4,
            "low": 2
          }
        }
      },
      "recommendations": [
        "Immediate security review required - critical vulnerabilities detected",
        "Review and strengthen authentication and authorization controls",
        "Implement robust input validation and parameter verification"
      ]
    }
  }
}
```

## 📈 System Information

Get system status and configuration information.

### Get System Status

Retrieve current system status and health information.

```http
GET /api/system/status
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime_seconds": 86400,
    "database": {
      "status": "connected",
      "type": "sqlite",
      "version": "3.39.0"
    },
    "statistics": {
      "total_flows": 15,
      "total_requests": 450,
      "total_test_cases": 1350,
      "total_anomalies": 89,
      "active_recordings": 2
    },
    "performance": {
      "avg_response_time_ms": 125,
      "requests_per_minute": 45,
      "memory_usage_mb": 256,
      "cpu_usage_percent": 15.5
    }
  }
}
```

### Get API Configuration

Retrieve current API configuration and limits.

```http
GET /api/system/config
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "api_version": "1.0.0",
    "rate_limits": {
      "requests_per_minute": 1000,
      "concurrent_replays": 10,
      "max_payload_size_mb": 16
    },
    "features": {
      "authentication_required": false,
      "cors_enabled": true,
      "debug_mode": false
    },
    "limits": {
      "max_flows_per_user": 100,
      "max_requests_per_flow": 1000,
      "max_test_cases_per_request": 50,
      "report_retention_days": 90
    }
  }
}
```

## 🔧 Error Handling

### HTTP Status Codes

The API uses standard HTTP status codes to indicate success or failure:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

All error responses follow a consistent format:

```json
{
  "success": false,
  "error": "Validation failed",
  "code": 422,
  "details": {
    "field": "name",
    "message": "Name is required and cannot be empty",
    "value": ""
  },
  "timestamp": "2025-01-20T16:15:00Z",
  "request_id": "req_2025012016150001"
}
```

### Common Error Scenarios

#### Validation Errors (422)
```json
{
  "success": false,
  "error": "Validation failed",
  "code": 422,
  "details": {
    "errors": [
      {
        "field": "name",
        "message": "Name must be between 1 and 255 characters"
      },
      {
        "field": "target_domain",
        "message": "Invalid domain format"
      }
    ]
  }
}
```

#### Resource Not Found (404)
```json
{
  "success": false,
  "error": "Flow not found",
  "code": 404,
  "details": {
    "resource": "flow",
    "id": 999
  }
}
```

#### Rate Limit Exceeded (429)
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "code": 429,
  "details": {
    "limit": 1000,
    "window": "1 minute",
    "retry_after": 60
  }
}
```

## 🔐 Security Considerations

### API Security Best Practices

1. **Authentication**: Implement proper authentication for production use
2. **Authorization**: Ensure users can only access their own resources
3. **Input Validation**: Validate all input data thoroughly
4. **Rate Limiting**: Implement rate limiting to prevent abuse
5. **HTTPS**: Always use HTTPS in production
6. **Logging**: Log all API access for security monitoring

### Production Configuration

```python
# Example production configuration
API_CONFIG = {
    'authentication': {
        'enabled': True,
        'method': 'jwt',
        'secret_key': 'your-secret-key',
        'token_expiry': 3600
    },
    'rate_limiting': {
        'enabled': True,
        'requests_per_minute': 100,
        'burst_limit': 200
    },
    'cors': {
        'enabled': True,
        'allowed_origins': ['https://yourdomain.com'],
        'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE']
    },
    'logging': {
        'level': 'INFO',
        'include_request_body': False,
        'include_response_body': False
    }
}
```

## 📚 SDK and Integration Examples

### Python SDK Example

```python
import requests
from typing import Dict, List, Optional

class AnomalyDetectorClient:
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_flow(self, name: str, description: str, target_domain: str) -> Dict:
        """Create a new testing flow."""
        data = {
            "name": name,
            "description": description,
            "target_domain": target_domain
        }
        response = self.session.post(f"{self.base_url}/flows", json=data)
        response.raise_for_status()
        return response.json()
    
    def add_request(self, method: str, url: str, headers: Dict = None, body: str = None) -> Dict:
        """Add a request to the current recording."""
        data = {
            "method": method,
            "url": url,
            "headers": headers or {},
            "body": body
        }
        response = self.session.post(f"{self.base_url}/recording/request", json=data)
        response.raise_for_status()
        return response.json()
    
    def generate_payloads(self, flow_id: int, categories: List[str] = None) -> Dict:
        """Generate test payloads for a flow."""
        data = {
            "categories": categories or ["string", "auth", "parameter", "sequence"]
        }
        response = self.session.post(f"{self.base_url}/payloads/generate/flow/{flow_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def replay_flow(self, flow_id: int) -> Dict:
        """Execute replay testing for a flow."""
        response = self.session.post(f"{self.base_url}/replay/flow/{flow_id}")
        response.raise_for_status()
        return response.json()
    
    def get_anomalies(self, flow_id: int, severity: str = None) -> Dict:
        """Get anomalies for a flow."""
        params = {}
        if severity:
            params['severity'] = severity
        
        response = self.session.get(f"{self.base_url}/analysis/anomalies/{flow_id}", params=params)
        response.raise_for_status()
        return response.json()

# Usage example
client = AnomalyDetectorClient()

# Create flow
flow = client.create_flow(
    name="API Security Test",
    description="Testing authentication endpoints",
    target_domain="api.example.com"
)

# Add requests
client.add_request(
    method="POST",
    url="https://api.example.com/login",
    headers={"Content-Type": "application/json"},
    body='{"username": "test", "password": "test123"}'
)

# Generate and execute tests
client.generate_payloads(flow['data']['flow_id'])
client.replay_flow(flow['data']['flow_id'])

# Get results
anomalies = client.get_anomalies(flow['data']['flow_id'], severity="critical")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class AnomalyDetectorClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async createFlow(name, description, targetDomain) {
        const response = await this.client.post('/flows', {
            name,
            description,
            target_domain: targetDomain
        });
        return response.data;
    }

    async addRequest(method, url, headers = {}, body = null) {
        const response = await this.client.post('/recording/request', {
            method,
            url,
            headers,
            body
        });
        return response.data;
    }

    async generatePayloads(flowId, categories = ['string', 'auth', 'parameter', 'sequence']) {
        const response = await this.client.post(`/payloads/generate/flow/${flowId}`, {
            categories
        });
        return response.data;
    }

    async replayFlow(flowId) {
        const response = await this.client.post(`/replay/flow/${flowId}`);
        return response.data;
    }

    async getAnomalies(flowId, severity = null) {
        const params = severity ? { severity } : {};
        const response = await this.client.get(`/analysis/anomalies/${flowId}`, { params });
        return response.data;
    }
}

// Usage example
(async () => {
    const client = new AnomalyDetectorClient();
    
    try {
        // Create flow
        const flow = await client.createFlow(
            'API Security Test',
            'Testing authentication endpoints',
            'api.example.com'
        );
        
        // Add request
        await client.addRequest(
            'POST',
            'https://api.example.com/login',
            { 'Content-Type': 'application/json' },
            JSON.stringify({ username: 'test', password: 'test123' })
        );
        
        // Generate and execute tests
        await client.generatePayloads(flow.data.flow_id);
        await client.replayFlow(flow.data.flow_id);
        
        // Get results
        const anomalies = await client.getAnomalies(flow.data.flow_id, 'critical');
        console.log('Critical anomalies found:', anomalies.data.length);
        
    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
})();
```

---

This comprehensive API reference provides all the information needed to integrate with the Business Logic Anomaly Detector programmatically. For additional support or questions, please refer to the main documentation or contact the development team.

