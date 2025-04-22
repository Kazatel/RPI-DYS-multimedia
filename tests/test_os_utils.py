"""
Tests for os_utils module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.os_utils import get_codename, is_running_as_root, get_raspberry_pi_model


class TestOsUtils(unittest.TestCase):
    """Test cases for os_utils module"""
    
    @patch('subprocess.check_output')
    def test_get_codename_success(self, mock_check_output):
        """Test get_codename when subprocess succeeds"""
        mock_check_output.return_value = "bookworm\n"
        self.assertEqual(get_codename(), "bookworm")
    
    @patch('subprocess.check_output')
    def test_get_codename_failure(self, mock_check_output):
        """Test get_codename when subprocess fails"""
        mock_check_output.side_effect = Exception("Command failed")
        self.assertEqual(get_codename(), "unknown")
    
    @patch('os.geteuid')
    def test_is_running_as_root(self, mock_geteuid):
        """Test is_running_as_root function"""
        mock_geteuid.return_value = 0
        self.assertTrue(is_running_as_root())
        
        mock_geteuid.return_value = 1000
        self.assertFalse(is_running_as_root())
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Raspberry Pi 5 Model B Rev 1.0\x00\n")
    def test_get_raspberry_pi_model_from_file(self, mock_open, mock_exists):
        """Test get_raspberry_pi_model when file exists"""
        mock_exists.return_value = True
        self.assertEqual(get_raspberry_pi_model(), "Raspberry Pi 5 Model B Rev 1.0")
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_get_raspberry_pi_model_from_subprocess(self, mock_run, mock_exists):
        """Test get_raspberry_pi_model when file doesn't exist but subprocess works"""
        mock_exists.return_value = False
        mock_process = MagicMock()
        mock_process.stdout = "Raspberry Pi 5 Model B Rev 1.0\x00\n"
        mock_run.return_value = mock_process
        self.assertEqual(get_raspberry_pi_model(), "Raspberry Pi 5 Model B Rev 1.0")
    
    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_get_raspberry_pi_model_failure(self, mock_run, mock_exists):
        """Test get_raspberry_pi_model when all methods fail"""
        mock_exists.return_value = False
        mock_run.side_effect = Exception("Command failed")
        self.assertEqual(get_raspberry_pi_model(), "Unknown")


if __name__ == '__main__':
    unittest.main()
