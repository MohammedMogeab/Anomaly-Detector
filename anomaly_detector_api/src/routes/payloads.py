"""
Flask routes for payload generation.
"""

from flask import Blueprint, request, jsonify
from src.database import DatabaseManager
from src.payload_generation import PayloadGenerator
from src.models import PayloadGenerationError, DatabaseError
import os

payloads_bp = Blueprint('payloads', __name__)

# Initialize database manager and payload generator
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'anomaly_detector.db')
db_manager = DatabaseManager(f"sqlite:///{db_path}")
payload_generator = PayloadGenerator(db_manager)

@payloads_bp.route('/payloads/generate/request/<int:request_id>', methods=['POST'])
def generate_payloads_for_request(request_id):
    """Generate payloads for a specific request."""
    try:
        generated_count = payload_generator.generate_for_request(request_id)
        
        return jsonify({
            'request_id': request_id,
            'generated_count': generated_count,
            'message': f'Generated {generated_count} test cases for request {request_id}'
        })
    except PayloadGenerationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@payloads_bp.route('/payloads/generate/flow/<int:flow_id>', methods=['POST'])
def generate_payloads_for_flow(flow_id):
    """Generate payloads for all requests in a flow."""
    try:
        requests = db_manager.get_requests(flow_id)
        if not requests:
            return jsonify({'error': 'No requests found for this flow'}), 404
        
        total_generated = 0
        for req in requests:
            generated_count = payload_generator.generate_for_request(req.request_id)
            total_generated += generated_count
        
        # Also generate sequence manipulation test cases
        sequence_generated = payload_generator.generate_for_flow_sequence(flow_id)
        total_generated += sequence_generated
        
        return jsonify({
            'flow_id': flow_id,
            'total_generated': total_generated,
            'message': f'Generated {total_generated} test cases for flow {flow_id}'
        })
    except PayloadGenerationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@payloads_bp.route('/payloads/rules', methods=['GET'])
def get_payload_rules():
    """Get all payload generation rules."""
    try:
        category = request.args.get('category')
        enabled_only = request.args.get('enabled_only', 'false').lower() == 'true'
        
        rules = db_manager.get_payload_rules(category=category, enabled_only=enabled_only)
        
        return jsonify(rules)
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@payloads_bp.route('/payloads/rules', methods=['POST'])
def add_payload_rule():
    """Add a new payload generation rule."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Rule data is required'}), 400
        
        # Validate required fields
        required_fields = ['category', 'type', 'rule_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        rule_id = db_manager.add_payload_rule(
            category=data['category'],
            type=data['type'],
            rule_data=data['rule_data'],
            enabled=data.get('enabled', True),
            description=data.get('description')
        )
        
        return jsonify({
            'rule_id': rule_id,
            'message': 'Payload rule added successfully'
        }), 201
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

