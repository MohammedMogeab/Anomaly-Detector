"""
Database module for the Business Logic Anomaly Detector.
Handles all database interactions using SQLAlchemy.
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, LargeBinary, Boolean, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    FlowInfo, RequestInfo, TestCaseInfo, ReplayedResponseInfo, AnomalyInfo, SessionInfo,
    DatabaseError, serialize_headers, deserialize_headers
)

Base = declarative_base()


class Flow(Base):
    __tablename__ = 'flows'
    flow_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    target_domain = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    request_count = Column(Integer, default=0)


class Request(Base):
    __tablename__ = 'requests'
    request_id = Column(Integer, primary_key=True, autoincrement=True)
    flow_id = Column(Integer, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    url = Column(Text, nullable=False)
    method = Column(String, nullable=False)
    headers = Column(Text)  # Stored as JSON string
    body = Column(LargeBinary)  # For binary data
    response_status = Column(Integer)
    response_headers = Column(Text)  # Stored as JSON string
    response_content = Column(LargeBinary)
    response_content_length = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)


class TestCase(Base):
    __tablename__ = 'test_cases'
    test_case_id = Column(Integer, primary_key=True, autoincrement=True)
    flow_id = Column(Integer, nullable=False)
    request_id = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'numeric_modification', 'string_modification'
    category = Column(String)  # e.g., 'auth', 'parameter_tampering'
    description = Column(Text)
    payload_value = Column(Text)  # The value used in the payload
    modified_url = Column(Text)
    modified_headers = Column(Text)  # Stored as JSON string
    modified_body = Column(LargeBinary)
    timestamp = Column(DateTime, default=datetime.now)


class ReplayedResponse(Base):
    __tablename__ = 'replayed_responses'
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, nullable=False)
    status_code = Column(Integer)
    headers = Column(Text)  # Stored as JSON string
    content = Column(LargeBinary)
    content_length = Column(Integer)
    response_time_ms = Column(Integer)
    timestamp = Column(DateTime, default=datetime.now)


class Anomaly(Base):
    __tablename__ = 'anomalies'
    anomaly_id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, nullable=False)
    response_id = Column(Integer) # Can be null if no response (e.g., timeout)
    type = Column(String, nullable=False)  # e.g., 'status_code_diff', 'content_change'
    severity = Column(String, nullable=False) # e.g., 'Low', 'Medium', 'High', 'Critical'
    description = Column(Text)
    confidence_score = Column(Float)
    is_potential_vulnerability = Column(Boolean, default=False)
    vulnerability_type = Column(String) # e.g., 'unauthorized_access', 'sql_injection'
    original_status = Column(Integer)
    replayed_status = Column(Integer)
    original_content_length = Column(Integer)
    replayed_content_length = Column(Integer)
    created_timestamp = Column(DateTime, default=datetime.now)


class Configuration(Base):
    __tablename__ = 'configuration'
    key = Column(String, primary_key=True)
    value = Column(Text)


class Session(Base):
    __tablename__ = 'sessions'
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    flow_id = Column(Integer, nullable=False, unique=True)
    session_name = Column(String)
    cookies = Column(Text) # Stored as JSON string
    auth_headers = Column(Text) # Stored as JSON string
    created_timestamp = Column(DateTime, default=datetime.now)
    last_updated_timestamp = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class PayloadRule(Base):
    __tablename__ = 'payload_rules'
    rule_id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False) # e.g., 'numeric', 'string', 'auth', 'parameter', 'sequence'
    type = Column(String, nullable=False) # e.g., 'id_increment', 'sql_injection_string'
    rule_data = Column(Text) # JSON string of rule-specific data
    enabled = Column(Boolean, default=True)
    description = Column(Text)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_url: str = "sqlite:///./anomaly_detector.db"):
        """Initialize database connection and create tables."""
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def _execute_query(self, query_func, *args, **kwargs):
        """Helper to execute database queries with session management."""
        session = self.Session()
        try:
            result = query_func(session, *args, **kwargs)
            session.commit()
            return result
        except SQLAlchemyError as e:
            session.rollback()
            raise DatabaseError(f"Database operation failed: {e}") from e
        finally:
            session.close()

    def create_flow(self, name: str, description: Optional[str] = None,
                    target_domain: Optional[str] = None) -> int:
        """Create a new flow and return its ID."""
        def _query(session):
            new_flow = Flow(name=name, description=description, target_domain=target_domain)
            session.add(new_flow)
            session.flush()  # To get the flow_id before commit
            return new_flow.flow_id
        return self._execute_query(_query)

    def get_flow(self, flow_id: int) -> Optional[FlowInfo]:
        """Retrieve flow information by ID."""
        def _query(session):
            flow = session.query(Flow).filter_by(flow_id=flow_id).first()
            if flow:
                return FlowInfo(
                    flow_id=flow.flow_id,
                    name=flow.name,
                    description=flow.description,
                    target_domain=flow.target_domain,
                    timestamp=flow.timestamp,
                    request_count=flow.request_count
                )
            return None
        return self._execute_query(_query)

    def get_all_flows(self) -> List[FlowInfo]:
        """Retrieve all flows."""
        def _query(session):
            flows = session.query(Flow).all()
            return [FlowInfo(
                flow_id=flow.flow_id,
                name=flow.name,
                description=flow.description,
                target_domain=flow.target_domain,
                timestamp=flow.timestamp,
                request_count=flow.request_count
            ) for flow in flows]
        return self._execute_query(_query)

    def add_request(self, flow_id: int, sequence_number: int, url: str, method: str,
                    headers: Dict[str, str], body: Optional[bytes],
                    response_status: int, response_headers: Dict[str, str],
                    response_content: Optional[bytes]) -> int:
        """Add a new request to a flow and return its ID."""
        def _query(session):
            new_request = Request(
                flow_id=flow_id,
                sequence_number=sequence_number,
                url=url,
                method=method,
                headers=serialize_headers(headers),
                body=body,
                response_status=response_status,
                response_headers=serialize_headers(response_headers),
                response_content=response_content,
                response_content_length=len(response_content) if response_content else 0
            )
            session.add(new_request)
            session.query(Flow).filter_by(flow_id=flow_id).update({
                Flow.request_count: Flow.request_count + 1
            })
            session.flush()
            return new_request.request_id
        return self._execute_query(_query)

    def get_request(self, request_id: int) -> Optional[RequestInfo]:
        """Retrieve request information by ID."""
        def _query(session):
            request = session.query(Request).filter_by(request_id=request_id).first()
            if request:
                return RequestInfo(
                    request_id=request.request_id,
                    flow_id=request.flow_id,
                    sequence_number=request.sequence_number,
                    url=request.url,
                    method=request.method,
                    headers=deserialize_headers(request.headers),
                    body=request.body,
                    response_status=request.response_status,
                    response_headers=deserialize_headers(request.response_headers),
                    response_content=request.response_content,
                    response_content_length=request.response_content_length,
                    timestamp=request.timestamp
                )
            return None
        return self._execute_query(_query)

    def get_requests(self, flow_id: int) -> List[RequestInfo]:
        """Retrieve all requests for a given flow."""
        def _query(session):
            requests = session.query(Request).filter_by(flow_id=flow_id).order_by(Request.sequence_number).all()
            return [RequestInfo(
                request_id=req.request_id,
                flow_id=req.flow_id,
                sequence_number=req.sequence_number,
                url=req.url,
                method=req.method,
                headers=deserialize_headers(req.headers),
                body=req.body,
                response_status=req.response_status,
                response_headers=deserialize_headers(req.response_headers),
                response_content=req.response_content,
                response_content_length=req.response_content_length,
                timestamp=req.timestamp
            ) for req in requests]
        return self._execute_query(_query)

    def add_test_case(self, flow_id: int, request_id: int, type: str, category: str,
                      description: str, payload_value: str,
                      modified_url: Optional[str] = None,
                      modified_headers: Optional[Dict[str, str]] = None,
                      modified_body: Optional[bytes] = None) -> int:
        """Add a new test case and return its ID."""
        def _query(session):
            new_test_case = TestCase(
                flow_id=flow_id,
                request_id=request_id,
                type=type,
                category=category,
                description=description,
                payload_value=payload_value,
                modified_url=modified_url,
                modified_headers=serialize_headers(modified_headers) if modified_headers else None,
                modified_body=modified_body
            )
            session.add(new_test_case)
            session.flush()
            return new_test_case.test_case_id
        return self._execute_query(_query)

    def get_test_cases(self, flow_id: Optional[int] = None,
                       request_id: Optional[int] = None) -> List[TestCaseInfo]:
        """Retrieve test cases by flow ID or request ID."""
        def _query(session):
            query = session.query(TestCase)
            if flow_id is not None:
                query = query.filter_by(flow_id=flow_id)
            if request_id is not None:
                query = query.filter_by(request_id=request_id)
            test_cases = query.all()
            return [TestCaseInfo(
                test_case_id=tc.test_case_id,
                flow_id=tc.flow_id,
                request_id=tc.request_id,
                type=tc.type,
                category=tc.category,
                description=tc.description,
                payload_value=tc.payload_value,
                modified_url=tc.modified_url,
                modified_headers=deserialize_headers(tc.modified_headers) if tc.modified_headers else None,
                modified_body=tc.modified_body,
                timestamp=tc.timestamp
            ) for tc in test_cases]
        return self._execute_query(_query)

    def add_replayed_response(self, test_case_id: int, status_code: int,
                              headers: Dict[str, str], content: bytes,
                              response_time_ms: int) -> int:
        """Add a replayed response and return its ID."""
        def _query(session):
            new_response = ReplayedResponse(
                test_case_id=test_case_id,
                status_code=status_code,
                headers=serialize_headers(headers),
                content=content,
                content_length=len(content),
                response_time_ms=response_time_ms
            )
            session.add(new_response)
            session.flush()
            return new_response.response_id
        return self._execute_query(_query)

    def get_replayed_response(self, test_case_id: int) -> Optional[ReplayedResponseInfo]:
        """Retrieve replayed response for a given test case ID."""
        def _query(session):
            response = session.query(ReplayedResponse).filter_by(test_case_id=test_case_id).first()
            if response:
                return ReplayedResponseInfo(
                    response_id=response.response_id,
                    test_case_id=response.test_case_id,
                    status_code=response.status_code,
                    headers=deserialize_headers(response.headers),
                    content=response.content,
                    content_length=response.content_length,
                    response_time_ms=response.response_time_ms,
                    timestamp=response.timestamp
                )
            return None
        return self._execute_query(_query)

    def add_anomaly(self, test_case_id: int, response_id: Optional[int], type: str,
                    severity: str, description: str, confidence_score: float,
                    is_potential_vulnerability: bool = False,
                    vulnerability_type: Optional[str] = None,
                    original_status: Optional[int] = None,
                    replayed_status: Optional[int] = None,
                    original_content_length: Optional[int] = None,
                    replayed_content_length: Optional[int] = None) -> int:
        """Add a new anomaly and return its ID."""
        def _query(session):
            new_anomaly = Anomaly(
                test_case_id=test_case_id,
                response_id=response_id,
                type=type,
                severity=severity,
                description=description,
                confidence_score=confidence_score,
                is_potential_vulnerability=is_potential_vulnerability,
                vulnerability_type=vulnerability_type,
                original_status=original_status,
                replayed_status=replayed_status,
                original_content_length=original_content_length,
                replayed_content_length=replayed_content_length
            )
            session.add(new_anomaly)
            session.flush()
            return new_anomaly.anomaly_id
        return self._execute_query(_query)

    def get_anomalies(self, flow_id: Optional[int] = None,
                      test_case_id: Optional[int] = None) -> List[AnomalyInfo]:
        """Retrieve anomalies by flow ID or test case ID."""
        def _query(session):
            query = session.query(Anomaly)
            if flow_id is not None:
                # Explicitly join with TestCase and filter
                query = query.join(TestCase, Anomaly.test_case_id == TestCase.test_case_id).filter(TestCase.flow_id == flow_id)
            if test_case_id is not None:
                query = query.filter_by(test_case_id=test_case_id)
            anomalies = query.all()
            return [AnomalyInfo(
                anomaly_id=a.anomaly_id,
                test_case_id=a.test_case_id,
                response_id=a.response_id,
                type=a.type,
                severity=a.severity,
                description=a.description,
                confidence_score=a.confidence_score,
                is_potential_vulnerability=a.is_potential_vulnerability,
                vulnerability_type=a.vulnerability_type,
                original_status=a.original_status,
                replayed_status=a.replayed_status,
                original_content_length=a.original_content_length,
                replayed_content_length=a.replayed_content_length,
                created_timestamp=a.created_timestamp
            ) for a in anomalies]
        return self._execute_query(_query)

    def set_config(self, key: str, value: str) -> None:
        """Set a configuration key-value pair."""
        def _query(session):
            config = session.query(Configuration).filter_by(key=key).first()
            if config:
                config.value = value
            else:
                new_config = Configuration(key=key, value=value)
                session.add(new_config)
        self._execute_query(_query)

    def get_config(self, key: str) -> Optional[str]:
        """Get a configuration value by key."""
        def _query(session):
            config = session.query(Configuration).filter_by(key=key).first()
            return config.value if config else None
        return self._execute_query(_query)

    def get_all_config(self) -> Dict[str, str]:
        """Get all configuration key-value pairs."""
        def _query(session):
            configs = session.query(Configuration).all()
            return {c.key: c.value for c in configs}
        return self._execute_query(_query)

    def create_session(self, flow_id: int, session_name: str,
                       cookies: Optional[Dict[str, str]] = None,
                       auth_headers: Optional[Dict[str, str]] = None) -> int:
        """Create a new session and return its ID."""
        def _query(session):
            new_session = Session(
                flow_id=flow_id,
                session_name=session_name,
                cookies=json.dumps(cookies) if cookies else None,
                auth_headers=json.dumps(auth_headers) if auth_headers else None
            )
            session.add(new_session)
            session.flush()
            return new_session.session_id
        return self._execute_query(_query)

    def get_session(self, flow_id: int) -> Optional[SessionInfo]:
        """Retrieve session information by flow ID."""
        def _query(session):
            session_obj = session.query(Session).filter_by(flow_id=flow_id).first()
            if session_obj:
                return SessionInfo(
                    session_id=session_obj.session_id,
                    flow_id=session_obj.flow_id,
                    session_name=session_obj.session_name,
                    cookies=json.loads(session_obj.cookies) if session_obj.cookies else None,
                    auth_headers=json.loads(session_obj.auth_headers) if session_obj.auth_headers else None,
                    created_timestamp=session_obj.created_timestamp,
                    last_updated_timestamp=session_obj.last_updated_timestamp
                )
            return None
        return self._execute_query(_query)

    def update_session(self, session_id: int,
                       cookies: Optional[Dict[str, str]] = None,
                       auth_headers: Optional[Dict[str, str]] = None) -> bool:
        """Update an existing session."""
        def _query(session):
            session_obj = session.query(Session).filter_by(session_id=session_id).first()
            if session_obj:
                if cookies is not None:
                    session_obj.cookies = json.dumps(cookies)
                if auth_headers is not None:
                    session_obj.auth_headers = json.dumps(auth_headers)
                return True
            return False
        return self._execute_query(_query)

    def add_payload_rule(self, category: str, type: str, rule_data: Dict[str, Any], enabled: bool = True, description: Optional[str] = None) -> int:
        """Add a new payload generation rule."""
        def _query(session):
            new_rule = PayloadRule(
                category=category,
                type=type,
                rule_data=json.dumps(rule_data),
                enabled=enabled,
                description=description
            )
            session.add(new_rule)
            session.flush()
            return new_rule.rule_id
        return self._execute_query(_query)

    def get_payload_rules(self, category: Optional[str] = None, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve payload generation rules."""
        def _query(session):
            query = session.query(PayloadRule)
            if category:
                query = query.filter_by(category=category)
            if enabled_only:
                query = query.filter_by(enabled=True)
            rules = query.all()
            return [
                {
                    "rule_id": r.rule_id,
                    "category": r.category,
                    "type": r.type,
                    "rule_data": json.loads(r.rule_data),
                    "enabled": r.enabled,
                    "description": r.description
                } for r in rules
            ]
        return self._execute_query(_query)

    def close(self):
        """Close the database connection."""
        # In SQLAlchemy, sessions are typically closed after each use (as in _execute_query)
        # The engine itself manages connections in a pool, so explicit engine close is often not needed
        # unless the application is shutting down and you want to release all resources.
        pass



