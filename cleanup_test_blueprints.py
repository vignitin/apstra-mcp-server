"""
Script to clean up test blueprints from the Apstra server
"""
from apstra_core import get_bp, delete_blueprint
import time

def cleanup_test_blueprints():
    """Remove all test blueprints from the server"""
    print("=" * 60)
    print("CLEANING UP TEST BLUEPRINTS")
    print("=" * 60)
    
    server = "10.87.2.74"
    
    # Get all blueprints
    print("1. Getting current blueprints...")
    try:
        blueprints = get_bp(server)
        print(f"   ✓ Found {len(blueprints)} total blueprints")
    except Exception as e:
        print(f"   ✗ Failed to get blueprints: {e}")
        return
    
    # Identify test blueprints (containing test keywords)
    test_keywords = ['test-', 'demo-', 'e2e-test']
    test_blueprints = []
    
    for bp in blueprints:
        bp_name = bp.get('label', '').lower()
        if any(keyword in bp_name for keyword in test_keywords):
            test_blueprints.append(bp)
    
    print(f"\n2. Found {len(test_blueprints)} test blueprints to clean up:")
    for bp in test_blueprints:
        print(f"   - {bp.get('label', 'Unknown')} ({bp.get('id', 'No ID')})")
    
    if not test_blueprints:
        print("   ✓ No test blueprints found to clean up!")
        return
    
    # Confirm cleanup
    print(f"\n3. Proceeding to delete {len(test_blueprints)} test blueprints...")
    
    deleted_count = 0
    failed_count = 0
    
    for bp in test_blueprints:
        bp_id = bp.get('id')
        bp_name = bp.get('label', 'Unknown')
        
        if not bp_id:
            print(f"   ⚠ Skipping {bp_name} - no ID found")
            failed_count += 1
            continue
            
        try:
            result = delete_blueprint(bp_id, server)
            print(f"   ✓ Deleted: {bp_name} ({bp_id})")
            deleted_count += 1
            time.sleep(1)  # Small delay between deletions
        except Exception as e:
            print(f"   ✗ Failed to delete {bp_name}: {e}")
            failed_count += 1
    
    # Final verification
    print(f"\n4. Verifying cleanup...")
    try:
        final_blueprints = get_bp(server)
        remaining_test_bps = []
        
        for bp in final_blueprints:
            bp_name = bp.get('label', '').lower()
            if any(keyword in bp_name for keyword in test_keywords):
                remaining_test_bps.append(bp.get('label', 'Unknown'))
        
        if not remaining_test_bps:
            print("   ✓ All test blueprints successfully removed!")
        else:
            print(f"   ⚠ {len(remaining_test_bps)} test blueprints still remain:")
            for bp_name in remaining_test_bps:
                print(f"     - {bp_name}")
        
        print(f"   ✓ Current total blueprint count: {len(final_blueprints)}")
        
    except Exception as e:
        print(f"   ✗ Failed final verification: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("CLEANUP SUMMARY")
    print("=" * 60)
    print(f"✓ Successfully deleted: {deleted_count} blueprints")
    print(f"✗ Failed to delete: {failed_count} blueprints")
    print(f"Total processed: {len(test_blueprints)} test blueprints")
    print("=" * 60)
    
    if deleted_count > 0:
        print("🧹 Test blueprint cleanup completed!")
    else:
        print("ℹ️ No test blueprints were deleted")

if __name__ == "__main__":
    cleanup_test_blueprints()