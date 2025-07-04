"""
Functional tests for Apstra MCP Server end-to-end blueprint creation
"""
import unittest
import sys
import os
import time
import json

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apstra_core import (
    auth, get_templates, create_datacenter_blueprint, 
    create_freeform_blueprint, delete_blueprint, get_bp
)
from tests.test_config import (
    TEST_SERVER, TEST_USERNAME, TEST_PASSWORD,
    TEST_DATACENTER_BLUEPRINT, TEST_FREEFORM_BLUEPRINT
)


class TestApstraMCPFunctional(unittest.TestCase):
    """Functional tests for Apstra MCP Server against real server"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures for the entire test class"""
        cls.test_server = TEST_SERVER
        cls.test_username = TEST_USERNAME
        cls.test_password = TEST_PASSWORD
        cls.created_blueprints = []
        
        # Test authentication first
        try:
            headers, server = auth(cls.test_server, cls.test_username, cls.test_password)
            cls.auth_working = True
            print(f"✓ Authentication successful to {server}")
        except Exception as e:
            cls.auth_working = False
            print(f"✗ Authentication failed: {e}")
            
    @classmethod
    def tearDownClass(cls):
        """Clean up created blueprints after all tests"""
        if cls.auth_working:
            # Clean up tracked blueprints
            if cls.created_blueprints:
                print(f"\nCleaning up {len(cls.created_blueprints)} tracked blueprints...")
                for bp_id in cls.created_blueprints:
                    try:
                        result = delete_blueprint(bp_id, cls.test_server)
                        print(f"✓ Deleted tracked blueprint {bp_id}")
                    except Exception as e:
                        print(f"✗ Failed to delete tracked blueprint {bp_id}: {e}")
            
            # Additional cleanup: remove any remaining test blueprints
            try:
                print("\nPerforming additional cleanup scan...")
                all_blueprints = get_bp(cls.test_server)
                test_keywords = ['test-', 'demo-', 'e2e-test']
                
                remaining_test_bps = []
                for bp in all_blueprints:
                    bp_name = bp.get('label', '').lower()
                    if any(keyword in bp_name for keyword in test_keywords):
                        remaining_test_bps.append(bp)
                
                if remaining_test_bps:
                    print(f"Found {len(remaining_test_bps)} additional test blueprints to clean up...")
                    for bp in remaining_test_bps:
                        try:
                            result = delete_blueprint(bp['id'], cls.test_server)
                            print(f"✓ Deleted additional test blueprint {bp.get('label', 'Unknown')} ({bp['id']})")
                        except Exception as e:
                            print(f"✗ Failed to delete {bp.get('label', 'Unknown')}: {e}")
                else:
                    print("✓ No additional test blueprints found")
                    
            except Exception as e:
                print(f"✗ Additional cleanup scan failed: {e}")
                    
    def setUp(self):
        """Set up for each test"""
        if not self.auth_working:
            self.skipTest("Authentication failed - skipping functional tests")
        self.test_blueprints_created = []
            
    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'test_blueprints_created') and self.test_blueprints_created:
            for bp_id in self.test_blueprints_created:
                try:
                    delete_blueprint(bp_id, self.test_server)
                    print(f"  → Cleaned up test blueprint {bp_id}")
                except Exception as e:
                    print(f"  → Failed to clean up blueprint {bp_id}: {e}")
            
    def test_01_authentication(self):
        """Test authentication against real server"""
        try:
            headers, server = auth(self.test_server, self.test_username, self.test_password)
            self.assertEqual(server, self.test_server)
            self.assertIn('AuthToken', headers)
            self.assertIn('Content-Type', headers)
            print("✓ Authentication test passed")
        except Exception as e:
            self.fail(f"Authentication failed: {e}")
            
    def test_02_get_existing_blueprints(self):
        """Test getting existing blueprints"""
        try:
            blueprints = get_bp(self.test_server)
            self.assertIsInstance(blueprints, list)
            print(f"✓ Retrieved {len(blueprints)} existing blueprints")
            for bp in blueprints:
                print(f"  - {bp.get('label', 'Unknown')} ({bp.get('id', 'No ID')})")
        except Exception as e:
            self.fail(f"Failed to get blueprints: {e}")
            
    def test_03_get_templates(self):
        """Test getting available templates"""
        try:
            templates = get_templates(self.test_server)
            self.assertIsInstance(templates, dict)
            
            if 'items' in templates:
                template_items = templates['items']
                self.assertIsInstance(template_items, list)
                print(f"✓ Retrieved {len(template_items)} templates")
                
                # Store first template for datacenter blueprint creation
                if template_items:
                    self.first_template_id = template_items[0]['id']
                    print(f"  - Using template: {template_items[0].get('display_name', 'Unknown')} ({self.first_template_id})")
                else:
                    self.first_template_id = None
                    print("  - No templates available")
            else:
                print("  - No template items found in response")
                self.first_template_id = None
                
        except Exception as e:
            self.fail(f"Failed to get templates: {e}")
            
    def test_04_create_freeform_blueprint(self):
        """Test creating a freeform blueprint"""
        try:
            blueprint_name = f"{TEST_FREEFORM_BLUEPRINT}-{int(time.time())}"
            result = create_freeform_blueprint(blueprint_name, self.test_server)
            
            self.assertIsInstance(result, dict)
            self.assertIn('id', result)
            
            # Store blueprint ID for cleanup
            blueprint_id = result['id']
            self.__class__.created_blueprints.append(blueprint_id)
            self.test_blueprints_created.append(blueprint_id)
            
            print(f"✓ Created freeform blueprint: {blueprint_name} ({blueprint_id})")
            
            # Verify blueprint was created by checking it exists
            blueprints = get_bp(self.test_server)
            blueprint_exists = any(bp['id'] == blueprint_id for bp in blueprints)
            self.assertTrue(blueprint_exists, "Created blueprint not found in blueprint list")
            
        except Exception as e:
            self.fail(f"Failed to create freeform blueprint: {e}")
            
    def test_05_create_datacenter_blueprint(self):
        """Test creating a datacenter blueprint"""
        # First get templates to use one for blueprint creation
        try:
            templates = get_templates(self.test_server)
            if not templates.get('items'):
                self.skipTest("No templates available for datacenter blueprint creation")
                
            template_id = templates['items'][0]['id']
            blueprint_name = f"{TEST_DATACENTER_BLUEPRINT}-{int(time.time())}"
            
            result = create_datacenter_blueprint(blueprint_name, template_id, self.test_server)
            
            self.assertIsInstance(result, dict)
            self.assertIn('id', result)
            
            # Store blueprint ID for cleanup
            blueprint_id = result['id']
            self.__class__.created_blueprints.append(blueprint_id)
            self.test_blueprints_created.append(blueprint_id)
            
            print(f"✓ Created datacenter blueprint: {blueprint_name} ({blueprint_id})")
            
            # Verify blueprint was created by checking it exists
            blueprints = get_bp(self.test_server)
            blueprint_exists = any(bp['id'] == blueprint_id for bp in blueprints)
            self.assertTrue(blueprint_exists, "Created blueprint not found in blueprint list")
            
        except Exception as e:
            self.fail(f"Failed to create datacenter blueprint: {e}")
            
    def test_06_end_to_end_blueprint_lifecycle(self):
        """Test complete blueprint lifecycle: create, verify, delete"""
        try:
            # Create a freeform blueprint
            blueprint_name = f"e2e-test-{int(time.time())}"
            create_result = create_freeform_blueprint(blueprint_name, self.test_server)
            
            self.assertIsInstance(create_result, dict)
            self.assertIn('id', create_result)
            blueprint_id = create_result['id']
            
            # Track for emergency cleanup (though this test deletes its own blueprint)
            self.test_blueprints_created.append(blueprint_id)
            
            print(f"✓ Step 1: Created blueprint {blueprint_name} ({blueprint_id})")
            
            # Verify it exists in the list
            blueprints = get_bp(self.test_server)
            blueprint_exists = any(bp['id'] == blueprint_id for bp in blueprints)
            self.assertTrue(blueprint_exists, "Created blueprint not found in blueprint list")
            
            print(f"✓ Step 2: Verified blueprint exists in list")
            
            # Delete the blueprint
            delete_result = delete_blueprint(blueprint_id, self.test_server)
            self.assertIsInstance(delete_result, str)
            
            # Remove from tracking since we successfully deleted it
            if blueprint_id in self.test_blueprints_created:
                self.test_blueprints_created.remove(blueprint_id)
            
            print(f"✓ Step 3: Deleted blueprint {blueprint_id}")
            
            # Verify it's gone (wait a moment for deletion to propagate)
            time.sleep(2)
            blueprints_after = get_bp(self.test_server)
            blueprint_still_exists = any(bp['id'] == blueprint_id for bp in blueprints_after)
            self.assertFalse(blueprint_still_exists, "Blueprint still exists after deletion")
            
            print(f"✓ Step 4: Verified blueprint no longer exists")
            print(f"✓ End-to-end blueprint lifecycle test completed successfully")
            
        except Exception as e:
            self.fail(f"End-to-end test failed: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)