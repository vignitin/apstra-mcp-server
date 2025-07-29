"""
Core Apstra functions without MCP decorators for testing and reuse
"""
import httpx
import sys
import json
import os

# Global configuration variables
aos_server = ''
aos_port = ''
username = ''
password = ''

# Load configuration from JSON file
def load_config(config_file=None):
    """
    Load Apstra configuration from JSON file.
    Args:
        config_file: Optional path to config file. Defaults to 'apstra_config.json'
    """
    if config_file is None:
        config_file = 'apstra_config.json'
    
    # If not absolute path, look in same directory as this script
    if not os.path.isabs(config_file):
        config_file = os.path.join(os.path.dirname(__file__), config_file)
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}", file=sys.stderr)
        print(f"Please create a config file based on apstra_config_sample.json", file=sys.stderr)
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in config file: {config_file}", file=sys.stderr)
        return {}

def initialize_config(config_file=None):
    """Initialize global configuration variables from specified config file"""
    global aos_server, aos_port, username, password
    config = load_config(config_file)
    aos_server = config.get('aos_server', '')
    aos_port = config.get('aos_port', '')
    username = config.get('username', '')
    password = config.get('password', '')

# Load default configuration
initialize_config()

# The authentication function
def auth(server_url=None, user=None, passwd=None):
    # Handle server URL construction
    if server_url:
        server = server_url
    else:
        # Check if aos_server already includes port (for backward compatibility)
        if ':' in aos_server:
            server = aos_server
        else:
            # Combine server and port
            if aos_port:
                server = f"{aos_server}:{aos_port}"
            else:
                # Default to port 443 if no port specified
                server = f"{aos_server}:443"
    
    auth_user = user or username
    auth_pass = passwd or password
    try:
        url_login = f'https://{server}/api/user/login'
        headers_init = { 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        data = f'{{"username": "{auth_user}","password":"{auth_pass}"}}'
        response = httpx.post(url_login, data=data, headers=headers_init, verify=False)
        if response.status_code != 201:
            raise Exception(f'Authentication failed: HTTP {response.status_code} - {response.text}')
        auth_token = response.json()['token']
        headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        return(headers, server)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        raise  # Re-raise the exception instead of returning None


# Get blueprints
def get_bp(server_url=None):
    """Gets blueprint information"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json()['items'], indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get node details
def get_nodes(blueprint_id, server_url=None):
    """Gets node information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/nodes'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json()['nodes'], indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get node ID details
def get_node_id(blueprint_id, node_id, server_url=None):
    """Gets specific node information by ID for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/nodes/{node_id}'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get racks
def get_racks(blueprint_id, server_url=None):
    """Gets rack information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/racks'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json()['items'], indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get routing zones
def get_rz(blueprint_id, server_url=None):
    """Gets routing zone information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/security-zones'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get virtual networks
def get_vn(blueprint_id, server_url=None):
    """Gets virtual networks information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg


# Check staging version through diff-status
def get_diff_status(blueprint_id, server_url=None):
    """Gets the diff status for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/diff-status'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Deploy config
def deploy(blueprint_id, description, staging_version, server_url=None):
    """Deploys the config for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/deploy'
        data = f'{{"version": {staging_version},"description":"{description}"}}'
        response = httpx.put(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get templates
def get_templates(server_url=None):
    """Gets available templates for blueprint creation"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/design/templates'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg


# Delete blueprint
def delete_blueprint(blueprint_id, server_url=None):
    """Deletes a blueprint by ID"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}'
        response = httpx.delete(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.text if response.text else "Blueprint deleted successfully"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get anomalies
def get_anomalies(blueprint_id, server_url=None):
    """Gets anomalies information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/anomalies'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get remote gateways
def get_remote_gw(blueprint_id, server_url=None):
    """Gets a list of all remote gateways within a blueprint, keyed by remote gateway node ID."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/remote_gateways'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get protocol sessions
def get_protocol_sessions(blueprint_id, server_url=None):
    """Return a list of all protocol sessions from the specified blueprint."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/protocol-sessions'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Get system info
def get_systems(server_url=None):
    """Return a list of all devices in Apstra and their key facts"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/systems'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# CREATE FUNCTIONS - All create operations grouped together

# Create virtual networks
def create_vn(blueprint_id, security_zone_id, vn_name, server_url=None):
    """Creates a virtual network in a given blueprint and routing zone"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks'
        data = f'{{"label": "{vn_name}","vn_type":"vxlan","security_zone_id":"{security_zone_id}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Create remote gateways
def create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, evpn_route_types="all", password=None, keepalive_timer=10, evpn_interconnect_group_id=None, holdtime_timer=30, ttl=30, server_url=None):
    """Creates a remote gateway in a given blueprint. Remote EVPN Gateway is a logical function that you could instantiate anywhere and on any device. 
    It requires BGP support in general, L2VPN/EVPN AFI/SAFI specifically. To establish a BGP session with an EVPN gateway, IP connectivity, 
    as well as connectivity to TCP port 179 (IANA allocates BGP TCP ports), should be available."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/remote_gateways'
        payload = {
            "gw_name": gw_name,
            "gw_ip": gw_ip,
            "gw_asn": gw_asn,
            "evpn_route_types": evpn_route_types,
            "local_gw_nodes": local_gw_nodes if isinstance(local_gw_nodes, list) else [local_gw_nodes]
        }
        
        # Add optional parameters only if they are provided
        if password is not None:
            payload["password"] = password
        if evpn_interconnect_group_id is not None:
            payload["evpn_interconnect_group_id"] = evpn_interconnect_group_id
            
        # Add optional parameters with their default values
        payload["keepalive_timer"] = keepalive_timer
        payload["holdtime_timer"] = holdtime_timer
        payload["ttl"] = ttl
        data = json.dumps(payload)
        response = httpx.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Create datacenter blueprint
def create_datacenter_blueprint(blueprint_name, template_id, server_url=None):
    """Creates a new datacenter blueprint with the specified name and template"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"two_stage_l3clos","init_type":"template_reference","template_id":"{template_id}","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

# Create freeform blueprint
def create_freeform_blueprint(blueprint_name, server_url=None):
    """Creates a new freeform blueprint with the specified name"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"freeform","init_type":"none","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        print(error_msg, file=sys.stderr)
        return error_msg

