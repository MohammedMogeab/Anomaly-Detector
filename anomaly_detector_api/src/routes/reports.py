"""
API routes for report generation and analytics.
"""

from flask import Blueprint, jsonify, request, Response
from src.database import DatabaseManager
from src.enhanced_reporting import create_enhanced_report_generator
import os

reports_bp = Blueprint('reports', __name__)
db_manager = DatabaseManager()

# Initialize enhanced report generator
template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
report_generator = create_enhanced_report_generator(template_dir)

@reports_bp.route('/summary/<int:flow_id>', methods=['GET'])
def get_report_summary(flow_id):
    """Get report summary for a flow."""
    try:
        # Get flow info
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        # Get anomalies
        anomalies = db_manager.get_anomalies(flow_id)
        
        # Generate enhanced summary
        summary = report_generator.generate_enhanced_summary(flow, anomalies)
        
        return jsonify({
            'flow': {
                'flow_id': flow.flow_id,
                'name': flow.name,
                'description': flow.description,
                'target_domain': flow.target_domain,
                'request_count': flow.request_count,
                'timestamp': flow.timestamp.isoformat() if flow.timestamp else None
            },
            'summary': summary,
            'anomalies': [
                {
                    'anomaly_id': a.anomaly_id,
                    'type': a.type,
                    'severity': a.severity,
                    'description': a.description,
                    'confidence_score': a.confidence_score,
                    'is_potential_vulnerability': a.is_potential_vulnerability,
                    'vulnerability_type': a.vulnerability_type,
                    'original_status': a.original_status,
                    'replayed_status': a.replayed_status,
                    'original_content_length': a.original_content_length,
                    'replayed_content_length': a.replayed_content_length,
                    'created_timestamp': a.created_timestamp.isoformat() if a.created_timestamp else None
                }
                for a in anomalies[:10]  # Limit to first 10 for summary
            ]
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/html/<int:flow_id>', methods=['GET'])
def generate_html_report(flow_id):
    """Generate HTML report for a flow."""
    try:
        # Get flow info
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        # Get anomalies
        anomalies = db_manager.get_anomalies(flow_id)
        
        # Generate HTML report
        html_content = report_generator.generate_html_report(flow, anomalies)
        
        return Response(
            html_content,
            mimetype='text/html',
            headers={
                'Content-Disposition': f'attachment; filename=anomaly_report_flow_{flow_id}.html'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/json/<int:flow_id>', methods=['GET'])
def generate_json_report(flow_id):
    """Generate JSON report for a flow."""
    try:
        # Get flow info
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        # Get anomalies
        anomalies = db_manager.get_anomalies(flow_id)
        
        # Generate JSON report
        json_content = report_generator.generate_json_report(flow, anomalies)
        
        return Response(
            json_content,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=anomaly_report_flow_{flow_id}.json'
            }
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/executive/<int:flow_id>', methods=['GET'])
def get_executive_summary(flow_id):
    """Get executive summary for a flow."""
    try:
        # Get flow info
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        # Get anomalies
        anomalies = db_manager.get_anomalies(flow_id)
        
        # Generate executive summary
        executive_summary = report_generator.generate_executive_summary(flow, anomalies)
        
        return jsonify(executive_summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/analytics/<int:flow_id>', methods=['GET'])
def get_flow_analytics(flow_id):
    """Get detailed analytics for a flow."""
    try:
        # Get flow info
        flow = db_manager.get_flow(flow_id)
        if not flow:
            return jsonify({'error': 'Flow not found'}), 404
        
        # Get anomalies
        anomalies = db_manager.get_anomalies(flow_id)
        
        # Generate analytics
        summary = report_generator.generate_enhanced_summary(flow, anomalies)
        
        return jsonify({
            'flow_id': flow_id,
            'analytics': {
                'risk_assessment': {
                    'score': summary['risk_score'],
                    'category': summary['risk_category'],
                    'factors': {
                        'total_anomalies': summary['total_anomalies'],
                        'vulnerabilities': summary['potential_vulnerabilities'],
                        'severity_distribution': summary['severity_breakdown']
                    }
                },
                'trends': summary['trends'],
                'recommendations': summary['recommendations']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

