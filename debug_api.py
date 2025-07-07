"""
Debug script to check the actual API requirements for blueprint creation
"""
from apstra_core import auth, get_templates
import json

def main():
    # Get templates to understand the structure
    templates = get_templates()
    print("Templates response:")
    print(json.dumps(templates, indent=2))
    
    # Check existing blueprints to understand structure
    from apstra_core import get_bp
    blueprints = get_bp()
    print("\nExisting blueprints:")
    print(json.dumps(blueprints, indent=2))

if __name__ == "__main__":
    main()