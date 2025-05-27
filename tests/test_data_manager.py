"""
Tests for data manager functionality
"""

import unittest
import tempfile
import json
import os
from pathlib import Path

from utils.data_manager import DistroDataManager

class TestDistroDataManager(unittest.TestCase):
    """Test cases for DistroDataManager"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_data = {
            "Ubuntu": {
                "description": "Ubuntu is a popular Linux distribution",
                "editions": {
                    "Desktop": {
                        "filename": "ubuntu-22.04-desktop-amd64.iso",
                        "url": "https://releases.ubuntu.com/22.04/ubuntu-22.04-desktop-amd64.iso",
                        "checksum": "a4acfda10b18da50e2ec50ccaf860d7f20b389df8765611142305c0e911d16fd"
                    }
                }
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()
        
        self.manager = DistroDataManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment"""
        os.unlink(self.temp_file.name)
    
    def test_load_data(self):
        """Test data loading"""
        self.assertTrue(self.manager.load_data())
        self.assertEqual(len(self.manager.data), 1)
        self.assertIn('Ubuntu', self.manager.data)
    
    def test_get_distributions(self):
        """Test getting distribution list"""
        distros = self.manager.get_distributions()
        self.assertEqual(distros, ['Ubuntu'])
    
    def test_get_editions(self):
        """Test getting edition list"""
        editions = self.manager.get_editions('Ubuntu')
        self.assertEqual(editions, ['Desktop'])
        
        # Test non-existent distribution
        editions = self.manager.get_editions('NonExistent')
        self.assertEqual(editions, [])
    
    def test_get_download_info(self):
        """Test getting download information"""
        info = self.manager.get_download_info('Ubuntu', 'Desktop')
        self.assertIsNotNone(info)
        self.assertIn('url', info)
        self.assertIn('filename', info)
        self.assertIn('checksum', info)
        
        # Test non-existent edition
        info = self.manager.get_download_info('Ubuntu', 'NonExistent')
        self.assertIsNone(info)
    
    def test_validate_data(self):
        """Test data validation"""
        self.assertTrue(self.manager.validate_data())
        
        # Test invalid data
        self.manager.data = "invalid"
        self.assertFalse(self.manager.validate_data())
    
    def test_get_stats(self):
        """Test getting statistics"""
        stats = self.manager.get_stats()
        self.assertEqual(stats['distributions'], 1)
        self.assertEqual(stats['editions'], 1)

if __name__ == '__main__':
    unittest.main()