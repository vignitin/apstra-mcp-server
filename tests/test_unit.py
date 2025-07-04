"""
Unit tests for Apstra MCP Server blueprint creation functions
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apstra_core import (
    auth, get_templates, create_datacenter_blueprint, 
    create_freeform_blueprint, delete_blueprint, get_bp
)
from tests.test_config import TEST_SERVER, TEST_USERNAME, TEST_PASSWORD


class TestApstraMCPUnit(unittest.TestCase):
    """Unit tests for Apstra MCP Server functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_server = TEST_SERVER
        self.test_username = TEST_USERNAME
        self.test_password = TEST_PASSWORD
        
    @patch('apstra_core.httpx.post')
    def test_auth_success(self, mock_post):
        """Test successful authentication"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'token': 'test-token-123'}
        mock_post.return_value = mock_response
        
        # Test authentication
        headers, server = auth(self.test_server, self.test_username, self.test_password)
        
        # Assertions
        self.assertEqual(server, self.test_server)
        self.assertEqual(headers['AuthToken'], 'test-token-123')
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['Cache-Control'], 'no-cache')
        
    @patch('apstra_core.httpx.post')
    def test_auth_failure(self, mock_post):
        """Test authentication failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        # Test authentication failure
        with self.assertRaises(SystemExit):
            auth(self.test_server, self.test_username, "wrong-password")
            
    @patch('apstra_core.auth')
    @patch('apstra_core.httpx.get')
    def test_get_templates_success(self, mock_get, mock_auth):
        """Test successful template retrieval"""
        # Mock auth and response
        mock_auth.return_value = ({'AuthToken': 'test-token'}, self.test_server)
        mock_response = Mock()
        mock_response.json.return_value = {'items': [{'id': 'template1', 'name': 'Template 1'}]}
        mock_get.return_value = mock_response
        
        # Test get_templates
        result = get_templates(self.test_server)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        mock_get.assert_called_once()
        
    @patch('apstra_core.auth')
    @patch('apstra_core.httpx.post')
    def test_create_datacenter_blueprint_success(self, mock_post, mock_auth):
        """Test successful datacenter blueprint creation"""
        # Mock auth and response
        mock_auth.return_value = ({'AuthToken': 'test-token'}, self.test_server)
        mock_response = Mock()
        mock_response.json.return_value = {'id': 'bp-123', 'label': 'test-blueprint'}
        mock_post.return_value = mock_response
        
        # Test create_datacenter_blueprint
        result = create_datacenter_blueprint('test-blueprint', 'template-123', self.test_server)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], 'bp-123')
        self.assertEqual(result['label'], 'test-blueprint')
        mock_post.assert_called_once()
        
    @patch('apstra_core.auth')
    @patch('apstra_core.httpx.post')
    def test_create_freeform_blueprint_success(self, mock_post, mock_auth):
        """Test successful freeform blueprint creation"""
        # Mock auth and response
        mock_auth.return_value = ({'AuthToken': 'test-token'}, self.test_server)
        mock_response = Mock()
        mock_response.json.return_value = {'id': 'bp-456', 'label': 'test-freeform-blueprint'}
        mock_post.return_value = mock_response
        
        # Test create_freeform_blueprint
        result = create_freeform_blueprint('test-freeform-blueprint', self.test_server)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], 'bp-456')
        self.assertEqual(result['label'], 'test-freeform-blueprint')
        mock_post.assert_called_once()
        
    @patch('apstra_core.auth')
    @patch('apstra_core.httpx.delete')
    def test_delete_blueprint_success(self, mock_delete, mock_auth):
        """Test successful blueprint deletion"""
        # Mock auth and response
        mock_auth.return_value = ({'AuthToken': 'test-token'}, self.test_server)
        mock_response = Mock()
        mock_response.text = ""
        mock_delete.return_value = mock_response
        
        # Test delete_blueprint
        result = delete_blueprint('bp-123', self.test_server)
        
        # Assertions
        self.assertEqual(result, "Blueprint deleted successfully")
        mock_delete.assert_called_once()
        
    @patch('apstra_core.auth')
    @patch('apstra_core.httpx.get')
    def test_get_bp_success(self, mock_get, mock_auth):
        """Test successful blueprint listing"""
        # Mock auth and response
        mock_auth.return_value = ({'AuthToken': 'test-token'}, self.test_server)
        mock_response = Mock()
        mock_response.json.return_value = {'items': [{'id': 'bp-1', 'label': 'Blueprint 1'}]}
        mock_get.return_value = mock_response
        
        # Test get_bp
        result = get_bp(self.test_server)
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 'bp-1')
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()