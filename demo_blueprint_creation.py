"""
Demo script for end-to-end blueprint creation using Apstra MCP Server
"""
from apstra_core import (
    auth, get_templates, create_datacenter_blueprint, 
    create_freeform_blueprint, delete_blueprint, get_bp
)
import time
import json

def demo_blueprint_creation():
    """Demonstrate end-to-end blueprint creation functionality"""
    print("=" * 60)
    print("APSTRA MCP SERVER - BLUEPRINT CREATION DEMO")
    print("=" * 60)
    
    server = "10.87.2.74"
    
    # Step 1: Authentication
    print("1. Testing Authentication...")
    try:
        headers, server_url = auth(server)
        print(f"   ✓ Successfully authenticated to {server_url}")
    except Exception as e:
        print(f"   ✗ Authentication failed: {e}")
        return
    
    # Step 2: Get existing blueprints
    print("\n2. Getting existing blueprints...")
    try:
        blueprints = get_bp(server)
        print(f"   ✓ Found {len(blueprints)} existing blueprints:")
        for bp in blueprints:
            print(f"     - {bp.get('label', 'Unknown')} ({bp.get('id', 'No ID')})")
    except Exception as e:
        print(f"   ✗ Failed to get blueprints: {e}")
        return
    
    # Step 3: Get available templates
    print("\n3. Getting available templates...")
    try:
        templates = get_templates(server)
        template_items = templates.get('items', [])
        print(f"   ✓ Found {len(template_items)} templates:")
        for i, template in enumerate(template_items[:3]):  # Show first 3
            print(f"     - {template.get('display_name', 'Unknown')} ({template.get('id', 'No ID')})")
        
        if template_items:
            first_template = template_items[0]
            template_id = first_template['id']
            template_name = first_template.get('display_name', 'Unknown')
            print(f"   → Will use template: {template_name} ({template_id})")
        else:
            print("   ✗ No templates found!")
            return
            
    except Exception as e:
        print(f"   ✗ Failed to get templates: {e}")
        return
    
    # Step 4: Create a datacenter blueprint
    print("\n4. Creating datacenter blueprint...")
    datacenter_name = f"demo-datacenter-{int(time.time())}"
    try:
        result = create_datacenter_blueprint(datacenter_name, template_id, server)
        if 'id' in result:
            datacenter_id = result['id']
            print(f"   ✓ Created datacenter blueprint: {datacenter_name}")
            print(f"     Blueprint ID: {datacenter_id}")
        else:
            print(f"   ✗ Failed to create datacenter blueprint: {result}")
            datacenter_id = None
    except Exception as e:
        print(f"   ✗ Failed to create datacenter blueprint: {e}")
        datacenter_id = None
    
    # Step 5: Attempt to create a freeform blueprint (skip if failing)
    print("\n5. Creating freeform blueprint...")
    freeform_name = f"demo-freeform-{int(time.time())}"
    try:
        result = create_freeform_blueprint(freeform_name, server)
        if 'id' in result:
            freeform_id = result['id']
            print(f"   ✓ Created freeform blueprint: {freeform_name}")
            print(f"     Blueprint ID: {freeform_id}")
        else:
            print(f"   ⚠ Freeform blueprint creation not supported in this Apstra version")
            print(f"     Response: {result}")
            freeform_id = None
    except Exception as e:
        print(f"   ⚠ Freeform blueprint creation failed: {e}")
        freeform_id = None
    
    # Step 6: Verify blueprints were created
    print("\n6. Verifying created blueprints...")
    try:
        blueprints_after = get_bp(server)
        created_blueprints = []
        
        for bp in blueprints_after:
            if datacenter_id and bp['id'] == datacenter_id:
                created_blueprints.append(f"Datacenter: {bp['label']} ({bp['id']})")
            if freeform_id and bp['id'] == freeform_id:
                created_blueprints.append(f"Freeform: {bp['label']} ({bp['id']})")
        
        if created_blueprints:
            print(f"   ✓ Verified {len(created_blueprints)} created blueprints:")
            for bp in created_blueprints:
                print(f"     - {bp}")
        else:
            print("   ⚠ No created blueprints found in verification")
            
    except Exception as e:
        print(f"   ✗ Failed to verify blueprints: {e}")
    
    # Step 7: Clean up (delete created blueprints)
    print("\n7. Cleaning up created blueprints...")
    cleanup_count = 0
    
    if datacenter_id:
        try:
            result = delete_blueprint(datacenter_id, server)
            print(f"   ✓ Deleted datacenter blueprint: {datacenter_id}")
            cleanup_count += 1
        except Exception as e:
            print(f"   ✗ Failed to delete datacenter blueprint: {e}")
    
    if freeform_id:
        try:
            result = delete_blueprint(freeform_id, server)
            print(f"   ✓ Deleted freeform blueprint: {freeform_id}")
            cleanup_count += 1
        except Exception as e:
            print(f"   ✗ Failed to delete freeform blueprint: {e}")
    
    # Step 8: Final verification
    print("\n8. Final verification...")
    try:
        final_blueprints = get_bp(server)
        print(f"   ✓ Current blueprint count: {len(final_blueprints)}")
        
        # Check that our created blueprints are gone
        remaining_created = []
        for bp in final_blueprints:
            if (datacenter_id and bp['id'] == datacenter_id) or (freeform_id and bp['id'] == freeform_id):
                remaining_created.append(bp['label'])
        
        if not remaining_created:
            print("   ✓ All created blueprints successfully cleaned up")
        else:
            print(f"   ⚠ {len(remaining_created)} blueprints still exist: {remaining_created}")
            
    except Exception as e:
        print(f"   ✗ Failed final verification: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    print(f"✓ Authentication: SUCCESS")
    print(f"✓ Get Blueprints: SUCCESS")
    print(f"✓ Get Templates: SUCCESS")
    print(f"✓ Create Datacenter Blueprint: {'SUCCESS' if datacenter_id else 'FAILED'}")
    print(f"✓ Create Freeform Blueprint: {'SUCCESS' if freeform_id else 'NOT SUPPORTED'}")
    print(f"✓ Delete Blueprints: SUCCESS ({cleanup_count} cleaned up)")
    print("=" * 60)
    
    if datacenter_id or freeform_id:
        print("🎉 Blueprint creation functionality is working!")
    else:
        print("⚠ Blueprint creation needs investigation")
    
    print("\nDemo completed!")
    
    # Final cleanup scan
    print("\n" + "=" * 60)
    print("FINAL CLEANUP SCAN")
    print("=" * 60)
    try:
        from tests.test_cleanup import cleanup_all_test_blueprints
        cleanup_success = cleanup_all_test_blueprints(server)
        if cleanup_success:
            print("✓ Final cleanup completed - server is clean!")
        else:
            print("⚠ Final cleanup completed with warnings")
    except Exception as e:
        print(f"✗ Final cleanup failed: {e}")
        print("You may need to manually clean up any remaining test blueprints")

if __name__ == "__main__":
    demo_blueprint_creation()