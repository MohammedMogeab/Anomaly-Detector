"""
Enhanced reporting module with advanced analytics and risk scoring.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from jinja2 import Environment, FileSystemLoader
import os

from src.models import FlowInfo, AnomalyInfo


class RiskScorer:
    """Calculate risk scores for flows and anomalies."""
    
    SEVERITY_WEIGHTS = {
        'Critical': 10.0,
        'High': 7.5,
        'Medium': 5.0,
        'Low': 2.5,
        'Info': 1.0
    }
    
    VULNERABILITY_MULTIPLIER = 1.5
    
    @classmethod
    def calculate_anomaly_risk(cls, anomaly: AnomalyInfo) -> float:
        """Calculate risk score for a single anomaly."""
        base_score = cls.SEVERITY_WEIGHTS.get(anomaly.severity, 1.0)
        confidence_factor = anomaly.confidence_score
        vulnerability_factor = cls.VULNERABILITY_MULTIPLIER if anomaly.is_potential_vulnerability else 1.0
        
        return min(10.0, base_score * confidence_factor * vulnerability_factor)
    
    @classmethod
    def calculate_flow_risk(cls, anomalies: List[AnomalyInfo]) -> float:
        """Calculate overall risk score for a flow."""
        if not anomalies:
            return 0.0
        
        # Calculate weighted average with emphasis on high-severity issues
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for anomaly in anomalies:
            risk_score = cls.calculate_anomaly_risk(anomaly)
            weight = cls.SEVERITY_WEIGHTS.get(anomaly.severity, 1.0)
            
            total_weighted_score += risk_score * weight
            total_weight += weight
        
        return min(10.0, total_weighted_score / total_weight if total_weight > 0 else 0.0)


class TrendAnalyzer:
    """Analyze trends in anomaly detection."""
    
    @staticmethod
    def analyze_severity_trends(anomalies: List[AnomalyInfo]) -> Dict[str, Any]:
        """Analyze severity distribution trends."""
        severity_counts = {}
        for anomaly in anomalies:
            severity_counts[anomaly.severity] = severity_counts.get(anomaly.severity, 0) + 1
        
        total = len(anomalies)
        severity_percentages = {
            severity: (count / total * 100) if total > 0 else 0
            for severity, count in severity_counts.items()
        }
        
        return {
            'counts': severity_counts,
            'percentages': severity_percentages,
            'total': total
        }
    
    @staticmethod
    def analyze_type_trends(anomalies: List[AnomalyInfo]) -> Dict[str, Any]:
        """Analyze anomaly type distribution."""
        type_counts = {}
        for anomaly in anomalies:
            type_counts[anomaly.type] = type_counts.get(anomaly.type, 0) + 1
        
        # Sort by frequency
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'counts': type_counts,
            'sorted': sorted_types,
            'most_common': sorted_types[0] if sorted_types else None
        }
    
    @staticmethod
    def analyze_confidence_trends(anomalies: List[AnomalyInfo]) -> Dict[str, Any]:
        """Analyze confidence score trends."""
        if not anomalies:
            return {'average': 0.0, 'min': 0.0, 'max': 0.0, 'distribution': {}}
        
        confidence_scores = [anomaly.confidence_score for anomaly in anomalies]
        
        # Confidence distribution buckets
        distribution = {
            'high': len([s for s in confidence_scores if s >= 0.8]),
            'medium': len([s for s in confidence_scores if 0.5 <= s < 0.8]),
            'low': len([s for s in confidence_scores if s < 0.5])
        }
        
        return {
            'average': sum(confidence_scores) / len(confidence_scores),
            'min': min(confidence_scores),
            'max': max(confidence_scores),
            'distribution': distribution
        }


class EnhancedReportGenerator:
    """Generate comprehensive reports with advanced analytics."""
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize the report generator."""
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.risk_scorer = RiskScorer()
        self.trend_analyzer = TrendAnalyzer()
    
    def generate_enhanced_summary(self, flow: FlowInfo, anomalies: List[AnomalyInfo]) -> Dict[str, Any]:
        """Generate enhanced summary with analytics."""
        # Basic counts
        total_anomalies = len(anomalies)
        potential_vulnerabilities = len([a for a in anomalies if a.is_potential_vulnerability])
        
        # Severity breakdown
        severity_breakdown = {}
        for anomaly in anomalies:
            severity_breakdown[anomaly.severity] = severity_breakdown.get(anomaly.severity, 0) + 1
        
        # Type breakdown
        type_breakdown = {}
        for anomaly in anomalies:
            type_breakdown[anomaly.type] = type_breakdown.get(anomaly.type, 0) + 1
        
        # Risk scoring
        risk_score = self.risk_scorer.calculate_flow_risk(anomalies)
        
        # Trend analysis
        severity_trends = self.trend_analyzer.analyze_severity_trends(anomalies)
        type_trends = self.trend_analyzer.analyze_type_trends(anomalies)
        confidence_trends = self.trend_analyzer.analyze_confidence_trends(anomalies)
        
        # Risk categorization
        risk_category = self._categorize_risk(risk_score)
        
        return {
            'total_anomalies': total_anomalies,
            'potential_vulnerabilities': potential_vulnerabilities,
            'severity_breakdown': severity_breakdown,
            'type_breakdown': type_breakdown,
            'risk_score': risk_score,
            'risk_category': risk_category,
            'trends': {
                'severity': severity_trends,
                'types': type_trends,
                'confidence': confidence_trends
            },
            'recommendations': self._generate_recommendations(anomalies, risk_score)
        }
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk based on score."""
        if risk_score >= 8.0:
            return 'Critical'
        elif risk_score >= 6.0:
            return 'High'
        elif risk_score >= 4.0:
            return 'Medium'
        elif risk_score >= 2.0:
            return 'Low'
        else:
            return 'Minimal'
    
    def _generate_recommendations(self, anomalies: List[AnomalyInfo], risk_score: float) -> List[str]:
        """Generate contextual recommendations."""
        recommendations = []
        
        # Risk-based recommendations
        if risk_score >= 8.0:
            recommendations.append("Immediate security review required - critical vulnerabilities detected")
        elif risk_score >= 6.0:
            recommendations.append("High-priority security issues require prompt attention")
        elif risk_score >= 4.0:
            recommendations.append("Moderate security concerns should be addressed in next sprint")
        
        # Type-specific recommendations
        vulnerability_types = set()
        for anomaly in anomalies:
            if anomaly.is_potential_vulnerability and anomaly.vulnerability_type:
                vulnerability_types.add(anomaly.vulnerability_type)
        
        if 'unauthorized_access' in vulnerability_types:
            recommendations.append("Review and strengthen authentication and authorization controls")
        if 'privilege_escalation' in vulnerability_types:
            recommendations.append("Audit user privilege assignments and access controls")
        if 'parameter_tampering' in vulnerability_types:
            recommendations.append("Implement robust input validation and parameter verification")
        if 'sequence_manipulation' in vulnerability_types:
            recommendations.append("Add sequence validation and state management controls")
        
        # General recommendations
        if len(anomalies) > 10:
            recommendations.append("Consider implementing automated security testing in CI/CD pipeline")
        
        if not recommendations:
            recommendations.append("Continue regular security testing to maintain current security posture")
        
        return recommendations
    
    def generate_html_report(self, flow: FlowInfo, anomalies: List[AnomalyInfo]) -> str:
        """Generate comprehensive HTML report."""
        template = self.env.get_template('report_template.html')
        
        summary = self.generate_enhanced_summary(flow, anomalies)
        
        # Sort anomalies by severity and confidence
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
        sorted_anomalies = sorted(
            anomalies,
            key=lambda a: (severity_order.get(a.severity, 5), -a.confidence_score)
        )
        
        return template.render(
            flow=flow,
            anomalies=sorted_anomalies,
            summary=summary,
            report_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def generate_json_report(self, flow: FlowInfo, anomalies: List[AnomalyInfo]) -> str:
        """Generate comprehensive JSON report."""
        summary = self.generate_enhanced_summary(flow, anomalies)
        
        # Convert anomalies to dictionaries
        anomalies_data = []
        for anomaly in anomalies:
            anomaly_dict = asdict(anomaly)
            # Add computed risk score
            anomaly_dict['risk_score'] = self.risk_scorer.calculate_anomaly_risk(anomaly)
            anomalies_data.append(anomaly_dict)
        
        report_data = {
            'metadata': {
                'report_type': 'business_logic_anomaly_detection',
                'version': '1.0.0',
                'generated_at': datetime.now().isoformat(),
                'generator': 'Enhanced Business Logic Anomaly Detector'
            },
            'flow': asdict(flow),
            'summary': summary,
            'anomalies': anomalies_data,
            'analytics': {
                'total_requests_analyzed': flow.request_count,
                'anomaly_detection_rate': (len(anomalies) / max(flow.request_count, 1)) * 100,
                'vulnerability_rate': (summary['potential_vulnerabilities'] / max(len(anomalies), 1)) * 100 if anomalies else 0
            }
        }
        
        return json.dumps(report_data, indent=2, default=str)
    
    def generate_executive_summary(self, flow: FlowInfo, anomalies: List[AnomalyInfo]) -> Dict[str, Any]:
        """Generate executive summary for dashboard."""
        summary = self.generate_enhanced_summary(flow, anomalies)
        
        return {
            'flow_name': flow.name,
            'risk_score': summary['risk_score'],
            'risk_category': summary['risk_category'],
            'total_anomalies': summary['total_anomalies'],
            'critical_issues': summary['severity_breakdown'].get('Critical', 0),
            'vulnerabilities': summary['potential_vulnerabilities'],
            'key_recommendations': summary['recommendations'][:3],  # Top 3 recommendations
            'last_analyzed': datetime.now().isoformat()
        }


# Export the enhanced report generator
def create_enhanced_report_generator(template_dir: str = "templates") -> EnhancedReportGenerator:
    """Factory function to create enhanced report generator."""
    return EnhancedReportGenerator(template_dir)

