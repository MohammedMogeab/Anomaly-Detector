"""
Flask routes for recording management.
"""

from flask import Blueprint, request, jsonify
from src.database import DatabaseManager
from src.recording import RecordingManager
from src.models import RecordingError, DatabaseError
import os

recording_bp = Blueprint('recording', __name__)

# Initialize database manager and recording manager
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'anomaly_detector.db')
db_manager = DatabaseManager(f"sqlite:///{db_path}")
recording_manager = RecordingManager(db_manager)

@recording_bp.route('/recording/start', methods=['POST'])
def start_recording():
    """Start recording a new flow."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Flow name is required'}), 400
        
        flow_id = recording_manager.start_recording(
            flow_name=data['name'],
            description=data.get('description'),
            target_domain=data.get('target_domain')
        )
        
        return jsonify({
            'flow_id': flow_id,
            'message': 'Recording started successfully',
            'is_recording': recording_manager.is_recording()
        }), 201
    except RecordingError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recording/stop', methods=['POST'])
def stop_recording():
    """Stop the current recording."""
    try:
        if not recording_manager.is_recording():
            return jsonify({'error': 'No recording in progress'}), 400
        
        recording_manager.stop_recording()
        
        return jsonify({
            'message': 'Recording stopped successfully',
            'is_recording': recording_manager.is_recording()
        })
    except RecordingError as e:
        return jsonify({'error': str(e)}), 400

@recording_bp.route('/recording/status', methods=['GET'])
def get_recording_status():
    """Get current recording status."""
    try:
        is_recording = recording_manager.is_recording()
        current_flow_id = recording_manager.current_flow_id if is_recording else None
        
        return jsonify({
            'is_recording': is_recording,
            'current_flow_id': current_flow_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recording/request', methods=['POST'])
def add_request():
    """Add a request to the current recording."""
    try:
        if not recording_manager.is_recording():
            return jsonify({'error': 'No recording in progress'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        # Validate required fields
        required_fields = ['url', 'method', 'response_status']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        request_id = recording_manager.add_recorded_request(
            url=data['url'],
            method=data['method'],
            headers=data.get('headers', {}),
            body=data.get('body', '').encode() if data.get('body') else None,
            response_status=data['response_status'],
            response_headers=data.get('response_headers', {}),
            response_content=data.get('response_content', '').encode() if data.get('response_content') else None
        )
        
        return jsonify({
            'request_id': request_id,
            'message': 'Request added successfully'
        }), 201
    except RecordingError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

