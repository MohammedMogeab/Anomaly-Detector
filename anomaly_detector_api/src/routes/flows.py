"""
Flask routes for flow management.
"""

from flask import Blueprint, request, jsonify
from src.database import DatabaseManager
from src.models import DatabaseError
import os

flows_bp = Blueprint('flows', __name__)

# Initialize database manager
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'anomaly_detector.db')
db_manager = DatabaseManager(f"sqlite:///{db_path}")

@flows_bp.route('/flows', methods=['GET'])
def get_flows():
    """Get all flows."""
    try:
        flows = db_manager.get_all_flows()
        return jsonify([{
            'flow_id': flow.flow_id,
            'name': flow.name,
            'description': flow.description,
            'target_domain': flow.target_domain,
            'timestamp': flow.timestamp.isoformat() if flow.timestamp else None,
            'request_count': flow.request_count
        } for flow in flows])
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@flows_bp.route('/flows', methods=['POST'])
def create_flow():
    """Create a new flow."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Flow name is required'}), 400
        
        flow_id = db_manager.create_flow(
            name=data['name'],
            description=data.get('description'),
            target_domain=data.get('target_domain')
        )
        
        return jsonify({'flow_id': flow_id, 'message': 'Flow created successfully'}), 201
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@flows_bp.route('/flows/<int:flow_id>', methods=['GET'])
def get_flow(flow_id):
    """Get a specific flow."""
    try:
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        return jsonify({
            'flow_id': flow.flow_id,
            'name': flow.name,
            'description': flow.description,
            'target_domain': flow.target_domain,
            'timestamp': flow.timestamp.isoformat() if flow.timestamp else None,
            'request_count': flow.request_count
        })
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@flows_bp.route('/flows/<int:flow_id>/requests', methods=['GET'])
def get_flow_requests(flow_id):
    """Get all requests for a flow."""
    try:
        requests = db_manager.get_requests(flow_id)
        return jsonify([{
            'request_id': req.request_id,
            'flow_id': req.flow_id,
            'sequence_number': req.sequence_number,
            'url': req.url,
            'method': req.method,
            'headers': req.headers,
            'response_status': req.response_status,
            'response_headers': req.response_headers,
            'response_content_length': req.response_content_length,
            'timestamp': req.timestamp.isoformat() if req.timestamp else None
        } for req in requests])
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@flows_bp.route('/flows/<int:flow_id>/test-cases', methods=['GET'])
def get_flow_test_cases(flow_id):
    """Get all test cases for a flow."""
    try:
        test_cases = db_manager.get_test_cases(flow_id=flow_id)
        return jsonify([{
            'test_case_id': tc.test_case_id,
            'flow_id': tc.flow_id,
            'request_id': tc.request_id,
            'type': tc.type,
            'category': tc.category,
            'description': tc.description,
            'payload_value': tc.payload_value,
            'modified_url': tc.modified_url,
            'modified_headers': tc.modified_headers,
            'timestamp': tc.timestamp.isoformat() if tc.timestamp else None
        } for tc in test_cases])
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@flows_bp.route('/flows/<int:flow_id>/anomalies', methods=['GET'])
def get_flow_anomalies(flow_id):
    """Get all anomalies for a flow."""
    try:
        anomalies = db_manager.get_anomalies(flow_id=flow_id)
        return jsonify([{
            'anomaly_id': anomaly.anomaly_id,
            'test_case_id': anomaly.test_case_id,
            'response_id': anomaly.response_id,
            'type': anomaly.type,
            'severity': anomaly.severity,
            'description': anomaly.description,
            'confidence_score': anomaly.confidence_score,
            'is_potential_vulnerability': anomaly.is_potential_vulnerability,
            'vulnerability_type': anomaly.vulnerability_type,
            'original_status': anomaly.original_status,
            'replayed_status': anomaly.replayed_status,
            'original_content_length': anomaly.original_content_length,
            'replayed_content_length': anomaly.replayed_content_length,
            'created_timestamp': anomaly.created_timestamp.isoformat() if anomaly.created_timestamp else None
        } for anomaly in anomalies])
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

