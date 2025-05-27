"""
Data management utilities for Linux Distro Downloader

This module handles loading, validating, and managing distribution data.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DistroDataManager:
    """Manage distribution data and validation"""
    
    def __init__(self, data_file: str = 'distro_data.json'):
        self.data_file = Path(data_file)
        self.data = {}
        self.load_data()
    
    def load_data(self) -> bool:
        """Load distribution data from JSON file"""
        try:
            if not self.data_file.exists():
                logger.error(f"Data file not found: {self.data_file}")
                return False
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            # Validate data structure
            if self.validate_data():
                logger.info(f"Successfully loaded {len(self.data)} distributions")
                return True
            else:
                logger.error("Data validation failed")
                return False
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading data file: {e}")
            return False
    
    def validate_data(self) -> bool:
        """Validate the structure of distribution data"""
        if not isinstance(self.data, dict):
            logger.error("Root data must be a dictionary")
            return False
        
        for distro_name, distro_data in self.data.items():
            if not self.validate_distro(distro_name, distro_data):
                return False
        
        return True
    
    def validate_distro(self, name: str, data: Dict[str, Any]) -> bool:
        """Validate a single distribution entry"""
        required_fields = ['description', 'editions']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field '{field}' in distribution '{name}'")
                return False
        
        if not isinstance(data['editions'], dict):
            logger.error(f"'editions' must be a dictionary in distribution '{name}'")
            return False
        
        if not data['editions']:
            logger.error(f"No editions defined for distribution '{name}'")
            return False
        
        # Validate each edition
        for edition_name, edition_data in data['editions'].items():
            if not self.validate_edition(name, edition_name, edition_data):
                return False
        
        return True
    
    def validate_edition(self, distro_name: str, edition_name: str, data: Dict[str, Any]) -> bool:
        """Validate a single edition entry"""
        required_fields = ['filename', 'url', 'checksum']
        
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field '{field}' in edition '{edition_name}' of '{distro_name}'")
                return False
        
        # Validate URL format
        url = data['url']
        if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
            logger.error(f"Invalid URL format in edition '{edition_name}' of '{distro_name}': {url}")
            return False
        
        # Validate checksum format (should be 64 character hex string for SHA256)
        checksum = data['checksum']
        if not isinstance(checksum, str) or len(checksum) != 64:
            logger.warning(f"Checksum in edition '{edition_name}' of '{distro_name}' may not be SHA256 format")
        
        # Validate filename
        filename = data['filename']
        if not isinstance(filename, str) or not filename.strip():
            logger.error(f"Invalid filename in edition '{edition_name}' of '{distro_name}'")
            return False
        
        return True
    
    def get_distributions(self) -> List[str]:
        """Get list of available distributions"""
        return list(self.data.keys())
    
    def get_editions(self, distro_name: str) -> List[str]:
        """Get list of editions for a distribution"""
        if distro_name in self.data:
            return list(self.data[distro_name]['editions'].keys())
        return []
    
    def get_distro_info(self, distro_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a distribution"""
        return self.data.get(distro_name)
    
    def get_edition_info(self, distro_name: str, edition_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific edition"""
        if distro_name in self.data and edition_name in self.data[distro_name]['editions']:
            return self.data[distro_name]['editions'][edition_name]
        return None
    
    def get_download_info(self, distro_name: str, edition_name: str) -> Optional[Dict[str, str]]:
        """Get download information for a specific edition"""
        edition_info = self.get_edition_info(distro_name, edition_name)
        if edition_info:
            return {
                'url': edition_info['url'],
                'filename': edition_info['filename'],
                'checksum': edition_info['checksum']
            }
        return None
    
    def save_data(self) -> bool:
        """Save current data back to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the data"""
        total_distros = len(self.data)
        total_editions = sum(len(distro['editions']) for distro in self.data.values())
        
        return {
            'distributions': total_distros,
            'editions': total_editions
        }