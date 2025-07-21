"""
Reporting module for the Business Logic Anomaly Detector.
Generates reports of findings in various formats.
"""

import json
import csv
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .database import DatabaseManager
from .models import ReportingError, FlowInfo, AnomalyInfo


class ReportGenerator:
    """Generates reports of anomaly detection findings."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
    
    def generate_html_report(self, flow_id: int, output_path: str,
                           include_all_requests: bool = False) -> bool:
        """Generate HTML report for a flow."""
        try:
            report_data = self.get_report_data(flow_id)
            
            html_content = self._generate_html_content(report_data, include_all_requests)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            raise ReportingError(f"Failed to generate HTML report: {e}")
    
    def generate_json_report(self, flow_id: int, output_path: str) -> bool:
        """Generate JSON report for a flow."""
        try:
            report_data = self.get_report_data(flow_id)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            raise ReportingError(f"Failed to generate JSON report: {e}")
    
    def generate_summary_report(self, flow_ids: List[int], output_path: str,
                              format: str = 'html') -> bool:
        """Generate summary report for multiple flows."""
        try:
            summary_data = {
                'generated_at': datetime.now().isoformat(),
                'flows': []
            }
            
            for flow_id in flow_ids:
                flow_data = self.get_report_data(flow_id)
                summary_data['flows'].append(flow_data)
            
            if format == 'html':
                html_content = self._generate_summary_html(summary_data)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            else:  # JSON
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            raise ReportingError(f"Failed to generate summary report: {e}")
    
    def get_report_data(self, flow_id: int) -> Dict[str, Any]:
        """Get structured report data for a flow."""
        try:
            flow = self.db_manager.get_flow(flow_id)
            if not flow:
                raise ReportingError(f"Flow {flow_id} not found")
            
            requests = self.db_manager.get_requests(flow_id)
            test_cases = self.db_manager.get_test_cases(flow_id=flow_id)
            anomalies = self.db_manager.get_anomalies(flow_id=flow_id)
            
            # Group test cases by request
            test_cases_by_request = {}
            for tc in test_cases:
                if tc.request_id not in test_cases_by_request:
                    test_cases_by_request[tc.request_id] = []
                test_cases_by_request[tc.request_id].append(tc)
            
            # Group anomalies by test case
            anomalies_by_test_case = {}
            for anomaly in anomalies:
                if anomaly.test_case_id not in anomalies_by_test_case:
                    anomalies_by_test_case[anomaly.test_case_id] = []
                anomalies_by_test_case[anomaly.test_case_id].append(anomaly)
            
            # Calculate statistics
            total_test_cases = len(test_cases)
            total_anomalies = len(anomalies)
            high_severity_anomalies = len([a for a in anomalies if a.severity == 'High'])
            critical_anomalies = len([a for a in anomalies if a.severity == 'Critical'])
            potential_vulnerabilities = len([a for a in anomalies if a.is_potential_vulnerability])
            
            report_data = {
                'flow': {
                    'id': flow.flow_id,
                    'name': flow.name,
                    'description': flow.description,
                    'target_domain': flow.target_domain,
                    'timestamp': flow.timestamp,
                    'request_count': len(requests)
                },
                'statistics': {
                    'total_requests': len(requests),
                    'total_test_cases': total_test_cases,
                    'total_anomalies': total_anomalies,
                    'critical_anomalies': critical_anomalies,
                    'high_severity_anomalies': high_severity_anomalies,
                    'potential_vulnerabilities': potential_vulnerabilities
                },
                'requests': [],
                'anomalies': [],
                'generated_at': datetime.now().isoformat()
            }
            
            # Add request details
            for request in requests:
                request_data = {
                    'id': request.request_id,
                    'sequence_number': request.sequence_number,
                    'method': request.method,
                    'url': request.url,
                    'response_status': request.response_status,
                    'test_cases': []
                }
                
                # Add test cases for this request
                if request.request_id in test_cases_by_request:
                    for tc in test_cases_by_request[request.request_id]:
                        tc_data = {
                            'id': tc.test_case_id,
                            'type': tc.type,
                            'category': tc.category,
                            'description': tc.description,
                            'payload_value': tc.payload_value,
                            'anomalies': []
                        }
                        
                        # Add anomalies for this test case
                        if tc.test_case_id in anomalies_by_test_case:
                            for anomaly in anomalies_by_test_case[tc.test_case_id]:
                                anomaly_data = {
                                    'id': anomaly.anomaly_id,
                                    'type': anomaly.type,
                                    'severity': anomaly.severity,
                                    'description': anomaly.description,
                                    'confidence_score': anomaly.confidence_score,
                                    'is_potential_vulnerability': anomaly.is_potential_vulnerability,
                                    'vulnerability_type': anomaly.vulnerability_type
                                }
                                tc_data['anomalies'].append(anomaly_data)
                        
                        request_data['test_cases'].append(tc_data)
                
                report_data['requests'].append(request_data)
            
            # Add all anomalies (sorted by severity)
            severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
            sorted_anomalies = sorted(anomalies, key=lambda a: (severity_order.get(a.severity, 5), -a.confidence_score))
            
            for anomaly in sorted_anomalies:
                anomaly_data = {
                    'id': anomaly.anomaly_id,
                    'test_case_id': anomaly.test_case_id,
                    'type': anomaly.type,
                    'severity': anomaly.severity,
                    'description': anomaly.description,
                    'confidence_score': anomaly.confidence_score,
                    'is_potential_vulnerability': anomaly.is_potential_vulnerability,
                    'vulnerability_type': anomaly.vulnerability_type,
                    'original_status': anomaly.original_status,
                    'replayed_status': anomaly.replayed_status,
                    'created_timestamp': anomaly.created_timestamp
                }
                report_data['anomalies'].append(anomaly_data)
            
            return report_data
        except Exception as e:
            raise ReportingError(f"Failed to get report data for flow {flow_id}: {e}")
    
    def export_anomalies_csv(self, flow_id: int, output_path: str) -> bool:
        """Export anomalies to CSV format."""
        try:
            anomalies = self.db_manager.get_anomalies(flow_id=flow_id)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'anomaly_id', 'test_case_id', 'type', 'severity', 'description',
                    'confidence_score', 'is_potential_vulnerability', 'vulnerability_type',
                    'original_status', 'replayed_status', 'created_timestamp'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for anomaly in anomalies:
                    writer.writerow({
                        'anomaly_id': anomaly.anomaly_id,
                        'test_case_id': anomaly.test_case_id,
                        'type': anomaly.type,
                        'severity': anomaly.severity,
                        'description': anomaly.description,
                        'confidence_score': anomaly.confidence_score,
                        'is_potential_vulnerability': anomaly.is_potential_vulnerability,
                        'vulnerability_type': anomaly.vulnerability_type,
                        'original_status': anomaly.original_status,
                        'replayed_status': anomaly.replayed_status,
                        'created_timestamp': anomaly.created_timestamp
                    })
            
            return True
        except Exception as e:
            raise ReportingError(f"Failed to export anomalies to CSV: {e}")
    
    def _generate_html_content(self, report_data: Dict[str, Any], include_all_requests: bool) -> str:
        """Generate HTML content for the report."""
        flow = report_data['flow']
        stats = report_data['statistics']
        anomalies = report_data['anomalies']
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anomaly Detection Report - {flow['name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .stats {{ display: flex; flex-wrap: wrap; gap: 20px; margin: 20px 0; }}
        .stat-box {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; min-width: 150px; }}
        .anomaly {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .critical {{ border-left: 5px solid #dc3545; }}
        .high {{ border-left: 5px solid #fd7e14; }}
        .medium {{ border-left: 5px solid #ffc107; }}
        .low {{ border-left: 5px solid #28a745; }}
        .info {{ border-left: 5px solid #17a2b8; }}
        .vulnerability {{ background-color: #fff3cd; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Business Logic Anomaly Detection Report</h1>
        <h2>Flow: {flow['name']}</h2>
        <p><strong>Description:</strong> {flow['description'] or 'N/A'}</p>
        <p><strong>Target Domain:</strong> {flow['target_domain'] or 'N/A'}</p>
        <p><strong>Generated:</strong> {report_data['generated_at']}</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>Total Requests</h3>
            <p>{stats['total_requests']}</p>
        </div>
        <div class="stat-box">
            <h3>Test Cases</h3>
            <p>{stats['total_test_cases']}</p>
        </div>
        <div class="stat-box">
            <h3>Anomalies Found</h3>
            <p>{stats['total_anomalies']}</p>
        </div>
        <div class="stat-box">
            <h3>Critical Issues</h3>
            <p>{stats['critical_anomalies']}</p>
        </div>
        <div class="stat-box">
            <h3>High Severity</h3>
            <p>{stats['high_severity_anomalies']}</p>
        </div>
        <div class="stat-box">
            <h3>Potential Vulnerabilities</h3>
            <p>{stats['potential_vulnerabilities']}</p>
        </div>
    </div>
    
    <h2>Anomalies Detected</h2>
"""
        
        if not anomalies:
            html += "<p>No anomalies detected in this flow.</p>"
        else:
            for anomaly in anomalies:
                severity_class = anomaly['severity'].lower()
                vuln_class = "vulnerability" if anomaly['is_potential_vulnerability'] else ""
                
                html += f"""
    <div class="anomaly {severity_class} {vuln_class}">
        <h3>{anomaly['type'].replace('_', ' ').title()} - {anomaly['severity']}</h3>
        <p><strong>Description:</strong> {anomaly['description']}</p>
        <p><strong>Confidence Score:</strong> {anomaly['confidence_score']:.2f}</p>
        <p><strong>Test Case ID:</strong> {anomaly['test_case_id']}</p>
        {f"<p><strong>Vulnerability Type:</strong> {anomaly['vulnerability_type']}</p>" if anomaly['vulnerability_type'] else ""}
        {f"<p><strong>Status Change:</strong> {anomaly['original_status']} → {anomaly['replayed_status']}</p>" if anomaly['original_status'] and anomaly['replayed_status'] else ""}
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
    
    def _generate_summary_html(self, summary_data: Dict[str, Any]) -> str:
        """Generate HTML content for summary report."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anomaly Detection Summary Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .flow-summary {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Business Logic Anomaly Detection Summary Report</h1>
        <p><strong>Generated:</strong> {summary_data['generated_at']}</p>
        <p><strong>Flows Analyzed:</strong> {len(summary_data['flows'])}</p>
    </div>
    
    <h2>Flow Summary</h2>
    <table>
        <tr>
            <th>Flow Name</th>
            <th>Requests</th>
            <th>Test Cases</th>
            <th>Anomalies</th>
            <th>Critical</th>
            <th>High</th>
            <th>Vulnerabilities</th>
        </tr>
"""
        
        for flow_data in summary_data['flows']:
            flow = flow_data['flow']
            stats = flow_data['statistics']
            html += f"""
        <tr>
            <td>{flow['name']}</td>
            <td>{stats['total_requests']}</td>
            <td>{stats['total_test_cases']}</td>
            <td>{stats['total_anomalies']}</td>
            <td>{stats['critical_anomalies']}</td>
            <td>{stats['high_severity_anomalies']}</td>
            <td>{stats['potential_vulnerabilities']}</td>
        </tr>
"""
        
        html += """
    </table>
</body>
</html>
"""
        return html

