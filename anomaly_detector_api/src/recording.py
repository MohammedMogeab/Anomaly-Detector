"""
Recording module for the Business Logic Anomaly Detector.
Handles capturing HTTP traffic and storing it in the database.
"""

import json
import os
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .database import DatabaseManager
from .models import RecordingError, RequestInfo


class RecordingManager:
    """Manages recording of HTTP flows."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        self.current_flow_id: Optional[int] = None
        self.current_flow_name: Optional[str] = None
        self.request_sequence_numbers: Dict[int, int] = {}
    
    def start_recording(self, flow_name: str, description: Optional[str] = None,
                       target_domain: Optional[str] = None) -> int:
        """Start recording a new flow. Returns flow_id."""
        if self.is_recording():
            raise RecordingError(f"Already recording flow: {self.current_flow_name}")
        
        try:
            flow_id = self.db_manager.create_flow(flow_name, description, target_domain)
            self.current_flow_id = flow_id
            self.current_flow_name = flow_name
            self.request_sequence_numbers[flow_id] = 0
            return flow_id
        except Exception as e:
            raise RecordingError(f"Failed to start recording flow {flow_name}: {e}")
    
    def stop_recording(self) -> bool:
        """Stop current recording session."""
        if not self.is_recording():
            return False
        
        self.current_flow_id = None
        self.current_flow_name = None
        return True
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.current_flow_id is not None
    
    def get_current_flow_id(self) -> Optional[int]:
        """Get the ID of currently recording flow."""
        return self.current_flow_id
    
    def add_recorded_request(self, url: str, method: str, headers: Dict[str, str],
                             body: Optional[bytes], response_status: int,
                             response_headers: Dict[str, str], response_content: Optional[bytes]) -> int:
        """Add a single recorded request to the current flow."""
        if not self.is_recording():
            raise RecordingError("Not currently recording any flow.")
        
        flow_id = self.current_flow_id
        self.request_sequence_numbers[flow_id] += 1
        sequence_number = self.request_sequence_numbers[flow_id]
        
        try:
            request_id = self.db_manager.add_request(
                flow_id=flow_id,
                sequence_number=sequence_number,
                url=url,
                method=method,
                headers=headers,
                body=body,
                response_status=response_status,
                response_headers=response_headers,
                response_content=response_content
            )
            return request_id
        except Exception as e:
            raise RecordingError(f"Failed to add recorded request to flow {flow_id}: {e}")
    
    def import_from_har(self, har_file_path: str, flow_name: str,
                       description: Optional[str] = None) -> int:
        """Import requests from HAR file. Returns flow_id."""
        if not os.path.exists(har_file_path):
            raise RecordingError(f"HAR file not found: {har_file_path}")
        
        try:
            with open(har_file_path, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
            
            entries = har_data.get("log", {}).get("entries", [])
            if not entries:
                raise RecordingError("No entries found in HAR file.")
            
            # Determine target domain from first entry
            first_url = entries[0]["request"]["url"]
            parsed_url = urlparse(first_url)
            target_domain = parsed_url.netloc
            
            flow_id = self.db_manager.create_flow(flow_name, description, target_domain)
            self.request_sequence_numbers[flow_id] = 0
            
            for entry in entries:
                request = entry.get("request", {})
                response = entry.get("response", {})
                
                url = request.get("url")
                method = request.get("method")
                
                headers = {h["name"]: h["value"] for h in request.get("headers", [])}
                post_data = request.get("postData", {})
                body = post_data.get("text", "").encode("utf-8") if post_data else None
                
                response_status = response.get("status")
                response_headers = {h["name"]: h["value"] for h in response.get("headers", [])}
                response_content = response.get("content", {}).get("text", "").encode("utf-8")
                
                self.request_sequence_numbers[flow_id] += 1
                sequence_number = self.request_sequence_numbers[flow_id]
                
                self.db_manager.add_request(
                    flow_id=flow_id,
                    sequence_number=sequence_number,
                    url=url,
                    method=method,
                    headers=headers,
                    body=body,
                    response_status=response_status,
                    response_headers=response_headers,
                    response_content=response_content
                )
            
            return flow_id
        except Exception as e:
            raise RecordingError(f"Failed to import from HAR file {har_file_path}: {e}")
    
    def import_from_burp(self, burp_file_path: str, flow_name: str,
                        description: Optional[str] = None) -> int:
        """Import requests from Burp Suite XML export. Returns flow_id."""
        # This would require parsing Burp XML format, which is more complex.
        # For now, we can raise a NotImplementedError or provide a placeholder.
        raise NotImplementedError("Import from Burp Suite XML is not yet implemented.")



