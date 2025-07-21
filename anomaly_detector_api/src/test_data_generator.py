"""
Test data generator for comprehensive testing of the anomaly detection system.
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import asdict

from src.models import (
    FlowInfo, RequestInfo, TestCaseInfo, ReplayedResponseInfo, 
    AnomalyInfo, SessionInfo
)


class TestDataGenerator:
    """Generate realistic test data for testing purposes."""
    
    def __init__(self):
        self.sample_domains = [
            'api.example-shop.com',
            'secure.banking-app.com',
            'api.social-network.com',
            'backend.healthcare-system.com',
            'api.fintech-startup.com'
        ]
        
        self.sample_endpoints = [
            '/api/v1/users',
            '/api/v1/products',
            '/api/v1/orders',
            '/api/v1/payments',
            '/api/v1/auth/login',
            '/api/v1/auth/logout',
            '/api/v1/profile',
            '/api/v1/admin/users',
            '/api/v1/admin/reports',
            '/api/v1/transactions'
        ]
        
        self.sample_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        
        self.vulnerability_types = [
            'unauthorized_access',
            'privilege_escalation', 
            'parameter_tampering',
            'sequence_manipulation'
        ]
        
        self.anomaly_types = [
            'status_code_anomaly',
            'content_length_anomaly',
            'response_time_anomaly',
            'unauthorized_access',
            'privilege_escalation',
            'parameter_tampering',
            'sequence_manipulation'
        ]
        
        self.severities = ['Critical', 'High', 'Medium', 'Low', 'Info']
    
    def generate_flow(self, flow_id: int = None) -> FlowInfo:
        """Generate a realistic flow for testing."""
        if flow_id is None:
            flow_id = random.randint(1, 1000)
        
        domain = random.choice(self.sample_domains)
        flow_names = [
            f"E-commerce API Security Test - {domain}",
            f"Banking API Vulnerability Assessment - {domain}",
            f"Social Media API Security Audit - {domain}",
            f"Healthcare API Compliance Test - {domain}",
            f"Fintech API Security Review - {domain}"
        ]
        
        descriptions = [
            "Comprehensive security testing of API endpoints including authentication bypass and privilege escalation",
            "Business logic vulnerability assessment focusing on parameter tampering and sequence manipulation",
            "Security audit of critical API endpoints with emphasis on unauthorized access detection",
            "Compliance-focused security testing for healthcare data protection requirements",
            "Financial services API security review with focus on transaction integrity"
        ]
        
        return FlowInfo(
            flow_id=flow_id,
            name=random.choice(flow_names),
            description=random.choice(descriptions),
            target_domain=domain,
            request_count=random.randint(5, 50),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        )
    
    def generate_request(self, flow_id: int, request_id: int = None) -> RequestInfo:
        """Generate a realistic HTTP request for testing."""
        if request_id is None:
            request_id = random.randint(1, 10000)
        
        method = random.choice(self.sample_methods)
        endpoint = random.choice(self.sample_endpoints)
        
        # Generate realistic headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*'
        }
        
        if method in ['POST', 'PUT', 'PATCH']:
            headers['Content-Length'] = str(random.randint(100, 2000))
        
        if random.random() > 0.3:  # 70% chance of having auth header
            headers['Authorization'] = f'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{"x" * 50}'
        
        # Generate realistic body for POST/PUT requests
        body = None
        if method in ['POST', 'PUT', 'PATCH']:
            if 'users' in endpoint:
                body = json.dumps({
                    'username': f'user_{random.randint(1, 1000)}',
                    'email': f'user{random.randint(1, 1000)}@example.com',
                    'role': random.choice(['user', 'admin', 'moderator'])
                })
            elif 'orders' in endpoint:
                body = json.dumps({
                    'product_id': random.randint(1, 100),
                    'quantity': random.randint(1, 10),
                    'price': round(random.uniform(10.0, 500.0), 2)
                })
            elif 'payments' in endpoint:
                body = json.dumps({
                    'amount': round(random.uniform(1.0, 1000.0), 2),
                    'currency': 'USD',
                    'payment_method': random.choice(['credit_card', 'paypal', 'bank_transfer'])
                })
        
        return RequestInfo(
            request_id=request_id,
            flow_id=flow_id,
            method=method,
            url=f"https://{random.choice(self.sample_domains)}{endpoint}",
            headers=json.dumps(headers),
            body=body,
            timestamp=datetime.now() - timedelta(minutes=random.randint(0, 1440))
        )
    
    def generate_test_case(self, request_id: int, test_case_id: int = None) -> TestCaseInfo:
        """Generate a test case for a request."""
        if test_case_id is None:
            test_case_id = random.randint(1, 100000)
        
        categories = ['string', 'auth', 'parameter', 'sequence']
        types = ['boundary', 'injection', 'bypass', 'manipulation']
        
        category = random.choice(categories)
        test_type = random.choice(types)
        
        descriptions = {
            'string': [
                'Testing string boundary conditions with oversized input',
                'SQL injection attempt in string parameters',
                'XSS payload injection in text fields',
                'Unicode and special character handling test'
            ],
            'auth': [
                'Authentication bypass attempt using modified tokens',
                'Session hijacking test with manipulated cookies',
                'Authorization escalation test with role modification',
                'Token expiration and refresh mechanism test'
            ],
            'parameter': [
                'Parameter tampering with modified values',
                'Hidden parameter discovery and manipulation',
                'Type confusion attack with parameter types',
                'Parameter pollution attack with duplicate parameters'
            ],
            'sequence': [
                'Workflow sequence manipulation test',
                'State transition bypass attempt',
                'Race condition exploitation test',
                'Business logic sequence violation test'
            ]
        }
        
        return TestCaseInfo(
            test_case_id=test_case_id,
            request_id=request_id,
            flow_id=random.randint(1, 10),
            category=category,
            type=test_type,
            description=random.choice(descriptions[category]),
            modified_url=f"https://api.example.com/test?param={random.randint(1, 1000)}",
            modified_headers=json.dumps({'X-Test': 'modified'}),
            modified_body='{"test": "modified"}' if random.random() > 0.5 else None,
            timestamp=datetime.now() - timedelta(minutes=random.randint(0, 60))
        )
    
    def generate_replayed_response(self, test_case_id: int, response_id: int = None) -> ReplayedResponseInfo:
        """Generate a replayed response for testing."""
        if response_id is None:
            response_id = random.randint(1, 100000)
        
        status_codes = [200, 201, 400, 401, 403, 404, 500, 502, 503]
        status_code = random.choice(status_codes)
        
        # Generate realistic response content
        if status_code == 200:
            content = json.dumps({
                'success': True,
                'data': {'id': random.randint(1, 1000), 'status': 'active'},
                'message': 'Request processed successfully'
            })
        elif status_code in [400, 401, 403]:
            content = json.dumps({
                'error': 'Request failed',
                'code': status_code,
                'message': 'Authentication or authorization failed'
            })
        else:
            content = json.dumps({
                'error': 'Server error',
                'code': status_code,
                'message': 'Internal server error occurred'
            })
        
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': str(len(content)),
            'Server': 'nginx/1.18.0',
            'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        }
        
        return ReplayedResponseInfo(
            response_id=response_id,
            test_case_id=test_case_id,
            status_code=status_code,
            headers=json.dumps(headers),
            content=content,
            content_length=len(content),
            response_time_ms=random.randint(50, 2000),
            timestamp=datetime.now() - timedelta(minutes=random.randint(0, 30))
        )
    
    def generate_anomaly(self, test_case_id: int, anomaly_id: int = None) -> AnomalyInfo:
        """Generate a realistic anomaly for testing."""
        if anomaly_id is None:
            anomaly_id = random.randint(1, 100000)
        
        anomaly_type = random.choice(self.anomaly_types)
        severity = random.choice(self.severities)
        
        # Adjust probability of vulnerability based on severity
        is_vulnerability = (
            (severity == 'Critical' and random.random() > 0.2) or
            (severity == 'High' and random.random() > 0.4) or
            (severity == 'Medium' and random.random() > 0.7) or
            (severity == 'Low' and random.random() > 0.9)
        )
        
        vulnerability_type = None
        if is_vulnerability:
            vulnerability_type = random.choice(self.vulnerability_types)
        
        descriptions = {
            'status_code_anomaly': [
                'Unexpected status code returned for authenticated request',
                'Status code differs significantly from baseline response',
                'Error status code returned for valid request parameters'
            ],
            'content_length_anomaly': [
                'Response content length varies significantly from expected',
                'Unusually large response content detected',
                'Empty response when content was expected'
            ],
            'response_time_anomaly': [
                'Response time significantly exceeds baseline threshold',
                'Unusually fast response time may indicate caching bypass',
                'Timeout occurred during request processing'
            ],
            'unauthorized_access': [
                'Successful access to protected resource without proper authentication',
                'Bypassed authorization controls detected',
                'Access granted with invalid or expired credentials'
            ],
            'privilege_escalation': [
                'User gained access to higher privilege functionality',
                'Role-based access control bypass detected',
                'Administrative functions accessible to regular user'
            ],
            'parameter_tampering': [
                'Modified parameters accepted without proper validation',
                'Price manipulation attack successful',
                'User ID parameter tampering allowed unauthorized access'
            ],
            'sequence_manipulation': [
                'Business logic sequence bypassed successfully',
                'Workflow state manipulation detected',
                'Required steps in process were skipped'
            ]
        }
        
        confidence_score = random.uniform(0.3, 1.0)
        if severity in ['Critical', 'High']:
            confidence_score = random.uniform(0.7, 1.0)
        
        return AnomalyInfo(
            anomaly_id=anomaly_id,
            test_case_id=test_case_id,
            type=anomaly_type,
            severity=severity,
            description=random.choice(descriptions[anomaly_type]),
            confidence_score=confidence_score,
            is_potential_vulnerability=is_vulnerability,
            vulnerability_type=vulnerability_type,
            original_status=random.choice([200, 201, 400, 401]),
            replayed_status=random.choice([200, 201, 400, 401, 403, 500]),
            original_content_length=random.randint(100, 5000),
            replayed_content_length=random.randint(100, 5000),
            created_timestamp=datetime.now() - timedelta(minutes=random.randint(0, 120))
        )
    
    def generate_session_info(self, flow_id: int) -> SessionInfo:
        """Generate session information for testing."""
        return SessionInfo(
            flow_id=flow_id,
            is_recording=random.choice([True, False]),
            start_time=datetime.now() - timedelta(hours=random.randint(1, 24)),
            request_count=random.randint(0, 100)
        )
    
    def generate_complete_test_scenario(self, num_flows: int = 3, num_requests_per_flow: int = 10) -> Dict[str, List[Dict]]:
        """Generate a complete test scenario with multiple flows and related data."""
        scenario = {
            'flows': [],
            'requests': [],
            'test_cases': [],
            'responses': [],
            'anomalies': [],
            'sessions': []
        }
        
        for flow_idx in range(num_flows):
            flow_id = flow_idx + 1
            flow = self.generate_flow(flow_id)
            scenario['flows'].append(asdict(flow))
            
            # Generate session info
            session = self.generate_session_info(flow_id)
            scenario['sessions'].append(asdict(session))
            
            # Generate requests for this flow
            for req_idx in range(num_requests_per_flow):
                request_id = flow_idx * num_requests_per_flow + req_idx + 1
                request = self.generate_request(flow_id, request_id)
                scenario['requests'].append(asdict(request))
                
                # Generate test cases for this request
                num_test_cases = random.randint(2, 5)
                for tc_idx in range(num_test_cases):
                    test_case_id = request_id * 10 + tc_idx + 1
                    test_case = self.generate_test_case(request_id, test_case_id)
                    scenario['test_cases'].append(asdict(test_case))
                    
                    # Generate response for this test case
                    response = self.generate_replayed_response(test_case_id)
                    scenario['responses'].append(asdict(response))
                    
                    # Generate anomaly (30% chance)
                    if random.random() > 0.7:
                        anomaly = self.generate_anomaly(test_case_id)
                        scenario['anomalies'].append(asdict(anomaly))
        
        return scenario
    
    def save_test_scenario(self, scenario: Dict[str, List[Dict]], filename: str):
        """Save test scenario to JSON file."""
        with open(filename, 'w') as f:
            json.dump(scenario, indent=2, default=str, fp=f)
    
    def load_test_scenario(self, filename: str) -> Dict[str, List[Dict]]:
        """Load test scenario from JSON file."""
        with open(filename, 'r') as f:
            return json.load(f)


# Convenience functions for testing
def create_test_data_generator() -> TestDataGenerator:
    """Factory function to create test data generator."""
    return TestDataGenerator()


def generate_sample_data(output_file: str = 'test_scenario.json'):
    """Generate and save sample test data."""
    generator = TestDataGenerator()
    scenario = generator.generate_complete_test_scenario(num_flows=5, num_requests_per_flow=8)
    generator.save_test_scenario(scenario, output_file)
    return scenario


if __name__ == '__main__':
    # Generate sample data when run directly
    print("Generating sample test data...")
    scenario = generate_sample_data()
    print(f"Generated test scenario with:")
    print(f"  - {len(scenario['flows'])} flows")
    print(f"  - {len(scenario['requests'])} requests")
    print(f"  - {len(scenario['test_cases'])} test cases")
    print(f"  - {len(scenario['responses'])} responses")
    print(f"  - {len(scenario['anomalies'])} anomalies")
    print("Test data saved to test_scenario.json")

