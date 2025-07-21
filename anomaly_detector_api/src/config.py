"""
Configuration module for the Business Logic Anomaly Detector.
Manages application settings and configuration.
"""

import yaml
import os
from typing import Dict, Any, List, Optional

from .database import DatabaseManager
from .models import ConfigurationError


class ConfigurationManager:
    """Manages configuration settings for the anomaly detector."""
    
    def __init__(self, db_manager: DatabaseManager, config_file: str = "config.yaml"):
        """Initialize with database manager and config file."""
        self.db_manager = db_manager
        self.config_file = config_file
        self.config_cache = {}
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file and database."""
        try:
            # Load from database first
            db_config = self.db_manager.get_all_config()
            self.config_cache.update(db_config)
            
            # Load from file if it exists
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                
                # File config overrides database config
                self.config_cache.update(file_config)
                
                # Sync file config back to database
                for key, value in file_config.items():
                    self.db_manager.set_config(key, str(value))
            
            return self.config_cache
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}")
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file and database."""
        try:
            # Update cache
            self.config_cache.update(config)
            
            # Save to database
            for key, value in config.items():
                self.db_manager.set_config(key, str(value))
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_cache, f, default_flow_style=False)
            
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config_cache.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value."""
        try:
            self.config_cache[key] = value
            self.db_manager.set_config(key, str(value))
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to set configuration {key}: {e}")
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        try:
            default_config = {
                'max_concurrent_requests': 10,
                'request_delay_ms': 100,
                'timeout_seconds': 30,
                'max_payload_size': 1048576,
                'enable_numeric_payloads': True,
                'enable_string_payloads': True,
                'enable_auth_payloads': True,
                'enable_parameter_payloads': True,
                'enable_sequence_payloads': True,
                'anomaly_detection_threshold': 0.7,
                'report_format': 'html'
            }
            
            return self.save_config(default_config)
        except Exception as e:
            raise ConfigurationError(f"Failed to reset configuration: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate numeric values
        numeric_fields = {
            'max_concurrent_requests': (1, 100),
            'request_delay_ms': (0, 10000),
            'timeout_seconds': (1, 300),
            'max_payload_size': (1024, 10485760),  # 1KB to 10MB
            'anomaly_detection_threshold': (0.0, 1.0)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in config:
                try:
                    value = float(config[field])
                    if not (min_val <= value <= max_val):
                        errors.append(f"{field} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        # Validate boolean values
        boolean_fields = [
            'enable_numeric_payloads',
            'enable_string_payloads',
            'enable_auth_payloads',
            'enable_parameter_payloads',
            'enable_sequence_payloads'
        ]
        
        for field in boolean_fields:
            if field in config:
                value = config[field]
                if not isinstance(value, bool) and str(value).lower() not in ['true', 'false']:
                    errors.append(f"{field} must be a boolean value")
        
        # Validate string values
        if 'report_format' in config:
            if config['report_format'] not in ['html', 'json']:
                errors.append("report_format must be 'html' or 'json'")
        
        return errors
    
    def get_payload_settings(self) -> Dict[str, bool]:
        """Get payload generation settings."""
        return {
            'numeric': self.get('enable_numeric_payloads', True),
            'string': self.get('enable_string_payloads', True),
            'auth': self.get('enable_auth_payloads', True),
            'parameter': self.get('enable_parameter_payloads', True),
            'sequence': self.get('enable_sequence_payloads', True)
        }
    
    def set_payload_settings(self, settings: Dict[str, bool]) -> bool:
        """Set payload generation settings."""
        try:
            for category, enabled in settings.items():
                key = f'enable_{category}_payloads'
                self.set(key, enabled)
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to set payload settings: {e}")
    
    def get_replay_settings(self) -> Dict[str, Any]:
        """Get replay settings."""
        return {
            'max_concurrent_requests': int(self.get('max_concurrent_requests', 10)),
            'request_delay_ms': int(self.get('request_delay_ms', 100)),
            'timeout_seconds': int(self.get('timeout_seconds', 30))
        }
    
    def set_replay_settings(self, settings: Dict[str, Any]) -> bool:
        """Set replay settings."""
        try:
            for key, value in settings.items():
                if key in ['max_concurrent_requests', 'request_delay_ms', 'timeout_seconds']:
                    self.set(key, value)
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to set replay settings: {e}")
    
    def get_analysis_settings(self) -> Dict[str, Any]:
        """Get analysis settings."""
        return {
            'anomaly_detection_threshold': float(self.get('anomaly_detection_threshold', 0.7))
        }
    
    def set_analysis_settings(self, settings: Dict[str, Any]) -> bool:
        """Set analysis settings."""
        try:
            for key, value in settings.items():
                if key in ['anomaly_detection_threshold']:
                    self.set(key, value)
            return True
        except Exception as e:
            raise ConfigurationError(f"Failed to set analysis settings: {e}")

