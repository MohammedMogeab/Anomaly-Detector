"""
Flask routes for replay management.
"""

from flask import Blueprint, request, jsonify
from src.database import DatabaseManager
from src.replay import ReplayManager
from src.models import ReplayError, DatabaseError
import os
import asyncio

replay_bp = Blueprint('replay', __name__)

# Initialize database manager and replay manager
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'anomaly_detector.db')
db_manager = DatabaseManager(f"sqlite:///{db_path}")
replay_manager = ReplayManager(db_manager)

@replay_bp.route('/replay/flow/<int:flow_id>', methods=['POST'])
def replay_flow(flow_id):
    """Replay all test cases for a flow."""
    try:
        # Run the async replay function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            replayed_count = loop.run_until_complete(replay_manager.replay_flow(flow_id))
        finally:
            loop.close()
        
        return jsonify({
            'flow_id': flow_id,
            'replayed_count': replayed_count,
            'message': f'Replayed {replayed_count} test cases for flow {flow_id}'
        })
    except ReplayError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@replay_bp.route('/replay/test-case/<int:test_case_id>', methods=['POST'])
def replay_test_case(test_case_id):
    """Replay a specific test case."""
    try:
        # Run the async replay function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response_info = loop.run_until_complete(replay_manager.replay_test_case(test_case_id))
        finally:
            loop.close()
        
        if response_info:
            return jsonify({
                'test_case_id': test_case_id,
                'response_id': response_info.response_id,
                'status_code': response_info.status_code,
                'content_length': response_info.content_length,
                'response_time_ms': response_info.response_time_ms,
                'message': f'Test case {test_case_id} replayed successfully'
            })
        else:
            return jsonify({
                'test_case_id': test_case_id,
                'message': 'Test case replayed but no response recorded'
            })
    except ReplayError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@replay_bp.route('/replay/responses/<int:test_case_id>', methods=['GET'])
def get_replayed_response(test_case_id):
    """Get the replayed response for a test case."""
    try:
        response = db_manager.get_replayed_response(test_case_id)
        if not response:
            return jsonify({'error': 'No replayed response found for this test case'}), 404
        
        return jsonify({
            'response_id': response.response_id,
            'test_case_id': response.test_case_id,
            'status_code': response.status_code,
            'headers': response.headers,
            'content_length': response.content_length,
            'response_time_ms': response.response_time_ms,
            'timestamp': response.timestamp.isoformat() if response.timestamp else None
        })
    except DatabaseError as e:
        return jsonify({'error': str(e)}), 500

