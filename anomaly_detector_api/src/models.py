"""
Data models and DTOs for the Business Logic Anomaly Detector.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, Any
import json


@dataclass
class FlowInfo:
    """Data transfer object for flow information."""
    flow_id: int
    name: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    target_domain: Optional[str] = None
    request_count: int = 0


@dataclass
class RequestInfo:
    """Data transfer object for request information."""
    request_id: int
    flow_id: int
    sequence_number: int
    url: str
    method: str
    headers: Dict[str, str]
    body: Optional[bytes] = None
    response_status: Optional[int] = None
    response_headers: Optional[Dict[str, str]] = None
    response_content_length: Optional[int] = None
    response_content: Optional[bytes] = None
    timestamp: Optional[datetime] = None


@dataclass
class TestCaseInfo:
    """Data transfer object for test case information."""
    test_case_id: int
    flow_id: int # Added flow_id
    request_id: int
    type: str
    category: str
    description: str
    payload_value: str
    modified_url: Optional[str] = None
    modified_headers: Optional[Dict[str, str]] = None
    modified_body: Optional[bytes] = None
    timestamp: Optional[datetime] = None # Changed from created_timestamp to timestamp


@dataclass
class ReplayedResponseInfo:
    """Data transfer object for replayed response information."""
    response_id: int
    test_case_id: int
    status_code: int
    headers: Dict[str, str]
    content_length: int
    content: bytes
    response_time_ms: int
    timestamp: Optional[datetime] = None


@dataclass
class AnomalyInfo:
    """Data transfer object for anomaly information."""
    anomaly_id: int
    test_case_id: int
    response_id: int
    type: str
    severity: str
    description: str
    confidence_score: float
    is_potential_vulnerability: bool = False
    vulnerability_type: Optional[str] = None
    original_status: Optional[int] = None
    replayed_status: Optional[int] = None
    original_content_length: Optional[int] = None
    replayed_content_length: Optional[int] = None
    created_timestamp: Optional[datetime] = None


@dataclass
class SessionInfo:
    """Data transfer object for session information."""
    session_id: int
    flow_id: int
    session_name: str
    cookies: Dict[str, str]
    auth_headers: Dict[str, str]
    session_data: Dict[str, Any]
    is_active: bool = True
    created_timestamp: Optional[datetime] = None
    updated_timestamp: Optional[datetime] = None


@dataclass
class PayloadRuleInfo:
    """Data transfer object for payload rule information."""
    rule_id: int
    name: str
    category: str
    rule_type: str
    template: str
    description: str
    is_enabled: bool = True
    created_timestamp: Optional[datetime] = None


class AnomalyDetectorError(Exception):
    """Base exception for the anomaly detector."""
    pass


class DatabaseError(AnomalyDetectorError):
    """Database-related errors."""
    pass


class RecordingError(AnomalyDetectorError):
    """Recording-related errors."""
    pass


class PayloadGenerationError(AnomalyDetectorError):
    """Payload generation errors."""
    pass


class ReplayError(AnomalyDetectorError):
    """Replay-related errors."""
    pass


class AnalysisError(AnomalyDetectorError):
    """Analysis-related errors."""
    pass


class ReportingError(AnomalyDetectorError):
    """Reporting-related errors."""
    pass


class ConfigurationError(AnomalyDetectorError):
    """Configuration-related errors."""
    pass

def serialize_headers(headers: Dict[str, str]) -> str:
    """Serialize headers dictionary to JSON string."""
    return json.dumps(headers) if headers else "{}"


def deserialize_headers(headers_str: str) -> Dict[str, str]:
    """Deserialize headers JSON string to dictionary."""
    try:
        return json.loads(headers_str) if headers_str else {}
    except json.JSONDecodeError:
        return {}


def serialize_session_data(data: Dict[str, Any]) -> str:
    """Serialize session data dictionary to JSON string."""
    return json.dumps(data) if data else "{}"


def deserialize_session_data(data_str: str) -> Dict[str, Any]:
    """Deserialize session data JSON string to dictionary."""
    try:
        return json.loads(data_str) if data_str else {}
    except json.JSONDecodeError:
        return {}


# Constants for anomaly types
ANOMALY_TYPES = {
    'status_code_diff': 'Different HTTP status codes',
    'content_length_variation': 'Significant content length differences',
    'unauthorized_success': 'Successful access without proper authentication',
    'business_rule_bypass': 'Bypassed business logic constraints',
    'error_disclosure': 'Internal error information disclosure',
    'redirect_anomaly': 'Unexpected redirects',
    'timing_anomaly': 'Unusual response times',
    'content_anomaly': 'Unexpected content changes'
}

# Constants for severity levels
SEVERITY_LEVELS = ['Critical', 'High', 'Medium', 'Low', 'Info']

# Constants for payload categories
PAYLOAD_CATEGORIES = {
    'numeric': 'Numeric value modifications',
    'string': 'String value modifications',
    'auth': 'Authentication modifications',
    'parameter': 'Parameter tampering',
    'sequence': 'Request sequence manipulation'
}

# Constants for HTTP methods
HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']


