"""
Standalone test cleanup utility for Apstra MCP Server tests
"""
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apstra_core import get_bp, delete_blueprint
from tests.test_config import TEST_SERVER
import time

def cleanup_all_test_blueprints(server_url=None):
    """
    Clean up all test blueprints from the server
    
    Args:
        server_url: Optional server URL, defaults to TEST_SERVER
    """
    server = server_url or TEST_SERVER
    
    print("=" * 50)
    print("TEST BLUEPRINT CLEANUP UTILITY")
    print("=" * 50)
    print(f"Server: {server}")
    
    try:
        # Get all blueprints
        print("\n1. Scanning for test blueprints...")
        blueprints = get_bp(server)
        
        # Identify test blueprints
        test_keywords = ['test-', 'demo-', 'e2e-test', 'unittest-', 'functional-']
        test_blueprints = []
        
        for bp in blueprints:
            bp_name = bp.get('label', '').lower()
            if any(keyword in bp_name for keyword in test_keywords):
                test_blueprints.append(bp)
        
        print(f"   Found {len(test_blueprints)} test blueprints out of {len(blueprints)} total")
        
        if not test_blueprints:
            print("   ✓ No test blueprints found - server is clean!")
            return True
            
        # List test blueprints
        print("\n2. Test blueprints to be deleted:")
        for i, bp in enumerate(test_blueprints, 1):
            print(f"   {i}. {bp.get('label', 'Unknown')} ({bp.get('id', 'No ID')})")
        
        # Delete test blueprints
        print(f"\n3. Deleting {len(test_blueprints)} test blueprints...")
        deleted_count = 0
        failed_count = 0
        
        for bp in test_blueprints:
            bp_id = bp.get('id')
            bp_name = bp.get('label', 'Unknown')
            
            if not bp_id:
                print(f"   ⚠ Skipping {bp_name} - no ID")
                failed_count += 1
                continue
            
            try:
                result = delete_blueprint(bp_id, server)
                print(f"   ✓ Deleted: {bp_name}")
                deleted_count += 1
                time.sleep(0.5)  # Small delay between deletions
            except Exception as e:
                print(f"   ✗ Failed: {bp_name} - {e}")
                failed_count += 1
        
        # Verification
        print(f"\n4. Verification...")
        final_blueprints = get_bp(server)
        
        # Check for remaining test blueprints
        remaining_test = []
        for bp in final_blueprints:
            bp_name = bp.get('label', '').lower()
            if any(keyword in bp_name for keyword in test_keywords):
                remaining_test.append(bp.get('label', 'Unknown'))
        
        if not remaining_test:
            print("   ✓ All test blueprints successfully removed!")
            success = True
        else:
            print(f"   ⚠ {len(remaining_test)} test blueprints still exist:")
            for bp_name in remaining_test:
                print(f"     - {bp_name}")
            success = False
        
        print(f"   Current total blueprints: {len(final_blueprints)}")
        
        # Summary
        print("\n" + "=" * 50)
        print("CLEANUP SUMMARY")
        print("=" * 50)
        print(f"✓ Successfully deleted: {deleted_count}")
        print(f"✗ Failed to delete: {failed_count}")
        print(f"⚠ Still remaining: {len(remaining_test)}")
        print("=" * 50)
        
        return success and failed_count == 0
        
    except Exception as e:
        print(f"\n✗ Cleanup failed: {e}")
        return False

def force_cleanup_by_pattern(pattern, server_url=None):
    """
    Force cleanup blueprints matching a specific pattern
    
    Args:
        pattern: String pattern to match in blueprint names
        server_url: Optional server URL
    """
    server = server_url or TEST_SERVER
    
    print(f"\nForce cleanup for pattern: '{pattern}'")
    
    try:
        blueprints = get_bp(server)
        matching_blueprints = [bp for bp in blueprints if pattern.lower() in bp.get('label', '').lower()]
        
        if not matching_blueprints:
            print(f"   No blueprints matching '{pattern}' found")
            return True
            
        print(f"   Found {len(matching_blueprints)} blueprints matching '{pattern}':")
        
        for bp in matching_blueprints:
            bp_id = bp.get('id')
            bp_name = bp.get('label', 'Unknown')
            
            try:
                result = delete_blueprint(bp_id, server)
                print(f"   ✓ Deleted: {bp_name} ({bp_id})")
            except Exception as e:
                print(f"   ✗ Failed: {bp_name} - {e}")
                
        return True
        
    except Exception as e:
        print(f"   ✗ Force cleanup failed: {e}")
        return False

def main():
    """Main cleanup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up test blueprints from Apstra server')
    parser.add_argument('--server', default=TEST_SERVER, help='Server URL')
    parser.add_argument('--pattern', help='Specific pattern to clean up')
    parser.add_argument('--force', action='store_true', help='Force cleanup without confirmation')
    
    args = parser.parse_args()
    
    if args.pattern:
        success = force_cleanup_by_pattern(args.pattern, args.server)
    else:
        success = cleanup_all_test_blueprints(args.server)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())