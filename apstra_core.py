"""
Core Apstra functions without MCP decorators for testing and reuse
"""
import httpx
import sys

# Default AOS Server configuration (can be overridden)
aos_server = "10.87.2.74"
username = "admin"
password = "Apstramarvis@123"

# The authentication function
def auth(server_url=None, user=None, passwd=None):
    server = server_url or aos_server
    auth_user = user or username
    auth_pass = passwd or password
    try:
        url_login = f'https://{server}/api/user/login'
        headers_init = { 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        data = f'{{"username": "{auth_user}","password":"{auth_pass}"}}'
        response = httpx.post(url_login, data=data, headers=headers_init, verify=False)
        if response.status_code != 201:
            sys.exit('error: authentication failed')
        auth_token = response.json()['token']
        headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        return(headers, server)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get blueprints
def get_bp(server_url=None):
    """Gets blueprint information"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json()['items'])
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get racks
def get_racks(blueprint_id, server_url=None):
    """Gets rack information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/racks'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json()['items'])
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get routing zones
def get_rz(blueprint_id, server_url=None):
    """Gets routing zone information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/security-zones'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Create virtual networks
def create_vn(blueprint_id, security_zone_id, vn_name, server_url=None):
    """Creates a virtual network in a given blueprint and routing zone"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks'
        data = f'{{"label": "{vn_name}","vn_type":"vxlan","security_zone_id":"{security_zone_id}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Check staging version through diff-status
def get_diff_status(blueprint_id, server_url=None):
    """Gets the diff status for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/diff-status'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Deploy config
def deploy(blueprint_id, description, staging_version, server_url=None):
    """Deploys the config for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/deploy'
        data = f'{{"version": {staging_version},"description":"{description}"}}'
        print(url)
        print(data)
        response = httpx.put(url, headers=headers, data=data, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get templates
def get_templates(server_url=None):
    """Gets available templates for blueprint creation"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/design/templates'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Create datacenter blueprint
def create_datacenter_blueprint(blueprint_name, template_id, server_url=None):
    """Creates a new datacenter blueprint with the specified name and template"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"two_stage_l3clos","init_type":"template_reference","template_id":"{template_id}","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Create freeform blueprint
def create_freeform_blueprint(blueprint_name, server_url=None):
    """Creates a new freeform blueprint with the specified name"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"freeform","init_type":"none","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Delete blueprint
def delete_blueprint(blueprint_id, server_url=None):
    """Deletes a blueprint by ID"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}'
        response = httpx.delete(url, headers=headers, verify=False)
        return(response.text if response.text else "Blueprint deleted successfully")
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)