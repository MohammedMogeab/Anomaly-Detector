"""
Flask routes for response analysis.
"""

from flask import Blueprint, request, jsonify
from src.database import DatabaseManager
from src.analysis import ResponseAnalyzer
from src.models import AnalysisError, DatabaseError
import os

analysis_bp = Blueprint('analysis', __name__)

# Initialize database manager and response analyzer
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'anomaly_detector.db')
db_manager = DatabaseManager(f"sqlite:///{db_path}")
response_analyzer = ResponseAnalyzer(db_manager)

@analysis_bp.route('/analysis/flow/<int:flow_id>', methods=['POST'])
def analyze_flow(flow_id):
    """Analyze all replayed responses for a flow."""
    try:
        anomalies_found = response_analyzer.analyze_flow(flow_id)
        
        return jsonify({
            'flow_id': flow_id,
            'anomalies_found': anomalies_found,
            'message': f'Found {anomalies_found} anomalies for flow {flow_id}'
        })
    except AnalysisError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/test-case/<int:test_case_id>', methods=['POST'])
def analyze_test_case(test_case_id):
    """Analyze a specific test case."""
    try:
        anomalies = response_analyzer.analyze_test_case(test_case_id)
        
        return jsonify({
            'test_case_id': test_case_id,
            'anomalies_found': len(anomalies),
            'anomalies': [{
                'anomaly_id': anomaly,  # This is actually the anomaly_id returned by add_anomaly
                'message': f'Anomaly detected for test case {test_case_id}'
            } for anomaly in anomalies],
            'message': f'Found {len(anomalies)} anomalies for test case {test_case_id}'
        })
    except AnalysisError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/threshold', methods=['GET'])
def get_detection_threshold():
    """Get the current anomaly detection threshold."""
    try:
        threshold = response_analyzer.detection_threshold
        return jsonify({'threshold': threshold})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/threshold', methods=['POST'])
def set_detection_threshold():
    """Set the anomaly detection threshold."""
    try:
        data = request.get_json()
        if not data or 'threshold' not in data:
            return jsonify({'error': 'Threshold value is required'}), 400
        
        threshold = float(data['threshold'])
        response_analyzer.set_detection_threshold(threshold)
        
        return jsonify({
            'threshold': threshold,
            'message': 'Detection threshold updated successfully'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/rules/keyword', methods=['POST'])
def add_keyword_rule():
    """Add a keyword-based detection rule."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Rule data is required'}), 400
        
        # Validate required fields
        required_fields = ['keyword', 'anomaly_type', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        rule_id = response_analyzer.add_keyword_rule(
            keyword=data['keyword'],
            anomaly_type=data['anomaly_type'],
            severity=data['severity']
        )
        
        return jsonify({
            'rule_id': rule_id,
            'message': 'Keyword rule added successfully'
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/rules/status-code', methods=['POST'])
def add_status_code_rule():
    """Add a status code comparison rule."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Rule data is required'}), 400
        
        # Validate required fields
        required_fields = ['original_status', 'replayed_status', 'anomaly_type', 'severity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        rule_id = response_analyzer.add_status_code_rule(
            original_status=int(data['original_status']),
            replayed_status=int(data['replayed_status']),
            anomaly_type=data['anomaly_type'],
            severity=data['severity']
        )
        
        return jsonify({
            'rule_id': rule_id,
            'message': 'Status code rule added successfully'
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analysis/anomaly-types', methods=['GET'])
def get_anomaly_types():
    """Get list of supported anomaly types."""
    try:
        anomaly_types = response_analyzer.get_anomaly_types()
        return jsonify({'anomaly_types': anomaly_types})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

