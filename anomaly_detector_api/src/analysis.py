"""
Response analysis module for the Business Logic Anomaly Detector.
Compares replayed responses with original baselines and detects anomalies.
"""

import json
from typing import List, Dict, Any, Optional

from .database import DatabaseManager
from .models import (
    RequestInfo, TestCaseInfo, ReplayedResponseInfo, AnomalyInfo,
    AnalysisError, ANOMALY_TYPES, SEVERITY_LEVELS
)


class ResponseAnalyzer:
    """Analyzes replayed responses to detect anomalies and potential vulnerabilities."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        self.detection_threshold = float(self.db_manager.get_config(
            "anomaly_detection_threshold") or 0.7)
        # Rules can be loaded from DB or defined here
        self.keyword_rules = []  # Example: [{"keyword": "access denied", "type": "unauthorized_access", "severity": "High"}]
        self.status_code_rules = [] # Example: [{"original": 200, "replayed": 403, "type": "unauthorized_access", "severity": "High"}]
    
    def analyze_flow(self, flow_id: int) -> int:
        """Analyze all replayed responses for a flow. Returns count of anomalies found."""
        try:
            test_cases = self.db_manager.get_test_cases(flow_id=flow_id)
            anomalies_found = 0
            for tc in test_cases:
                anomalies = self.analyze_test_case(tc.test_case_id)
                anomalies_found += len(anomalies)
            return anomalies_found
        except Exception as e:
            raise AnalysisError(f"Failed to analyze flow {flow_id}: {e}")
    
    def analyze_test_case(self, test_case_id: int) -> List[AnomalyInfo]:
        """Analyze a specific test case. Returns list of anomalies."""
        anomalies = []
        try:
            test_case = self.db_manager.get_test_cases(request_id=None, flow_id=None)
            test_case = next((tc for tc in test_case if tc.test_case_id == test_case_id), None)
            if not test_case:
                raise AnalysisError(f"Test case {test_case_id} not found.")
            
            original_request = self.db_manager.get_request(test_case.request_id)
            if not original_request:
                raise AnalysisError(f"Original request for test case {test_case_id} not found.")
            
            # Correctly fetch the replayed response associated with this test case
            replayed_response_info = self.db_manager.get_replayed_response(test_case_id)
            
            if not replayed_response_info:
                # This means the replay module didn't record a response for this test case
                # This itself could be an anomaly (e.g., request timed out, blocked)
                anomaly_description = "No replayed response found for this test case. Possible timeout or block."
                anomalies.append(self.db_manager.add_anomaly(
                    test_case_id=test_case_id,
                    response_id=0, # No response ID, or a placeholder
                    type="no_response",
                    severity="High",
                    description=anomaly_description,
                    confidence_score=1.0,
                    is_potential_vulnerability=True,
                    vulnerability_type="denial_of_service" # Or similar
                ))
                return anomalies
            
            # 1. Status Code Difference
            if original_request.response_status != replayed_response_info.status_code:
                description = (
                    f"Status code changed from {original_request.response_status} "
                    f"to {replayed_response_info.status_code}."
                )
                severity = "Medium"
                is_vuln = False
                vuln_type = None
                
                # Check for specific status code rules
                for rule in self.status_code_rules:
                    if (rule["original"] == original_request.response_status and
                            rule["replayed"] == replayed_response_info.status_code):
                        severity = rule["severity"]
                        is_vuln = True
                        vuln_type = rule["type"]
                        break
                
                # Common cases
                if replayed_response_info.status_code in [401, 403]:
                    severity = "Low" # Expected for auth bypass attempts
                elif replayed_response_info.status_code == 200 and original_request.response_status in [401, 403]:
                    severity = "High" # Auth bypass success
                    is_vuln = True
                    vuln_type = "unauthorized_access"
                elif replayed_response_info.status_code >= 500:
                    severity = "High" # Server error
                    is_vuln = True
                    vuln_type = "error_disclosure"

                anomalies.append(self.db_manager.add_anomaly(
                    test_case_id=test_case_id,
                    response_id=replayed_response_info.response_id,
                    type="status_code_diff",
                    severity=severity,
                    description=description,
                    original_status=original_request.response_status,
                    replayed_status=replayed_response_info.status_code,
                    confidence_score=0.8 if is_vuln else 0.5,
                    is_potential_vulnerability=is_vuln,
                    vulnerability_type=vuln_type
                ))
            
            # 2. Content Length Variation
            original_len = original_request.response_content_length
            replayed_len = replayed_response_info.content_length
            
            if original_len and replayed_len and abs(original_len - replayed_len) > (original_len * 0.1):
                description = (
                    f"Content length changed significantly: {original_len} -> {replayed_len}."
                )
                anomalies.append(self.db_manager.add_anomaly(
                    test_case_id=test_case_id,
                    response_id=replayed_response_info.response_id,
                    type="content_length_variation",
                    severity="Low",
                    description=description,
                    original_content_length=original_len,
                    replayed_content_length=replayed_len,
                    confidence_score=0.6
                ))
            
            # 3. Keyword Detection in Replayed Response
            replayed_content_str = replayed_response_info.content.decode(
                errors='ignore').lower() if replayed_response_info.content else ""
            
            for rule in self.keyword_rules:
                if rule["keyword"].lower() in replayed_content_str:
                    keyword = rule["keyword"]
                    description = f"Keyword '{keyword}' detected in replayed response."
                    anomalies.append(self.db_manager.add_anomaly(
                        test_case_id=test_case_id,
                        response_id=replayed_response_info.response_id,
                        type=rule["type"],
                        severity=rule["severity"],
                        description=description,
                        confidence_score=0.9,
                        is_potential_vulnerability=True,
                        vulnerability_type=rule["type"]
                    ))
            
            # 4. Generic Content Anomaly (simple diff for now)
            # More advanced content comparison (e.g., DOM diff, semantic diff) can be added later
            original_content_str = original_request.response_content.decode(
                errors='ignore').lower() if original_request.response_content else ""
            
            # Check for unauthorized access based on content changes and test case category
            if test_case.category == "auth":
                if original_request.response_status in [401, 403] and replayed_response_info.status_code == 200:
                    # This case is already handled by status code difference, but reinforce here
                    description = "Authentication bypass detected: Original request was unauthorized, but replayed request was successful."
                    anomalies.append(self.db_manager.add_anomaly(
                        test_case_id=test_case_id,
                        response_id=replayed_response_info.response_id,
                        type="unauthorized_access",
                        severity="Critical",
                        description=description,
                        confidence_score=1.0,
                        is_potential_vulnerability=True,
                        vulnerability_type="unauthorized_access"
                    ))
                elif "success" in replayed_content_str and "success" not in original_content_str:
                    description = "Unexpected success message in replayed response for authentication test."
                    anomalies.append(self.db_manager.add_anomaly(
                        test_case_id=test_case_id,
                        response_id=replayed_response_info.response_id,
                        type="unauthorized_access",
                        severity="High",
                        description=description,
                        confidence_score=0.9,
                        is_potential_vulnerability=True,
                        vulnerability_type="unauthorized_access"
                    ))

            # General content difference check (after specific auth checks)
            if original_content_str and replayed_content_str and original_content_str != replayed_content_str:
                if "error" in replayed_content_str and "error" not in original_content_str:
                    description = "New error message detected in replayed response."
                    anomalies.append(self.db_manager.add_anomaly(
                        test_case_id=test_case_id,
                        response_id=replayed_response_info.response_id,
                        type="error_disclosure",
                        severity="Medium",
                        description=description,
                        confidence_score=0.7,
                        is_potential_vulnerability=True,
                        vulnerability_type="error_disclosure"
                    ))

            return anomalies
        except Exception as e:
            raise AnalysisError(f"Error analyzing test case {test_case_id}: {e}")
    
    def set_detection_threshold(self, threshold: float) -> None:
        """Set confidence threshold for anomaly detection (0.0 to 1.0)."""
        if 0.0 <= threshold <= 1.0:
            self.detection_threshold = threshold
            self.db_manager.set_config("anomaly_detection_threshold", str(threshold))
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def add_keyword_rule(self, keyword: str, anomaly_type: str, severity: str) -> int:
        """Add a keyword-based detection rule. Returns rule_id."""
        if anomaly_type not in ANOMALY_TYPES:
            raise ValueError(f"Invalid anomaly type: {anomaly_type}")
        if severity not in SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {severity}")
        
        # In a real scenario, these rules would be persisted in the DB
        rule_id = len(self.keyword_rules) + 1
        self.keyword_rules.append({"id": rule_id, "keyword": keyword, "type": anomaly_type, "severity": severity})
        return rule_id
    
    def add_status_code_rule(self, original_status: int, replayed_status: int,
                           anomaly_type: str, severity: str) -> int:
        """Add a status code comparison rule. Returns rule_id."""
        if anomaly_type not in ANOMALY_TYPES:
            raise ValueError(f"Invalid anomaly type: {anomaly_type}")
        if severity not in SEVERITY_LEVELS:
            raise ValueError(f"Invalid severity: {severity}")
        
        # In a real scenario, these rules would be persisted in the DB
        rule_id = len(self.status_code_rules) + 1
        self.status_code_rules.append({"id": rule_id, "original": original_status, 
                                       "replayed": replayed_status, "type": anomaly_type, "severity": severity})
        return rule_id
    
    def get_anomaly_types(self) -> List[str]:
        """Get list of supported anomaly types."""
        return list(ANOMALY_TYPES.keys())



