"""
Tests for config_validator module
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import types

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.config_validator import validate_config, validate_user_exists, validate_path_exists
from utils.exceptions import ValidationError, ConfigurationError


class TestConfigValidator(unittest.TestCase):
    """Test cases for config_validator module"""
    
    def test_validate_config_minimal_valid(self):
        """Test validate_config with minimal valid config"""
        # Create a minimal valid config
        mock_config = types.ModuleType('config')
        mock_config.USER = 'testuser'
        mock_config.APPLICATIONS = {
            'app1': {'enabled': True, 'user': 'testuser'}
        }
        mock_config.LOG_DIR = '/tmp'
        mock_config.TESTED_OS_VERSION = ['bookworm']
        mock_config.TESTED_MODELS = ['Raspberry Pi 5']
        
        # Should not raise an exception
        self.assertTrue(validate_config(mock_config))
    
    def test_validate_config_missing_user(self):
        """Test validate_config with missing USER"""
        # Create an invalid config
        mock_config = types.ModuleType('config')
        mock_config.APPLICATIONS = {
            'app1': {'enabled': True, 'user': 'testuser'}
        }
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError):
            validate_config(mock_config)
    
    def test_validate_config_missing_applications(self):
        """Test validate_config with missing APPLICATIONS"""
        # Create an invalid config
        mock_config = types.ModuleType('config')
        mock_config.USER = 'testuser'
        
        # Should raise ConfigurationError
        with self.assertRaises(ConfigurationError):
            validate_config(mock_config)
    
    @patch('pwd.getpwnam')
    def test_validate_user_exists_valid(self, mock_getpwnam):
        """Test validate_user_exists with valid user"""
        mock_getpwnam.return_value = MagicMock()
        self.assertTrue(validate_user_exists('testuser'))
    
    @patch('pwd.getpwnam')
    def test_validate_user_exists_invalid(self, mock_getpwnam):
        """Test validate_user_exists with invalid user"""
        mock_getpwnam.side_effect = KeyError('User not found')
        with self.assertRaises(ValidationError):
            validate_user_exists('nonexistentuser')
    
    @patch('os.path.exists')
    def test_validate_path_exists_valid(self, mock_exists):
        """Test validate_path_exists with existing path"""
        mock_exists.return_value = True
        self.assertTrue(validate_path_exists('/existing/path'))
    
    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_validate_path_exists_not_dir(self, mock_isdir, mock_exists):
        """Test validate_path_exists with existing file when dir expected"""
        mock_exists.return_value = True
        mock_isdir.return_value = False
        with self.assertRaises(ValidationError):
            validate_path_exists('/existing/file', is_dir=True)
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_validate_path_exists_create(self, mock_makedirs, mock_exists):
        """Test validate_path_exists with non-existing path and create=True"""
        mock_exists.return_value = False
        self.assertTrue(validate_path_exists('/nonexistent/path', create=True))
        mock_makedirs.assert_called_once_with('/nonexistent/path', exist_ok=True)
    
    @patch('os.path.exists')
    def test_validate_path_exists_nonexistent(self, mock_exists):
        """Test validate_path_exists with non-existing path and create=False"""
        mock_exists.return_value = False
        with self.assertRaises(ValidationError):
            validate_path_exists('/nonexistent/path', create=False)


if __name__ == '__main__':
    unittest.main()
