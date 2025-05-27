"""
Tests for download functionality
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock

from utils.downloader import DownloadProgress, calculate_sha256, verify_checksum

class TestDownloadProgress(unittest.TestCase):
    """Test cases for DownloadProgress"""
    
    def setUp(self):
        """Set up test environment"""
        self.progress = DownloadProgress()
        self.progress.total_size = 1024 * 1024  # 1MB
    
    def test_progress_calculation(self):
        """Test progress percentage calculation"""
        self.progress.update(512 * 1024)  # 512KB
        self.assertEqual(self.progress.progress_percent, 50.0)
    
    def test_speed_calculation(self):
        """Test download speed calculation"""
        # Mock time to control speed calculation
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0, 1]  # 1 second elapsed
            
            self.progress = DownloadProgress()
            self.progress.update(1024 * 1024)  # 1MB in 1 second
            
            # Should be approximately 1 MB/s
            self.assertGreater(self.progress.speed_mbps, 0.9)
            self.assertLess(self.progress.speed_mbps, 1.1)
    
    def test_format_size(self):
        """Test file size formatting"""
        self.assertEqual(self.progress.format_size(1024), "1.0 KB")
        self.assertEqual(self.progress.format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(self.progress.format_size(1024 * 1024 * 1024), "1.0 GB")

class TestChecksumFunctions(unittest.TestCase):
    """Test cases for checksum functions"""
    
    def test_calculate_sha256(self):
        """Test SHA256 calculation"""
        # Create temporary file with known content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Hello, World!")
            temp_path = f.name
        
        try:
            # Calculate checksum
            checksum = calculate_sha256(temp_path)
            
            # Known SHA256 of "Hello, World!"
            expected = "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
            self.assertEqual(checksum, expected)
        finally:
            os.unlink(temp_path)
    
    def test_verify_checksum(self):
        """Test checksum verification"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            # Get actual checksum
            actual_checksum = calculate_sha256(temp_path)
            
            # Test verification with correct checksum
            self.assertTrue(verify_checksum(temp_path, actual_checksum))
            
            # Test verification with incorrect checksum
            wrong_checksum = "0" * 64
            self.assertFalse(verify_checksum(temp_path, wrong_checksum))
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()