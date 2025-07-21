"""
Replay module for the Business Logic Anomaly Detector.
Replays modified requests against the target application.
"""

import httpx
import asyncio
import time
from typing import List, Dict, Any, Optional

from .database import DatabaseManager
from .models import (
    RequestInfo, TestCaseInfo, ReplayedResponseInfo, ReplayError, SessionInfo,
    deserialize_headers, serialize_headers
)


class ReplayManager:
    """Manages replaying of test cases against the target application."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        self.client = httpx.AsyncClient(verify=False) # Disable SSL verification for testing
        self.rate_limit_rps = float(self.db_manager.get_config("max_concurrent_requests") or 10)
        self.request_delay_ms = int(self.db_manager.get_config("request_delay_ms") or 100)
        self.timeout_seconds = int(self.db_manager.get_config("timeout_seconds") or 30)
    
    async def replay_flow(self, flow_id: int, max_concurrent: Optional[int] = None,
                          delay_ms: Optional[int] = None) -> int:
        """Replay all test cases for a flow. Returns count of replayed requests."""
        try:
            test_cases = self.db_manager.get_test_cases(flow_id=flow_id)
            if not test_cases:
                return 0
            
            # Group test cases by original request to handle sequence manipulation
            requests_map = {}
            for tc in test_cases:
                if tc.request_id not in requests_map:
                    requests_map[tc.request_id] = []
                requests_map[tc.request_id].append(tc)
            
            # Get original requests in sequence
            original_requests = self.db_manager.get_requests(flow_id)
            
            replayed_count = 0
            
            # Implement sequence manipulation here if needed
            # For now, replay in original request order, then all test cases for that request
            
            for original_req in original_requests:
                if original_req.request_id in requests_map:
                    for test_case in requests_map[original_req.request_id]:
                        await self._execute_replay(test_case)
                        replayed_count += 1
                        await asyncio.sleep(self.request_delay_ms / 1000.0)
            
            return replayed_count
        except Exception as e:
            raise ReplayError(f"Failed to replay flow {flow_id}: {e}")
    
    async def replay_test_cases(self, test_case_ids: List[int], max_concurrent: Optional[int] = None,
                                delay_ms: Optional[int] = None) -> int:
        """Replay specific test cases. Returns count of replayed requests."""
        try:
            replayed_count = 0
            tasks = []
            
            for tc_id in test_case_ids:
                test_cases = self.db_manager.get_test_cases(request_id=None, flow_id=None)
                test_case = next((tc for tc in test_cases if tc.test_case_id == tc_id), None)
                if test_case:
                    tasks.append(self._execute_replay(test_case))
                    replayed_count += 1
            
            if tasks:
                # Use a semaphore for concurrency control
                semaphore = asyncio.Semaphore(max_concurrent or self.rate_limit_rps)
                async def limited_task(task):
                    async with semaphore:
                        return await task
                await asyncio.gather(*[limited_task(task) for task in tasks])
            
            return replayed_count
        except Exception as e:
            raise ReplayError(f"Failed to replay specific test cases: {e}")
    
    async def _execute_replay(self, test_case: TestCaseInfo) -> ReplayedResponseInfo:
        """Execute a single replayed request and store the response."""
        original_request = self.db_manager.get_request(test_case.request_id)
        if not original_request:
            raise ReplayError(f"Original request for test case {test_case.test_case_id} not found.")
        
        url = test_case.modified_url or original_request.url
        headers = test_case.modified_headers or original_request.headers
        body = test_case.modified_body or original_request.body
        method = original_request.method
        
        start_time = time.time()
        try:
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                timeout=self.timeout_seconds
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            response_id = self.db_manager.add_replayed_response(
                test_case_id=test_case.test_case_id,
                status_code=response.status_code,
                headers=dict(response.headers),
                content=response.content,
                response_time_ms=response_time_ms
            )
            
            return ReplayedResponseInfo(
                response_id=response_id,
                test_case_id=test_case.test_case_id,
                status_code=response.status_code,
                headers=dict(response.headers),
                content_length=len(response.content),
                content=response.content,
                response_time_ms=response_time_ms
            )
        except httpx.RequestError as e:
            # Handle network errors, timeouts, etc.
            error_msg = f"Request failed for {url}: {e}"
            print(f"Error: {error_msg}")
            # Store a placeholder response indicating failure
            response_id = self.db_manager.add_replayed_response(
                test_case_id=test_case.test_case_id,
                status_code=0, # Indicate error
                headers={}, # Empty headers
                content=error_msg.encode(),
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            raise ReplayError(error_msg) from e
    
    def set_session_data(self, flow_id: int, cookies: Dict[str, str] = None,
                        auth_headers: Dict[str, str] = None) -> bool:
        """Set session data for maintaining authentication state."""
        session = self.db_manager.get_session(flow_id)
        if session:
            return self.db_manager.update_session(
                session.session_id, cookies=cookies, auth_headers=auth_headers
            )
        else:
            # Create a new session if one doesn't exist for this flow
            session_id = self.db_manager.create_session(
                flow_id=flow_id, session_name=f"flow_{flow_id}_session",
                cookies=cookies, auth_headers=auth_headers
            )
            return session_id is not None
    
    def get_session_data(self, flow_id: int) -> Optional[SessionInfo]:
        """Get current session data for a flow."""
        return self.db_manager.get_session(flow_id)
    
    def set_rate_limit(self, requests_per_second: float) -> None:
        """Set rate limiting for requests."""
        self.rate_limit_rps = requests_per_second
        self.db_manager.set_config("max_concurrent_requests", str(requests_per_second))
    
    def set_timeout(self, timeout_seconds: int) -> None:
        """Set request timeout."""
        self.timeout_seconds = timeout_seconds
        self.db_manager.set_config("timeout_seconds", str(timeout_seconds))
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()

