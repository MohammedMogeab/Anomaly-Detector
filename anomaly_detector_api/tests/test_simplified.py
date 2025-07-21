"""
Simplified test suite for the Business Logic Anomaly Detector.
"""

import unittest
import json
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.enhanced_reporting import RiskScorer, TrendAnalyzer, EnhancedReportGenerator
from src.advanced_visualizations import VisualizationDataProcessor, ChartConfigGenerator


class TestRiskScorer(unittest.TestCase):
    """Test risk scoring functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.risk_scorer = RiskScorer()
    
    def test_severity_weights(self):
        """Test severity weight constants."""
        expected_weights = {
            'Critical': 10.0,
            'High': 7.5,
            'Medium': 5.0,
            'Low': 2.5,
            'Info': 1.0
        }
        
        for severity, expected_weight in expected_weights.items():
            self.assertEqual(self.risk_scorer.SEVERITY_WEIGHTS[severity], expected_weight)
    
    def test_anomaly_risk_calculation(self):
        """Test individual anomaly risk scoring."""
        # Create mock anomaly
        mock_anomaly = Mock()
        mock_anomaly.severity = 'Critical'
        mock_anomaly.confidence_score = 0.9
        mock_anomaly.is_potential_vulnerability = True
        
        risk_score = self.risk_scorer.calculate_anomaly_risk(mock_anomaly)
        
        self.assertGreater(risk_score, 8.0)  # Should be high risk
        self.assertLessEqual(risk_score, 10.0)  # Should not exceed maximum
        
        # Test low risk anomaly
        mock_anomaly.severity = 'Low'
        mock_anomaly.confidence_score = 0.3
        mock_anomaly.is_potential_vulnerability = False
        
        low_risk_score = self.risk_scorer.calculate_anomaly_risk(mock_anomaly)
        
        self.assertLess(low_risk_score, risk_score)  # Should be lower than critical
        self.assertGreater(low_risk_score, 0.0)  # Should be positive
    
    def test_flow_risk_calculation(self):
        """Test flow-level risk scoring."""
        anomalies = []
        
        # Add mix of anomalies
        for i in range(5):
            mock_anomaly = Mock()
            mock_anomaly.severity = ['Critical', 'High', 'Medium', 'Low', 'Info'][i]
            mock_anomaly.confidence_score = 0.8
            mock_anomaly.is_potential_vulnerability = i < 2  # First two are vulnerabilities
            anomalies.append(mock_anomaly)
        
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
    
    def test_severity_trends(self):
        """Test severity trend analysis."""
        # Create mock anomalies
        anomalies = []
        severities = ['Critical', 'High', 'Medium', 'Low', 'Critical', 'High']
        
        for severity in severities:
            mock_anomaly = Mock()
            mock_anomaly.severity = severity
            anomalies.append(mock_anomaly)
        
        trends = self.trend_analyzer.analyze_severity_trends(anomalies)
        
        self.assertIn('counts', trends)
        self.assertIn('percentages', trends)
        self.assertIn('total', trends)
        
        self.assertEqual(trends['total'], len(anomalies))
        self.assertEqual(trends['counts']['Critical'], 2)
        self.assertEqual(trends['counts']['High'], 2)
        
        # Percentages should sum to 100
        total_percentage = sum(trends['percentages'].values())
        self.assertAlmostEqual(total_percentage, 100.0, places=1)
    
    def test_type_trends(self):
        """Test anomaly type trend analysis."""
        anomalies = []
        types = ['unauthorized_access', 'parameter_tampering', 'unauthorized_access', 'sequence_manipulation']
        
        for anomaly_type in types:
            mock_anomaly = Mock()
            mock_anomaly.type = anomaly_type
            anomalies.append(mock_anomaly)
        
        trends = self.trend_analyzer.analyze_type_trends(anomalies)
        
        self.assertIn('counts', trends)
        self.assertIn('sorted', trends)
        self.assertIn('most_common', trends)
        
        self.assertEqual(trends['counts']['unauthorized_access'], 2)
        self.assertEqual(trends['counts']['parameter_tampering'], 1)
        
        # Most common should be unauthorized_access
        self.assertEqual(trends['most_common'][0], 'unauthorized_access')
        self.assertEqual(trends['most_common'][1], 2)
    
    def test_confidence_trends(self):
        """Test confidence score trend analysis."""
        anomalies = []
        confidence_scores = [0.9, 0.7, 0.4, 0.8, 0.3, 0.6]
        
        for score in confidence_scores:
            mock_anomaly = Mock()
            mock_anomaly.confidence_score = score
            anomalies.append(mock_anomaly)
        
        trends = self.trend_analyzer.analyze_confidence_trends(anomalies)
        
        self.assertIn('average', trends)
        self.assertIn('min', trends)
        self.assertIn('max', trends)
        self.assertIn('distribution', trends)
        
        # Check calculated values
        expected_avg = sum(confidence_scores) / len(confidence_scores)
        self.assertAlmostEqual(trends['average'], expected_avg, places=2)
        self.assertEqual(trends['min'], min(confidence_scores))
        self.assertEqual(trends['max'], max(confidence_scores))
        
        # Check distribution
        self.assertEqual(trends['distribution']['high'], 2)  # 0.9, 0.8
        self.assertEqual(trends['distribution']['medium'], 2)  # 0.7, 0.6
        self.assertEqual(trends['distribution']['low'], 2)  # 0.4, 0.3


class TestVisualizationDataProcessor(unittest.TestCase):
    """Test visualization data processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.processor = VisualizationDataProcessor()
    
    def test_timeline_data_preparation(self):
        """Test timeline data preparation."""
        # Create mock anomalies with different timestamps
        anomalies = []
        base_date = datetime.now()
        
        for i in range(5):
            anomaly_dict = {
                'created_timestamp': (base_date - timedelta(days=i)).isoformat(),
                'severity': ['Critical', 'High', 'Medium', 'Low', 'Info'][i],
                'is_potential_vulnerability': i < 2
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
        test_data = [
            ('unauthorized_access', 'Critical'),
            ('unauthorized_access', 'High'),
            ('parameter_tampering', 'Medium'),
            ('sequence_manipulation', 'Low')
        ]
        
        for anomaly_type, severity in test_data:
            anomaly_dict = {
                'type': anomaly_type,
                'severity': severity
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
                
                # Intensity should be between 0 and 1
                self.assertGreaterEqual(cell['intensity'], 0.0)
                self.assertLessEqual(cell['intensity'], 1.0)
    
    def test_risk_distribution_data_preparation(self):
        """Test risk distribution data preparation."""
        anomalies = []
        test_data = [
            ('Critical', True, 'unauthorized_access', 0.9),
            ('High', True, 'parameter_tampering', 0.8),
            ('Medium', False, None, 0.6),
            ('Low', False, None, 0.4)
        ]
        
        for severity, is_vuln, vuln_type, confidence in test_data:
            anomaly_dict = {
                'severity': severity,
                'is_potential_vulnerability': is_vuln,
                'vulnerability_type': vuln_type,
                'confidence_score': confidence
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
        
        # Check vulnerability types
        self.assertEqual(risk_data['vulnerability_types']['unauthorized_access'], 1)
        self.assertEqual(risk_data['vulnerability_types']['parameter_tampering'], 1)
        
        # Check confidence distribution
        confidence_dist = risk_data['confidence_distribution']
        self.assertIn('high', confidence_dist)
        self.assertIn('medium', confidence_dist)
        self.assertIn('low', confidence_dist)
        
        self.assertEqual(confidence_dist['high'], 2)  # 0.9, 0.8
        self.assertEqual(confidence_dist['medium'], 1)  # 0.6
        self.assertEqual(confidence_dist['low'], 1)  # 0.4
    
    def test_trend_analysis_data_preparation(self):
        """Test trend analysis data preparation."""
        # Create anomalies over the past few days
        anomalies = []
        base_date = datetime.now()
        
        for i in range(10):
            anomaly_dict = {
                'created_timestamp': (base_date - timedelta(days=i)).isoformat(),
                'severity': ['Critical', 'High', 'Medium', 'Low'][i % 4],
                'is_potential_vulnerability': i % 3 == 0
            }
            anomalies.append(anomaly_dict)
        
        trend_data = self.processor.prepare_trend_analysis_data(anomalies, days=15)
        
        self.assertIn('daily_data', trend_data)
        self.assertIn('summary', trend_data)
        
        # Check daily data structure
        for day_data in trend_data['daily_data']:
            self.assertIn('date', day_data)
            self.assertIn('total', day_data)
            self.assertIn('vulnerabilities', day_data)
            self.assertIn('critical', day_data)
            self.assertIn('high', day_data)
            self.assertIn('medium', day_data)
            self.assertIn('low', day_data)
            self.assertIn('moving_avg_total', day_data)
            self.assertIn('moving_avg_vulnerabilities', day_data)
        
        # Check summary
        summary = trend_data['summary']
        self.assertIn('total_period', summary)
        self.assertIn('total_anomalies', summary)
        self.assertIn('total_vulnerabilities', summary)
        self.assertIn('peak_day', summary)
        self.assertIn('trend_direction', summary)
        
        self.assertEqual(summary['total_period'], 15)
        self.assertIn(summary['trend_direction'], ['increasing', 'decreasing', 'stable'])


class TestChartConfigGenerator(unittest.TestCase):
    """Test chart configuration generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.generator = ChartConfigGenerator()
    
    def test_timeline_config_generation(self):
        """Test timeline chart configuration generation."""
        # Create sample timeline data
        timeline_data = [
            {'date': '2025-01-01', 'total': 5, 'vulnerabilities': 2},
            {'date': '2025-01-02', 'total': 3, 'vulnerabilities': 1},
            {'date': '2025-01-03', 'total': 7, 'vulnerabilities': 3}
        ]
        
        config = self.generator.generate_timeline_config(timeline_data)
        
        self.assertIn('type', config)
        self.assertIn('data', config)
        self.assertIn('options', config)
        
        self.assertEqual(config['type'], 'line')
        
        # Check data structure
        data = config['data']
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        
        self.assertEqual(len(data['labels']), 3)
        self.assertEqual(len(data['datasets']), 2)  # Total and Vulnerabilities
        
        # Check datasets
        total_dataset = data['datasets'][0]
        vuln_dataset = data['datasets'][1]
        
        self.assertEqual(total_dataset['label'], 'Total Anomalies')
        self.assertEqual(vuln_dataset['label'], 'Vulnerabilities')
        
        self.assertEqual(total_dataset['data'], [5, 3, 7])
        self.assertEqual(vuln_dataset['data'], [2, 1, 3])
    
    def test_risk_radar_config_generation(self):
        """Test risk radar chart configuration generation."""
        # Create sample risk data
        risk_data = {
            'risk_buckets': {
                'Critical Risk': 3,
                'High Risk': 5,
                'Medium Risk': 2,
                'Low Risk': 1,
                'Minimal Risk': 0
            }
        }
        
        config = self.generator.generate_risk_radar_config(risk_data)
        
        self.assertIn('type', config)
        self.assertIn('data', config)
        self.assertIn('options', config)
        
        self.assertEqual(config['type'], 'radar')
        
        # Check data structure
        data = config['data']
        self.assertIn('labels', data)
        self.assertIn('datasets', data)
        
        self.assertEqual(len(data['labels']), 5)
        self.assertEqual(len(data['datasets']), 1)
        
        # Check dataset
        dataset = data['datasets'][0]
        self.assertEqual(dataset['label'], 'Risk Distribution')
        self.assertEqual(dataset['data'], [3, 5, 2, 1, 0])


class TestEnhancedReportGenerator(unittest.TestCase):
    """Test enhanced report generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.report_generator = EnhancedReportGenerator()
    
    def test_risk_categorization(self):
        """Test risk score categorization."""
        test_cases = [
            (9.5, 'Critical'),
            (7.0, 'High'),
            (5.0, 'Medium'),
            (3.0, 'Low'),
            (1.0, 'Minimal')
        ]
        
        for risk_score, expected_category in test_cases:
            category = self.report_generator._categorize_risk(risk_score)
            self.assertEqual(category, expected_category)
    
    def test_recommendation_generation(self):
        """Test contextual recommendation generation."""
        # Create mock anomalies
        anomalies = []
        
        # High-risk scenario
        mock_anomaly = Mock()
        mock_anomaly.is_potential_vulnerability = True
        mock_anomaly.vulnerability_type = 'unauthorized_access'
        anomalies.append(mock_anomaly)
        
        recommendations = self.report_generator._generate_recommendations(anomalies, 8.5)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should include critical security review recommendation
        critical_rec = any('critical' in rec.lower() for rec in recommendations)
        self.assertTrue(critical_rec)
        
        # Should include unauthorized access specific recommendation
        auth_rec = any('authentication' in rec.lower() for rec in recommendations)
        self.assertTrue(auth_rec)
    
    def test_enhanced_summary_generation(self):
        """Test enhanced summary generation."""
        # Create mock flow
        mock_flow = Mock()
        mock_flow.name = 'Test Flow'
        mock_flow.description = 'Test Description'
        mock_flow.request_count = 10
        
        # Create mock anomalies
        anomalies = []
        for i in range(5):
            mock_anomaly = Mock()
            mock_anomaly.severity = ['Critical', 'High', 'Medium', 'Low', 'Info'][i]
            mock_anomaly.type = 'unauthorized_access'
            mock_anomaly.is_potential_vulnerability = i < 2
            mock_anomaly.vulnerability_type = 'unauthorized_access' if i < 2 else None
            mock_anomaly.confidence_score = 0.8
            anomalies.append(mock_anomaly)
        
        summary = self.report_generator.generate_enhanced_summary(mock_flow, anomalies)
        
        # Check summary structure
        expected_keys = [
            'total_anomalies', 'potential_vulnerabilities', 'severity_breakdown',
            'type_breakdown', 'risk_score', 'risk_category', 'trends', 'recommendations'
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
        
        # Check values
        self.assertEqual(summary['total_anomalies'], 5)
        self.assertEqual(summary['potential_vulnerabilities'], 2)
        self.assertGreater(summary['risk_score'], 0.0)
        self.assertLessEqual(summary['risk_score'], 10.0)
        self.assertIn(summary['risk_category'], ['Critical', 'High', 'Medium', 'Low', 'Minimal'])


def run_simplified_tests():
    """Run all simplified tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestRiskScorer,
        TestTrendAnalyzer,
        TestVisualizationDataProcessor,
        TestChartConfigGenerator,
        TestEnhancedReportGenerator
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running simplified test suite...")
    success = run_simplified_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
        print("\nTest Coverage Summary:")
        print("- Risk Scoring: ✅ Tested")
        print("- Trend Analysis: ✅ Tested")
        print("- Data Visualization: ✅ Tested")
        print("- Chart Configuration: ✅ Tested")
        print("- Report Generation: ✅ Tested")
    else:
        print("\n❌ Some tests failed. Please review the output above.")
    
    sys.exit(0 if success else 1)

