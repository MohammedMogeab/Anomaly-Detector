"""
Advanced visualization components and data processing for anomaly detection.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import math


class VisualizationDataProcessor:
    """Process data for advanced visualizations."""
    
    @staticmethod
    def prepare_timeline_data(anomalies: List[Dict]) -> List[Dict]:
        """Prepare data for timeline visualization."""
        timeline_data = []
        
        # Group anomalies by date
        date_groups = defaultdict(list)
        for anomaly in anomalies:
            if anomaly.get('created_timestamp'):
                date = datetime.fromisoformat(anomaly['created_timestamp']).date()
                date_groups[date].append(anomaly)
        
        # Create timeline points
        for date, day_anomalies in sorted(date_groups.items()):
            severity_counts = defaultdict(int)
            for anomaly in day_anomalies:
                severity_counts[anomaly['severity']] += 1
            
            timeline_data.append({
                'date': date.isoformat(),
                'total': len(day_anomalies),
                'critical': severity_counts['Critical'],
                'high': severity_counts['High'],
                'medium': severity_counts['Medium'],
                'low': severity_counts['Low'],
                'vulnerabilities': len([a for a in day_anomalies if a.get('is_potential_vulnerability')])
            })
        
        return timeline_data
    
    @staticmethod
    def prepare_heatmap_data(anomalies: List[Dict]) -> Dict[str, Any]:
        """Prepare data for severity/type heatmap."""
        severity_order = ['Critical', 'High', 'Medium', 'Low', 'Info']
        type_counts = defaultdict(lambda: defaultdict(int))
        
        # Count anomalies by type and severity
        for anomaly in anomalies:
            type_counts[anomaly['type']][anomaly['severity']] += 1
        
        # Prepare heatmap matrix
        heatmap_data = []
        for anomaly_type, severity_counts in type_counts.items():
            row_data = {
                'type': anomaly_type.replace('_', ' ').title(),
                'data': []
            }
            
            for severity in severity_order:
                count = severity_counts.get(severity, 0)
                row_data['data'].append({
                    'severity': severity,
                    'count': count,
                    'intensity': min(1.0, count / 10.0)  # Normalize for color intensity
                })
            
            heatmap_data.append(row_data)
        
        return {
            'data': heatmap_data,
            'severities': severity_order,
            'max_count': max([
                max([cell['count'] for cell in row['data']])
                for row in heatmap_data
            ]) if heatmap_data else 0
        }
    
    @staticmethod
    def prepare_risk_distribution_data(anomalies: List[Dict]) -> Dict[str, Any]:
        """Prepare data for risk distribution visualization."""
        risk_buckets = {
            'Critical Risk': 0,
            'High Risk': 0,
            'Medium Risk': 0,
            'Low Risk': 0,
            'Minimal Risk': 0
        }
        
        vulnerability_types = defaultdict(int)
        confidence_distribution = {'high': 0, 'medium': 0, 'low': 0}
        
        for anomaly in anomalies:
            # Risk categorization based on severity and vulnerability status
            severity = anomaly['severity']
            is_vuln = anomaly.get('is_potential_vulnerability', False)
            
            if severity == 'Critical' or (severity == 'High' and is_vuln):
                risk_buckets['Critical Risk'] += 1
            elif severity == 'High' or (severity == 'Medium' and is_vuln):
                risk_buckets['High Risk'] += 1
            elif severity == 'Medium':
                risk_buckets['Medium Risk'] += 1
            elif severity == 'Low':
                risk_buckets['Low Risk'] += 1
            else:
                risk_buckets['Minimal Risk'] += 1
            
            # Vulnerability types
            if is_vuln and anomaly.get('vulnerability_type'):
                vulnerability_types[anomaly['vulnerability_type']] += 1
            
            # Confidence distribution
            confidence = anomaly.get('confidence_score', 0)
            if confidence >= 0.8:
                confidence_distribution['high'] += 1
            elif confidence >= 0.5:
                confidence_distribution['medium'] += 1
            else:
                confidence_distribution['low'] += 1
        
        return {
            'risk_buckets': risk_buckets,
            'vulnerability_types': dict(vulnerability_types),
            'confidence_distribution': confidence_distribution
        }
    
    @staticmethod
    def prepare_trend_analysis_data(anomalies: List[Dict], days: int = 30) -> Dict[str, Any]:
        """Prepare data for trend analysis over time."""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Initialize daily buckets
        daily_data = {}
        current_date = start_date
        while current_date <= end_date:
            daily_data[current_date] = {
                'date': current_date.isoformat(),
                'total': 0,
                'vulnerabilities': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            current_date += timedelta(days=1)
        
        # Populate with actual data
        for anomaly in anomalies:
            if anomaly.get('created_timestamp'):
                anomaly_date = datetime.fromisoformat(anomaly['created_timestamp']).date()
                if start_date <= anomaly_date <= end_date:
                    daily_data[anomaly_date]['total'] += 1
                    
                    if anomaly.get('is_potential_vulnerability'):
                        daily_data[anomaly_date]['vulnerabilities'] += 1
                    
                    severity = anomaly['severity'].lower()
                    if severity in daily_data[anomaly_date]:
                        daily_data[anomaly_date][severity] += 1
        
        # Convert to list and calculate trends
        trend_data = list(daily_data.values())
        
        # Calculate moving averages
        window_size = 7  # 7-day moving average
        for i in range(len(trend_data)):
            start_idx = max(0, i - window_size + 1)
            window_data = trend_data[start_idx:i+1]
            
            trend_data[i]['moving_avg_total'] = sum(d['total'] for d in window_data) / len(window_data)
            trend_data[i]['moving_avg_vulnerabilities'] = sum(d['vulnerabilities'] for d in window_data) / len(window_data)
        
        return {
            'daily_data': trend_data,
            'summary': {
                'total_period': days,
                'total_anomalies': sum(d['total'] for d in trend_data),
                'total_vulnerabilities': sum(d['vulnerabilities'] for d in trend_data),
                'peak_day': max(trend_data, key=lambda x: x['total']) if trend_data else None,
                'trend_direction': VisualizationDataProcessor._calculate_trend_direction(trend_data)
            }
        }
    
    @staticmethod
    def _calculate_trend_direction(data: List[Dict]) -> str:
        """Calculate overall trend direction."""
        if len(data) < 2:
            return 'stable'
        
        # Use linear regression to determine trend
        n = len(data)
        x_values = list(range(n))
        y_values = [d['total'] for d in data]
        
        # Calculate slope
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 'stable'
        
        slope = numerator / denominator
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def prepare_comparative_analysis_data(flows_data: List[Dict]) -> Dict[str, Any]:
        """Prepare data for comparative analysis between flows."""
        comparison_data = []
        
        for flow_data in flows_data:
            flow = flow_data['flow']
            anomalies = flow_data['anomalies']
            
            # Calculate metrics for each flow
            total_anomalies = len(anomalies)
            vulnerabilities = len([a for a in anomalies if a.get('is_potential_vulnerability')])
            
            severity_counts = defaultdict(int)
            for anomaly in anomalies:
                severity_counts[anomaly['severity']] += 1
            
            # Calculate risk score (simplified)
            risk_score = (
                severity_counts['Critical'] * 10 +
                severity_counts['High'] * 7 +
                severity_counts['Medium'] * 4 +
                severity_counts['Low'] * 1
            ) / max(total_anomalies, 1)
            
            comparison_data.append({
                'flow_id': flow['flow_id'],
                'flow_name': flow['name'],
                'total_anomalies': total_anomalies,
                'vulnerabilities': vulnerabilities,
                'risk_score': min(10, risk_score),
                'critical': severity_counts['Critical'],
                'high': severity_counts['High'],
                'medium': severity_counts['Medium'],
                'low': severity_counts['Low'],
                'vulnerability_rate': (vulnerabilities / max(total_anomalies, 1)) * 100
            })
        
        return {
            'flows': comparison_data,
            'summary': {
                'total_flows': len(comparison_data),
                'highest_risk_flow': max(comparison_data, key=lambda x: x['risk_score']) if comparison_data else None,
                'most_anomalies_flow': max(comparison_data, key=lambda x: x['total_anomalies']) if comparison_data else None,
                'average_risk_score': sum(f['risk_score'] for f in comparison_data) / len(comparison_data) if comparison_data else 0
            }
        }


class ChartConfigGenerator:
    """Generate chart configurations for various visualization libraries."""
    
    @staticmethod
    def generate_timeline_config(data: List[Dict]) -> Dict[str, Any]:
        """Generate configuration for timeline chart."""
        return {
            'type': 'line',
            'data': {
                'labels': [d['date'] for d in data],
                'datasets': [
                    {
                        'label': 'Total Anomalies',
                        'data': [d['total'] for d in data],
                        'borderColor': 'rgb(59, 130, 246)',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'tension': 0.4
                    },
                    {
                        'label': 'Vulnerabilities',
                        'data': [d['vulnerabilities'] for d in data],
                        'borderColor': 'rgb(239, 68, 68)',
                        'backgroundColor': 'rgba(239, 68, 68, 0.1)',
                        'tension': 0.4
                    }
                ]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Anomaly Detection Timeline'
                    },
                    'legend': {
                        'position': 'top'
                    }
                },
                'scales': {
                    'x': {
                        'display': True,
                        'title': {
                            'display': True,
                            'text': 'Date'
                        }
                    },
                    'y': {
                        'display': True,
                        'title': {
                            'display': True,
                            'text': 'Count'
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def generate_risk_radar_config(risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate configuration for risk assessment radar chart."""
        return {
            'type': 'radar',
            'data': {
                'labels': list(risk_data['risk_buckets'].keys()),
                'datasets': [{
                    'label': 'Risk Distribution',
                    'data': list(risk_data['risk_buckets'].values()),
                    'backgroundColor': 'rgba(239, 68, 68, 0.2)',
                    'borderColor': 'rgb(239, 68, 68)',
                    'pointBackgroundColor': 'rgb(239, 68, 68)',
                    'pointBorderColor': '#fff',
                    'pointHoverBackgroundColor': '#fff',
                    'pointHoverBorderColor': 'rgb(239, 68, 68)'
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Risk Assessment Overview'
                    }
                },
                'scales': {
                    'r': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Number of Issues'
                        }
                    }
                }
            }
        }


# Export functions for use in API routes
def process_visualization_data(anomalies: List[Dict], visualization_type: str) -> Dict[str, Any]:
    """Main function to process data for different visualization types."""
    processor = VisualizationDataProcessor()
    
    if visualization_type == 'timeline':
        return processor.prepare_timeline_data(anomalies)
    elif visualization_type == 'heatmap':
        return processor.prepare_heatmap_data(anomalies)
    elif visualization_type == 'risk_distribution':
        return processor.prepare_risk_distribution_data(anomalies)
    elif visualization_type == 'trend_analysis':
        return processor.prepare_trend_analysis_data(anomalies)
    else:
        raise ValueError(f"Unknown visualization type: {visualization_type}")


def generate_chart_config(data: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
    """Generate chart configuration for frontend visualization libraries."""
    generator = ChartConfigGenerator()
    
    if chart_type == 'timeline':
        return generator.generate_timeline_config(data)
    elif chart_type == 'risk_radar':
        return generator.generate_risk_radar_config(data)
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")

