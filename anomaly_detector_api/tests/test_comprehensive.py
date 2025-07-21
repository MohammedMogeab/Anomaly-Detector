"""
Comprehensive test suite for the Business Logic Anomaly Detector.
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models import FlowInfo, RequestInfo, TestCaseInfo, ReplayedResponseInfo, AnomalyInfo
from src.database import DatabaseManager
from src.payload_generation import PayloadGenerator
from src.replay import ReplayManager
from src.analysis import ResponseAnalyzer
from src.recording import RecordingManager
from src.enhanced_reporting import EnhancedReportGenerator, RiskScorer, TrendAnalyzer
from src.advanced_visualizations import VisualizationDataProcessor
from src.test_data_generator import TestDataGenerator


class TestDatabaseManager(unittest.TestCase):
    """Test database operations."""
    
    def setUp(self):
        """Set up test database."""
        self.db_manager = DatabaseManager(":memory:")  # Use in-memory database
        self.test_generator = TestDataGenerator()
    
    def test_flow_operations(self):
        """Test flow CRUD operations."""
        # Create flow
        flow = self.test_generator.generate_flow(1)
        created_flow = self.db_manager.create_flow(flow.name, flow.description, flow.target_domain)
        
        self.assertIsNotNone(created_flow)
        self.assertEqual(created_flow.name, flow.name)
        self.assertEqual(created_flow.description, flow.description)
        
        # Get flow
        retrieved_flow = self.db_manager.get_flow(created_flow.flow_id)
        self.assertIsNotNone(retrieved_flow)
        self.assertEqual(retrieved_flow.flow_id, created_flow.flow_id)
        
        # List flows
        flows = self.db_manager.get_flows()
        self.assertGreater(len(flows), 0)
        self.assertIn(created_flow.flow_id, [f.flow_id for f in flows])
    
    def test_request_operations(self):
        """Test request CRUD operations."""
        # Create flow first
        flow = self.db_manager.create_flow("Test Flow", "Test Description", "example.com")
        
        # Create request
        request = self.test_generator.generate_request(flow.flow_id, 1)
        created_request = self.db_manager.add_request(
            flow.flow_id, request.method, request.url, 
            request.headers, request.body
        )
        
        self.assertIsNotNone(created_request)
        self.assertEqual(created_request.method, request.method)
        self.assertEqual(created_request.url, request.url)
        
        # Get requests for flow
        requests = self.db_manager.get_requests(flow.flow_id)
        self.assertGreater(len(requests), 0)
        self.assertIn(created_request.request_id, [r.request_id for r in requests])
    
    def test_anomaly_operations(self):
        """Test anomaly CRUD operations."""
        # Create test data
        flow = self.db_manager.create_flow("Test Flow", "Test Description", "example.com")
        request = self.db_manager.add_request(flow.flow_id, "GET", "https://example.com/api", "{}", None)
        test_case = self.db_manager.add_test_case(
            request.request_id, flow.flow_id, "auth", "bypass", 
            "Test bypass", "https://example.com/api", "{}", None
        )
        
        # Create anomaly
        anomaly = self.test_generator.generate_anomaly(test_case.test_case_id, 1)
        created_anomaly = self.db_manager.add_anomaly(
            test_case.test_case_id, anomaly.type, anomaly.severity,
            anomaly.description, anomaly.confidence_score,
            anomaly.is_potential_vulnerability, anomaly.vulnerability_type
        )
        
        self.assertIsNotNone(created_anomaly)
        self.assertEqual(created_anomaly.type, anomaly.type)
        self.assertEqual(created_anomaly.severity, anomaly.severity)
        
        # Get anomalies
        anomalies = self.db_manager.get_anomalies(flow.flow_id)
        self.assertGreater(len(anomalies), 0)


class TestPayloadGenerator(unittest.TestCase):
    """Test payload generation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_manager = DatabaseManager(":memory:")
        self.payload_generator = PayloadGenerator(self.db_manager)
        self.test_generator = TestDataGenerator()
    
    def test_string_payload_generation(self):
        """Test string boundary payload generation."""
        request = self.test_generator.generate_request(1, 1)
        
        payloads = self.payload_generator.generate_string_payloads(request)
        
        self.assertIsInstance(payloads, list)
        self.assertGreater(len(payloads), 0)
        
        # Check that payloads have required fields
        for payload in payloads:
            self.assertIn('category', payload)
            self.assertIn('type', payload)
            self.assertIn('description', payload)
            self.assertEqual(payload['category'], 'string')
    
    def test_auth_payload_generation(self):
        """Test authentication bypass payload generation."""
        request = self.test_generator.generate_request(1, 1)
        
        payloads = self.payload_generator.generate_auth_payloads(request)
        
        self.assertIsInstance(payloads, list)
        self.assertGreater(len(payloads), 0)
        
        for payload in payloads:
            self.assertEqual(payload['category'], 'auth')
    
    def test_parameter_payload_generation(self):
        """Test parameter tampering payload generation."""
        request = self.test_generator.generate_request(1, 1)
        
        payloads = self.payload_generator.generate_parameter_payloads(request)
        
        self.assertIsInstance(payloads, list)
        self.assertGreater(len(payloads), 0)
        
        for payload in payloads:
            self.assertEqual(payload['category'], 'parameter')


class TestResponseAnalyzer(unittest.TestCase):
    """Test response analysis functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.db_manager = DatabaseManager(":memory:")
        self.analyzer = ResponseAnalyzer(self.db_manager)
        self.test_generator = TestDataGenerator()
    
    def test_status_code_analysis(self):
        """Test status code anomaly detection."""
        # Create test data
        original_response = Mock()
        original_response.status_code = 200
        original_response.content = b'{"success": true}'
        original_response.headers = {'Content-Type': 'application/json'}
        original_response.elapsed.total_seconds.return_value = 0.5
        
        replayed_response = Mock()
        replayed_response.status_code = 403  # Different status code
        replayed_response.content = b'{"error": "Forbidden"}'
        replayed_response.headers = {'Content-Type': 'application/json'}
        replayed_response.elapsed.total_seconds.return_value = 0.3
        
        test_case = self.test_generator.generate_test_case(1, 1)
        
        anomalies = self.analyzer.analyze_responses(original_response, replayed_response, test_case)
        
        self.assertIsInstance(anomalies, list)
        # Should detect status code anomaly
        status_anomalies = [a for a in anomalies if a.type == 'status_code_anomaly']
        self.assertGreater(len(status_anomalies), 0)
    
    def test_content_length_analysis(self):
        """Test content length anomaly detection."""
        original_response = Mock()
        original_response.status_code = 200
        original_response.content = b'{"data": "short"}'
        original_response.headers = {'Content-Type': 'application/json'}
        original_response.elapsed.total_seconds.return_value = 0.5
        
        replayed_response = Mock()
        replayed_response.status_code = 200
        replayed_response.content = b'{"data": "' + b'x' * 10000 + b'"}'  # Much longer content
        replayed_response.headers = {'Content-Type': 'application/json'}
        replayed_response.elapsed.total_seconds.return_value = 0.5
        
        test_case = self.test_generator.generate_test_case(1, 1)
        
        anomalies = self.analyzer.analyze_responses(original_response, replayed_response, test_case)
        
        # Should detect content length anomaly
        length_anomalies = [a for a in anomalies if a.type == 'content_length_anomaly']
        self.assertGreater(len(length_anomalies), 0)
    
    def test_unauthorized_access_detection(self):
        """Test unauthorized access detection."""
        original_response = Mock()
        original_response.status_code = 401  # Unauthorized
        original_response.content = b'{"error": "Unauthorized"}'
        original_response.headers = {'Content-Type': 'application/json'}
        original_response.elapsed.total_seconds.return_value = 0.2
        
        replayed_response = Mock()
        replayed_response.status_code = 200  # Successful access
        replayed_response.content = b'{"data": "sensitive_data"}'
        replayed_response.headers = {'Content-Type': 'application/json'}
        replayed_response.elapsed.total_seconds.return_value = 0.3
        
        test_case = self.test_generator.generate_test_case(1, 1)
        test_case.category = 'auth'
        test_case.type = 'bypass'
        
        anomalies = self.analyzer.analyze_responses(original_response, replayed_response, test_case)
        
        # Should detect unauthorized access
        access_anomalies = [a for a in anomalies if a.type == 'unauthorized_access']
        self.assertGreater(len(access_anomalies), 0)
        
        # Should be marked as potential vulnerability
        self.assertTrue(any(a.is_potential_vulnerability for a in access_anomalies))


class TestRiskScorer(unittest.TestCase):
    """Test risk scoring functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.risk_scorer = RiskScorer()
        self.test_generator = TestDataGenerator()
    
    def test_anomaly_risk_calculation(self):
        """Test individual anomaly risk scoring."""
        # High severity, high confidence, vulnerability
        critical_anomaly = self.test_generator.generate_anomaly(1, 1)
        critical_anomaly.severity = 'Critical'
        critical_anomaly.confidence_score = 0.9
        critical_anomaly.is_potential_vulnerability = True
        
        risk_score = self.risk_scorer.calculate_anomaly_risk(critical_anomaly)
        
        self.assertGreater(risk_score, 8.0)  # Should be high risk
        self.assertLessEqual(risk_score, 10.0)  # Should not exceed maximum
        
        # Low severity, low confidence, not vulnerability
        low_anomaly = self.test_generator.generate_anomaly(1, 2)
        low_anomaly.severity = 'Low'
        low_anomaly.confidence_score = 0.3
        low_anomaly.is_potential_vulnerability = False
        
        low_risk_score = self.risk_scorer.calculate_anomaly_risk(low_anomaly)
        
        self.assertLess(low_risk_score, risk_score)  # Should be lower than critical
        self.assertGreater(low_risk_score, 0.0)  # Should be positive
    
    def test_flow_risk_calculation(self):
        """Test flow-level risk scoring."""
        anomalies = []
        
        # Add mix of anomalies
        for i in range(5):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomalies.append(anomaly)
        
        flow_risk = self.risk_scorer.calculate_flow_risk(anomalies)
        
        self.assertGreaterEqual(flow_risk, 0.0)
        self.assertLessEqual(flow_risk, 10.0)
        
        # Empty list should return 0
        empty_risk = self.risk_scorer.calculate_flow_risk([])
        self.assertEqual(empty_risk, 0.0)


class TestTrendAnalyzer(unittest.TestCase):
    """Test trend analysis functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.trend_analyzer = TrendAnalyzer()
        self.test_generator = TestDataGenerator()
    
    def test_severity_trends(self):
        """Test severity trend analysis."""
        anomalies = []
        for i in range(10):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomalies.append(anomaly)
        
        trends = self.trend_analyzer.analyze_severity_trends(anomalies)
        
        self.assertIn('counts', trends)
        self.assertIn('percentages', trends)
        self.assertIn('total', trends)
        
        self.assertEqual(trends['total'], len(anomalies))
        
        # Percentages should sum to 100
        total_percentage = sum(trends['percentages'].values())
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
    
    def test_type_trends(self):
        """Test anomaly type trend analysis."""
        anomalies = []
        for i in range(8):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomalies.append(anomaly)
        
        trends = self.trend_analyzer.analyze_type_trends(anomalies)
        
        self.assertIn('counts', trends)
        self.assertIn('sorted', trends)
        self.assertIn('most_common', trends)
        
        # Sorted should be in descending order
        if len(trends['sorted']) > 1:
            for i in range(len(trends['sorted']) - 1):
                self.assertGreaterEqual(trends['sorted'][i][1], trends['sorted'][i + 1][1])
    
    def test_confidence_trends(self):
        """Test confidence score trend analysis."""
        anomalies = []
        for i in range(6):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomalies.append(anomaly)
        
        trends = self.trend_analyzer.analyze_confidence_trends(anomalies)
        
        self.assertIn('average', trends)
        self.assertIn('min', trends)
        self.assertIn('max', trends)
        self.assertIn('distribution', trends)
        
        # Average should be between min and max
        self.assertGreaterEqual(trends['average'], trends['min'])
        self.assertLessEqual(trends['average'], trends['max'])
        
        # Distribution should have all categories
        self.assertIn('high', trends['distribution'])
        self.assertIn('medium', trends['distribution'])
        self.assertIn('low', trends['distribution'])


class TestVisualizationDataProcessor(unittest.TestCase):
    """Test visualization data processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = VisualizationDataProcessor()
        self.test_generator = TestDataGenerator()
    
    def test_timeline_data_preparation(self):
        """Test timeline data preparation."""
        # Generate anomalies with different timestamps
        anomalies = []
        for i in range(10):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomaly_dict = {
                'created_timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
                'severity': anomaly.severity,
                'is_potential_vulnerability': anomaly.is_potential_vulnerability
            }
            anomalies.append(anomaly_dict)
        
        timeline_data = self.processor.prepare_timeline_data(anomalies)
        
        self.assertIsInstance(timeline_data, list)
        
        for point in timeline_data:
            self.assertIn('date', point)
            self.assertIn('total', point)
            self.assertIn('critical', point)
            self.assertIn('high', point)
            self.assertIn('medium', point)
            self.assertIn('low', point)
            self.assertIn('vulnerabilities', point)
    
    def test_heatmap_data_preparation(self):
        """Test heatmap data preparation."""
        anomalies = []
        for i in range(15):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomaly_dict = {
                'type': anomaly.type,
                'severity': anomaly.severity
            }
            anomalies.append(anomaly_dict)
        
        heatmap_data = self.processor.prepare_heatmap_data(anomalies)
        
        self.assertIn('data', heatmap_data)
        self.assertIn('severities', heatmap_data)
        self.assertIn('max_count', heatmap_data)
        
        # Check data structure
        for row in heatmap_data['data']:
            self.assertIn('type', row)
            self.assertIn('data', row)
            
            for cell in row['data']:
                self.assertIn('severity', cell)
                self.assertIn('count', cell)
                self.assertIn('intensity', cell)
    
    def test_risk_distribution_data_preparation(self):
        """Test risk distribution data preparation."""
        anomalies = []
        for i in range(12):
            anomaly = self.test_generator.generate_anomaly(i + 1, i + 1)
            anomaly_dict = {
                'severity': anomaly.severity,
                'is_potential_vulnerability': anomaly.is_potential_vulnerability,
                'vulnerability_type': anomaly.vulnerability_type,
                'confidence_score': anomaly.confidence_score
            }
            anomalies.append(anomaly_dict)
        
        risk_data = self.processor.prepare_risk_distribution_data(anomalies)
        
        self.assertIn('risk_buckets', risk_data)
        self.assertIn('vulnerability_types', risk_data)
        self.assertIn('confidence_distribution', risk_data)
        
        # Check risk buckets
        expected_buckets = ['Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk', 'Minimal Risk']
        for bucket in expected_buckets:
            self.assertIn(bucket, risk_data['risk_buckets'])
        
        # Check confidence distribution
        confidence_dist = risk_data['confidence_distribution']
        self.assertIn('high', confidence_dist)
        self.assertIn('medium', confidence_dist)
        self.assertIn('low', confidence_dist)


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.db_manager = DatabaseManager(":memory:")
        self.payload_generator = PayloadGenerator(self.db_manager)
        self.analyzer = ResponseAnalyzer(self.db_manager)
        self.report_generator = EnhancedReportGenerator()
        self.test_generator = TestDataGenerator()
    
    def test_complete_workflow(self):
        """Test complete anomaly detection workflow."""
        # 1. Create flow
        flow = self.db_manager.create_flow(
            "Integration Test Flow",
            "Complete workflow test",
            "api.test.com"
        )
        self.assertIsNotNone(flow)
        
        # 2. Add request
        request = self.db_manager.add_request(
            flow.flow_id,
            "POST",
            "https://api.test.com/users",
            '{"Content-Type": "application/json"}',
            '{"username": "testuser", "role": "user"}'
        )
        self.assertIsNotNone(request)
        
        # 3. Generate payloads
        payloads = self.payload_generator.generate_payloads_for_request(request)
        self.assertGreater(len(payloads), 0)
        
        # 4. Create test cases (simulate)
        test_cases = []
        for i, payload in enumerate(payloads[:3]):  # Limit for testing
            test_case = self.db_manager.add_test_case(
                request.request_id,
                flow.flow_id,
                payload['category'],
                payload['type'],
                payload['description'],
                payload.get('modified_url', request.url),
                payload.get('modified_headers', request.headers),
                payload.get('modified_body', request.body)
            )
            test_cases.append(test_case)
        
        self.assertGreater(len(test_cases), 0)
        
        # 5. Simulate responses and analysis
        for test_case in test_cases:
            # Create mock responses
            original_response = Mock()
            original_response.status_code = 401
            original_response.content = b'{"error": "Unauthorized"}'
            original_response.headers = {'Content-Type': 'application/json'}
            original_response.elapsed.total_seconds.return_value = 0.2
            
            replayed_response = Mock()
            replayed_response.status_code = 200
            replayed_response.content = b'{"success": true, "user_id": 123}'
            replayed_response.headers = {'Content-Type': 'application/json'}
            replayed_response.elapsed.total_seconds.return_value = 0.3
            
            # Analyze responses
            anomalies = self.analyzer.analyze_responses(original_response, replayed_response, test_case)
            
            # Store anomalies
            for anomaly in anomalies:
                self.db_manager.add_anomaly(
                    test_case.test_case_id,
                    anomaly.type,
                    anomaly.severity,
                    anomaly.description,
                    anomaly.confidence_score,
                    anomaly.is_potential_vulnerability,
                    anomaly.vulnerability_type
                )
        
        # 6. Generate report
        flow_anomalies = self.db_manager.get_anomalies(flow.flow_id)
        self.assertGreater(len(flow_anomalies), 0)
        
        # Test HTML report generation
        html_report = self.report_generator.generate_html_report(flow, flow_anomalies)
        self.assertIsInstance(html_report, str)
        self.assertIn(flow.name, html_report)
        
        # Test JSON report generation
        json_report = self.report_generator.generate_json_report(flow, flow_anomalies)
        self.assertIsInstance(json_report, str)
        
        # Parse JSON to verify structure
        report_data = json.loads(json_report)
        self.assertIn('metadata', report_data)
        self.assertIn('flow', report_data)
        self.assertIn('summary', report_data)
        self.assertIn('anomalies', report_data)
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with non-existent flow
        non_existent_flow = self.db_manager.get_flow(99999)
        self.assertIsNone(non_existent_flow)
        
        # Test with invalid data
        with self.assertRaises(Exception):
            self.db_manager.create_flow("", "", "")  # Empty values
        
        # Test analyzer with None responses
        test_case = self.test_generator.generate_test_case(1, 1)
        
        # Should handle None gracefully
        anomalies = self.analyzer.analyze_responses(None, None, test_case)
        self.assertIsInstance(anomalies, list)
    
    def test_performance_with_large_dataset(self):
        """Test performance with larger datasets."""
        # Generate larger test scenario
        scenario = self.test_generator.generate_complete_test_scenario(
            num_flows=2, 
            num_requests_per_flow=5
        )
        
        # Verify data generation performance
        self.assertGreater(len(scenario['flows']), 0)
        self.assertGreater(len(scenario['requests']), 0)
        self.assertGreater(len(scenario['test_cases']), 0)
        
        # Test visualization data processing with larger dataset
        processor = VisualizationDataProcessor()
        
        # Convert anomalies to expected format
        anomalies_data = []
        for anomaly in scenario['anomalies']:
            anomaly_data = {
                'created_timestamp': anomaly['created_timestamp'],
                'severity': anomaly['severity'],
                'type': anomaly['type'],
                'is_potential_vulnerability': anomaly['is_potential_vulnerability'],
                'confidence_score': anomaly['confidence_score']
            }
            anomalies_data.append(anomaly_data)
        
        # Test various visualization preparations
        timeline_data = processor.prepare_timeline_data(anomalies_data)
        heatmap_data = processor.prepare_heatmap_data(anomalies_data)
        risk_data = processor.prepare_risk_distribution_data(anomalies_data)
        
        self.assertIsInstance(timeline_data, list)
        self.assertIsInstance(heatmap_data, dict)
        self.assertIsInstance(risk_data, dict)


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestDatabaseManager,
        TestPayloadGenerator,
        TestResponseAnalyzer,
        TestRiskScorer,
        TestTrendAnalyzer,
        TestVisualizationDataProcessor,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running comprehensive test suite...")
    success = run_comprehensive_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
    
    sys.exit(0 if success else 1)

