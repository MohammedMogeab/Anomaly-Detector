"""
Payload generation module for the Business Logic Anomaly Detector.
Generates various types of malicious and anomalous payloads.
"""

import json
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode

from .database import DatabaseManager
from .models import RequestInfo, TestCaseInfo, PayloadGenerationError


class PayloadGenerator:
    """Generates various types of payloads for business logic testing."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize with database manager."""
        self.db_manager = db_manager
        self.config = self.db_manager.get_all_config()
        self._initialize_default_rules()

    def _initialize_default_rules(self):
        """Initialize default payload generation rules if they don't exist."""
        # Numeric modification rules
        if not self.db_manager.get_payload_rules(category='numeric'):
            self.db_manager.add_payload_rule(
                category='numeric', type='id_increment', 
                rule_data={'increment_by': 1, 'max_increment': 5}, 
                description='Increment numeric IDs in URL paths and query parameters.'
            )
            self.db_manager.add_payload_rule(
                category='numeric', type='id_decrement', 
                rule_data={'decrement_by': 1, 'max_decrement': 5}, 
                description='Decrement numeric IDs in URL paths and query parameters.'
            )
            self.db_manager.add_payload_rule(
                category='numeric', type='large_number', 
                rule_data={'value': 999999999}, 
                description='Replace numeric values with a large number.'
            )
            self.db_manager.add_payload_rule(
                category='numeric', type='zero_value', 
                rule_data={'value': 0}, 
                description='Replace numeric values with zero.'
            )

        # String modification rules
        if not self.db_manager.get_payload_rules(category='string'):
            self.db_manager.add_payload_rule(
                category='string', type='sql_injection_string', 
                rule_data={'payloads': [


"' OR 1=1--", "' UNION SELECT NULL,NULL,NULL--"], 'position': 'append'}, 
                description='Append common SQL injection strings.'
            )
            self.db_manager.add_payload_rule(
                category='string', type='xss_string', 
                rule_data={'payloads': ['<script>alert(1)</script>', '" onmouseover="alert(1)"'], 'position': 'append'}, 
                description='Append common XSS strings.'
            )
            self.db_manager.add_payload_rule(
                category='string', type='path_traversal_string', 
                rule_data={'payloads': ['../', '..\\'], 'position': 'prepend'}, 
                description='Prepend path traversal sequences.'
            )

        # Authentication modification rules
        if not self.db_manager.get_payload_rules(category='auth'):
            self.db_manager.add_payload_rule(
                category='auth', type='invalid_token', 
                rule_data={'header_name': 'Authorization', 'value': 'Bearer invalid_token'}, 
                description='Replace Authorization header with an invalid token.'
            )
            self.db_manager.add_payload_rule(
                category='auth', type='no_token', 
                rule_data={'header_name': 'Authorization'}, 
                description='Remove Authorization header.'
            )
            self.db_manager.add_payload_rule(
                category='auth', type='session_fixation_cookie', 
                rule_data={'cookie_name': 'JSESSIONID', 'value': 'fixed_session_id'}, 
                description='Set a fixed session ID cookie.'
            )

        # Parameter tampering rules
        if not self.db_manager.get_payload_rules(category='parameter'):
            self.db_manager.add_payload_rule(
                category='parameter', type='change_boolean', 
                rule_data={'values': ['true', 'false', '1', '0']}, 
                description='Toggle boolean parameter values.'
            )
            self.db_manager.add_payload_rule(
                category='parameter', type='change_enum', 
                rule_data={'values': ['admin', 'user', 'guest']}, 
                description='Change enum parameter values to common roles.'
            )
            self.db_manager.add_payload_rule(
                category='parameter', type='null_byte_injection', 
                rule_data={'value': '%00'}, 
                description='Append null byte to parameter values.'
            )

        # Sequence manipulation rules
        if not self.db_manager.get_payload_rules(category='sequence'):
            self.db_manager.add_payload_rule(
                category='sequence', type='reorder_requests', 
                rule_data={'reorder_pairs': [[1, 2], [2, 1]]}, 
                description='Reorder pairs of requests within a flow.'
            )
            self.db_manager.add_payload_rule(
                category='sequence', type='skip_request', 
                rule_data={'skip_indices': [0]}, 
                description='Skip specific requests in a flow.'
            )
            self.db_manager.add_payload_rule(
                category='sequence', type='repeat_request', 
                rule_data={'repeat_index': 0, 'times': 2}, 
                description='Repeat a specific request multiple times.'
            )

    def generate_for_request(self, request_id: int) -> int:
        """Generate test cases for a given request."""
        try:
            request = self.db_manager.get_request(request_id)
            if not request:
                raise PayloadGenerationError(f"Request {request_id} not found.")

            generated_count = 0

            # Numeric modifications
            if self.config.get('enable_numeric_payloads', True):
                generated_count += self._generate_numeric_payloads(request)

            # String modifications
            if self.config.get('enable_string_payloads', True):
                generated_count += self._generate_string_payloads(request)

            # Authentication modifications
            if self.config.get('enable_auth_payloads', True):
                generated_count += self._generate_auth_payloads(request)

            # Parameter tampering
            if self.config.get('enable_parameter_payloads', True):
                generated_count += self._generate_parameter_payloads(request)

            # Sequence manipulation (handled at flow level, not per request)
            # if self.config.get('enable_sequence_payloads', True):
            #     generated_count += self._generate_sequence_payloads(request)

            return generated_count
        except Exception as e:
            raise PayloadGenerationError(f"Failed to generate test cases for request {request_id}: {e}")

    def _generate_numeric_payloads(self, request: RequestInfo) -> int:
        """Generate numeric modification payloads."""
        generated_count = 0
        rules = self.db_manager.get_payload_rules(category='numeric', enabled_only=True)

        # URL path parameters (e.g., /users/123)
        path_segments = request.url.split('/')
        for i, segment in enumerate(path_segments):
            if segment.isdigit():
                original_value = int(segment)
                for rule in rules:
                    modified_value = None
                    if rule['type'] == 'id_increment':
                        modified_value = original_value + rule['rule_data']['increment_by']
                    elif rule['type'] == 'id_decrement':
                        modified_value = original_value - rule['rule_data']['decrement_by']
                    elif rule['type'] == 'large_number':
                        modified_value = rule['rule_data']['value']
                    elif rule['type'] == 'zero_value':
                        modified_value = rule['rule_data']['value']

                    if modified_value is not None:
                        new_path_segments = list(path_segments)
                        new_path_segments[i] = str(modified_value)
                        modified_url = '/'.join(new_path_segments)
                        self.db_manager.add_test_case(
                            flow_id=request.flow_id,
                            request_id=request.request_id,
                            type=rule['type'],
                            category='numeric',
                            description=f"Increment ID parameter path_segment_{i}: {original_value} -> {modified_value}",
                            payload_value=str(modified_value),
                            modified_url=modified_url
                        )
                        generated_count += 1

        # URL query parameters (e.g., ?id=123)
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)
        for param, values in query_params.items():
            for i, value in enumerate(values):
                if value.isdigit():
                    original_value = int(value)
                    for rule in rules:
                        modified_value = None
                        if rule['type'] == 'id_increment':
                            modified_value = original_value + rule['rule_data']['increment_by']
                        elif rule['type'] == 'id_decrement':
                            modified_value = original_value - rule['rule_data']['decrement_by']
                        elif rule['type'] == 'large_number':
                            modified_value = rule['rule_data']['value']
                        elif rule['type'] == 'zero_value':
                            modified_value = rule['rule_data']['value']

                        if modified_value is not None:
                            new_query_params = query_params.copy()
                            new_query_params[param] = values[:i] + [str(modified_value)] + values[i+1:]
                            modified_query = urlencode(new_query_params, doseq=True)
                            modified_url = parsed_url._replace(query=modified_query).geturl()
                            self.db_manager.add_test_case(
                                flow_id=request.flow_id,
                                request_id=request.request_id,
                                type=rule['type'],
                                category='numeric',
                                description=f"Increment ID parameter {param}: {original_value} -> {modified_value}",
                                payload_value=str(modified_value),
                                modified_url=modified_url
                            )
                            generated_count += 1

        # JSON body parameters (if applicable)
        if request.body and 'application/json' in request.headers.get('Content-Type', ''):
            try:
                json_body = json.loads(request.body)
                # Recursively find and modify numeric values in JSON
                modified_json_bodies = self._modify_json_numeric(json_body, rules)
                for modified_body_data in modified_json_bodies:
                    modified_body_bytes = json.dumps(modified_body_data['json']).encode('utf-8')
                    self.db_manager.add_test_case(
                        flow_id=request.flow_id,
                        request_id=request.request_id,
                        type=modified_body_data['rule_type'],
                        category='numeric',
                        description=f"Numeric modification in JSON body: {modified_body_data['description']}",
                        payload_value=str(modified_body_data['payload_value']),
                        modified_body=modified_body_bytes
                    )
                    generated_count += 1
            except json.JSONDecodeError:
                pass # Not a valid JSON body

        return generated_count

    def _modify_json_numeric(self, data: Any, rules: List[Dict[str, Any]], path: str = '') -> List[Dict[str, Any]]:
        """Recursively modify numeric values in a JSON object/array."""
        results = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, (int, float)):
                    for rule in rules:
                        modified_value = None
                        if rule['type'] == 'id_increment':
                            modified_value = value + rule['rule_data']['increment_by']
                        elif rule['type'] == 'id_decrement':
                            modified_value = value - rule['rule_data']['decrement_by']
                        elif rule['type'] == 'large_number':
                            modified_value = rule['rule_data']['value']
                        elif rule['type'] == 'zero_value':
                            modified_value = rule['rule_data']['value']

                        if modified_value is not None:
                            new_data = json.loads(json.dumps(data)) # Deep copy
                            self._set_json_value(new_data, current_path, modified_value)
                            results.append({
                                'json': new_data,
                                'rule_type': rule['type'],
                                'payload_value': modified_value,
                                'description': f"Changed {current_path} from {value} to {modified_value}"
                            })
                else:
                    sub_results = self._modify_json_numeric(value, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, (int, float)):
                    for rule in rules:
                        modified_value = None
                        if rule['type'] == 'id_increment':
                            modified_value = item + rule['rule_data']['increment_by']
                        elif rule['type'] == 'id_decrement':
                            modified_value = item - rule['rule_data']['decrement_by']
                        elif rule['type'] == 'large_number':
                            modified_value = rule['rule_data']['value']
                        elif rule['type'] == 'zero_value':
                            modified_value = rule['rule_data']['value']

                        if modified_value is not None:
                            new_data = json.loads(json.dumps(data))
                            self._set_json_value(new_data, current_path, modified_value)
                            results.append({
                                'json': new_data,
                                'rule_type': rule['type'],
                                'payload_value': modified_value,
                                'description': f"Changed {current_path} from {item} to {modified_value}"
                            })
                else:
                    sub_results = self._modify_json_numeric(item, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        return results

    def _set_json_value(self, obj: Any, path: str, value: Any):
        """Helper to set a value in a nested JSON object/array by path."""
        parts = re.findall(r'[^.[\]]+|\[\d+\]', path)
        for i, part in enumerate(parts):
            if part.startswith('['):
                index = int(part[1:-1])
                if i == len(parts) - 1:
                    obj[index] = value
                else:
                    obj = obj[index]
            else:
                if i == len(parts) - 1:
                    obj[part] = value
                else:
                    obj = obj[part]

    def _generate_string_payloads(self, request: RequestInfo) -> int:
        """Generate string modification payloads."""
        generated_count = 0
        rules = self.db_manager.get_payload_rules(category='string', enabled_only=True)

        # Apply to URL query parameters
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)
        for param, values in query_params.items():
            for i, value in enumerate(values):
                for rule in rules:
                    modified_value = value
                    if rule['rule_data']['position'] == 'append':
                        for p in rule['rule_data']['payloads']:
                            modified_value = value + p
                            new_query_params = query_params.copy()
                            new_query_params[param] = values[:i] + [modified_value] + values[i+1:]
                            modified_query = urlencode(new_query_params, doseq=True)
                            modified_url = parsed_url._replace(query=modified_query).geturl()
                            self.db_manager.add_test_case(
                                flow_id=request.flow_id,
                                request_id=request.request_id,
                                type=rule['type'],
                                category='string',
                                description=f"String modification in query param {param}: {value} -> {modified_value}",
                                payload_value=modified_value,
                                modified_url=modified_url
                            )
                            generated_count += 1
                    elif rule['rule_data']['position'] == 'prepend':
                        for p in rule['rule_data']['payloads']:
                            modified_value = p + value
                            new_query_params = query_params.copy()
                            new_query_params[param] = values[:i] + [modified_value] + values[i+1:]
                            modified_query = urlencode(new_query_params, doseq=True)
                            modified_url = parsed_url._replace(query=modified_query).geturl()
                            self.db_manager.add_test_case(
                                flow_id=request.flow_id,
                                request_id=request.request_id,
                                type=rule['type'],
                                category='string',
                                description=f"String modification in query param {param}: {value} -> {modified_value}",
                                payload_value=modified_value,
                                modified_url=modified_url
                            )
                            generated_count += 1

        # Apply to JSON body parameters
        if request.body and 'application/json' in request.headers.get('Content-Type', ''):
            try:
                json_body = json.loads(request.body)
                modified_json_bodies = self._modify_json_string(json_body, rules)
                for modified_body_data in modified_json_bodies:
                    modified_body_bytes = json.dumps(modified_body_data['json']).encode('utf-8')
                    self.db_manager.add_test_case(
                        flow_id=request.flow_id,
                        request_id=request.request_id,
                        type=modified_body_data['rule_type'],
                        category='string',
                        description=f"String modification in JSON body: {modified_body_data['description']}",
                        payload_value=str(modified_body_data['payload_value']),
                        modified_body=modified_body_bytes
                    )
                    generated_count += 1
            except json.JSONDecodeError:
                pass

        return generated_count

    def _modify_json_string(self, data: Any, rules: List[Dict[str, Any]], path: str = '') -> List[Dict[str, Any]]:
        """Recursively modify string values in a JSON object/array."""
        results = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    for rule in rules:
                        for p in rule['rule_data']['payloads']:
                            modified_value = value
                            if rule['rule_data']['position'] == 'append':
                                modified_value = value + p
                            elif rule['rule_data']['position'] == 'prepend':
                                modified_value = p + value

                            new_data = json.loads(json.dumps(data))
                            self._set_json_value(new_data, current_path, modified_value)
                            results.append({
                                'json': new_data,
                                'rule_type': rule['type'],
                                'payload_value': modified_value,
                                'description': f"Changed {current_path} from '{value}' to '{modified_value}'"
                            })
                else:
                    sub_results = self._modify_json_string(value, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                if isinstance(item, str):
                    for rule in rules:
                        for p in rule['rule_data']['payloads']:
                            modified_value = item
                            if rule['rule_data']['position'] == 'append':
                                modified_value = item + p
                            elif rule['rule_data']['position'] == 'prepend':
                                modified_value = p + item

                            new_data = json.loads(json.dumps(data))
                            self._set_json_value(new_data, current_path, modified_value)
                            results.append({
                                'json': new_data,
                                'rule_type': rule['type'],
                                'payload_value': modified_value,
                                'description': f"Changed {current_path} from '{item}' to '{modified_value}'"
                            })
                else:
                    sub_results = self._modify_json_string(item, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        return results

    def _generate_auth_payloads(self, request: RequestInfo) -> int:
        """Generate authentication modification payloads."""
        generated_count = 0
        rules = self.db_manager.get_payload_rules(category='auth', enabled_only=True)

        for rule in rules:
            modified_headers = request.headers.copy()
            description = ""
            payload_value = ""

            if rule['type'] == 'invalid_token':
                header_name = rule['rule_data']['header_name']
                modified_headers[header_name] = rule['rule_data']['value']
                description = f"Set invalid token in {header_name} header."
                payload_value = rule['rule_data']['value']
            elif rule['type'] == 'no_token':
                header_name = rule['rule_data']['header_name']
                if header_name in modified_headers:
                    del modified_headers[header_name]
                description = f"Remove {header_name} header."
                payload_value = "<removed>"
            elif rule['type'] == 'session_fixation_cookie':
                cookie_name = rule['rule_data']['cookie_name']
                fixed_value = rule['rule_data']['value']
                # This is a simplified approach; real cookie modification is more complex
                # and might involve parsing/rebuilding the Cookie header.
                # For now, we'll just add/overwrite a simple cookie.
                modified_headers['Cookie'] = f"{cookie_name}={fixed_value}"
                description = f"Set fixed session cookie {cookie_name} to {fixed_value}."
                payload_value = fixed_value

            if description:
                self.db_manager.add_test_case(
                    flow_id=request.flow_id,
                    request_id=request.request_id,
                    type=rule['type'],
                    category='auth',
                    description=description,
                    payload_value=payload_value,
                    modified_headers=modified_headers
                )
                generated_count += 1
        return generated_count

    def _generate_parameter_payloads(self, request: RequestInfo) -> int:
        """Generate parameter tampering payloads."""
        generated_count = 0
        rules = self.db_manager.get_payload_rules(category='parameter', enabled_only=True)

        # Apply to URL query parameters
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)
        for param, values in query_params.items():
            for i, value in enumerate(values):
                for rule in rules:
                    modified_value = None
                    if rule['type'] == 'change_boolean':
                        if value.lower() in ['true', 'false', '1', '0']:
                            for new_val in rule['rule_data']['values']:
                                if new_val != value:
                                    modified_value = new_val
                                    break
                    elif rule['type'] == 'change_enum':
                        for new_val in rule['rule_data']['values']:
                            if new_val != value:
                                modified_value = new_val
                                break
                    elif rule['type'] == 'null_byte_injection':
                        modified_value = value + rule['rule_data']['value']

                    if modified_value is not None:
                        new_query_params = query_params.copy()
                        new_query_params[param] = values[:i] + [modified_value] + values[i+1:]
                        modified_query = urlencode(new_query_params, doseq=True)
                        modified_url = parsed_url._replace(query=modified_query).geturl()
                        self.db_manager.add_test_case(
                            flow_id=request.flow_id,
                            request_id=request.request_id,
                            type=rule['type'],
                            category='parameter',
                            description=f"Parameter tampering in query param {param}: {value} -> {modified_value}",
                            payload_value=modified_value,
                            modified_url=modified_url
                        )
                        generated_count += 1

        # Apply to JSON body parameters
        if request.body and 'application/json' in request.headers.get('Content-Type', ''):
            try:
                json_body = json.loads(request.body)
                modified_json_bodies = self._modify_json_parameter(json_body, rules)
                for modified_body_data in modified_json_bodies:
                    modified_body_bytes = json.dumps(modified_body_data['json']).encode('utf-8')
                    self.db_manager.add_test_case(
                        flow_id=request.flow_id,
                        request_id=request.request_id,
                        type=modified_body_data['rule_type'],
                        category='parameter',
                        description=f"Parameter tampering in JSON body: {modified_body_data['description']}",
                        payload_value=str(modified_body_data['payload_value']),
                        modified_body=modified_body_bytes
                    )
                    generated_count += 1
            except json.JSONDecodeError:
                pass

        return generated_count

    def _modify_json_parameter(self, data: Any, rules: List[Dict[str, Any]], path: str = '') -> List[Dict[str, Any]]:
        """Recursively modify parameter values in a JSON object/array."""
        results = []
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                for rule in rules:
                    modified_value = None
                    if rule['type'] == 'change_boolean':
                        if isinstance(value, (bool, int)) or (isinstance(value, str) and value.lower() in ['true', 'false', '1', '0']):
                            for new_val in rule['rule_data']['values']:
                                if str(new_val).lower() != str(value).lower():
                                    modified_value = new_val
                                    break
                    elif rule['type'] == 'change_enum':
                        if isinstance(value, str):
                            for new_val in rule['rule_data']['values']:
                                if new_val != value:
                                    modified_value = new_val
                                    break
                    elif rule['type'] == 'null_byte_injection':
                        if isinstance(value, str):
                            modified_value = value + rule['rule_data']['value']

                    if modified_value is not None:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, modified_value)
                        results.append({
                            'json': new_data,
                            'rule_type': rule['type'],
                            'payload_value': modified_value,
                            'description': f"Changed {current_path} from '{value}' to '{modified_value}'"
                        })
                else:
                    sub_results = self._modify_json_parameter(value, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                for rule in rules:
                    modified_value = None
                    if rule['type'] == 'change_boolean':
                        if isinstance(item, (bool, int)) or (isinstance(item, str) and item.lower() in ['true', 'false', '1', '0']):
                            for new_val in rule['rule_data']['values']:
                                if str(new_val).lower() != str(item).lower():
                                    modified_value = new_val
                                    break
                    elif rule['type'] == 'change_enum':
                        if isinstance(item, str):
                            for new_val in rule['rule_data']['values']:
                                if new_val != item:
                                    modified_value = new_val
                                    break
                    elif rule['type'] == 'null_byte_injection':
                        if isinstance(item, str):
                            modified_value = item + rule['rule_data']['value']

                    if modified_value is not None:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, modified_value)
                        results.append({
                            'json': new_data,
                            'rule_type': rule['type'],
                            'payload_value': modified_value,
                            'description': f"Changed {current_path} from '{item}' to '{modified_value}'"
                        })
                else:
                    sub_results = self._modify_json_parameter(item, rules, current_path)
                    for sub_res in sub_results:
                        new_data = json.loads(json.dumps(data))
                        self._set_json_value(new_data, current_path, sub_res['json'])
                        results.append({
                            'json': new_data,
                            'rule_type': sub_res['rule_type'],
                            'payload_value': sub_res['payload_value'],
                            'description': sub_res['description']
                        })
        return results

    def generate_for_flow_sequence(self, flow_id: int) -> int:
        """Generate sequence manipulation test cases for a given flow."""
        generated_count = 0
        rules = self.db_manager.get_payload_rules(category='sequence', enabled_only=True)
        original_requests = self.db_manager.get_requests(flow_id)

        for rule in rules:
            if rule['type'] == 'reorder_requests':
                for pair in rule['rule_data']['reorder_pairs']:
                    if len(original_requests) >= max(pair):
                        # Create a new sequence by reordering
                        reordered_requests = list(original_requests)
                        reordered_requests[pair[0]-1], reordered_requests[pair[1]-1] = \
                            reordered_requests[pair[1]-1], reordered_requests[pair[0]-1]
                        
                        # Store this as a test case for sequence manipulation
                        # This is a conceptual test case, actual replay logic needs to handle it
                        self.db_manager.add_test_case(
                            flow_id=flow_id,
                            request_id=original_requests[0].request_id, # Associate with first request for now
                            type=rule['type'],
                            category='sequence',
                            description=f"Reorder requests: {pair[0]} and {pair[1]}",
                            payload_value=json.dumps([r.request_id for r in reordered_requests]),
                            modified_url=None, # Not applicable for sequence
                            modified_headers=None,
                            modified_body=None
                        )
                        generated_count += 1
            elif rule['type'] == 'skip_request':
                for skip_index in rule['rule_data']['skip_indices']:
                    if len(original_requests) > skip_index:
                        skipped_requests = [r for i, r in enumerate(original_requests) if i != skip_index]
                        self.db_manager.add_test_case(
                            flow_id=flow_id,
                            request_id=original_requests[0].request_id,
                            type=rule['type'],
                            category='sequence',
                            description=f"Skip request at index {skip_index}",
                            payload_value=json.dumps([r.request_id for r in skipped_requests]),
                            modified_url=None,
                            modified_headers=None,
                            modified_body=None
                        )
                        generated_count += 1
            elif rule['type'] == 'repeat_request':
                repeat_index = rule['rule_data']['repeat_index']
                times = rule['rule_data']['times']
                if len(original_requests) > repeat_index:
                    repeated_requests = list(original_requests)
                    repeated_requests.extend([original_requests[repeat_index]] * (times - 1))
                    self.db_manager.add_test_case(
                        flow_id=flow_id,
                        request_id=original_requests[0].request_id,
                        type=rule['type'],
                        category='sequence',
                        description=f"Repeat request at index {repeat_index} {times} times",
                        payload_value=json.dumps([r.request_id for r in repeated_requests]),
                        modified_url=None,
                        modified_headers=None,
                        modified_body=None
                    )
                    generated_count += 1

        return generated_count





