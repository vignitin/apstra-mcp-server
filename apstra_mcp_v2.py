from fastmcp import FastMCP
import httpx, sys

# Create an MCP server
mcp = FastMCP("Apstra MCP server")

# IP of Cloudlabs AOS Server
aos_server = 'Apstra server IP/Name'
username = 'Apstra username'
password = 'Apstra password'

# The authentication function
def auth():
    try:
        url_login = 'https://' + aos_server + '/api/user/login'
        headers_init = { 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        data = f'{{"username": "{username}","password":"{password}"}}'
        response = httpx.post(url_login, data=data, headers=headers_init, verify=False)
        if response.status_code != 201:
            sys.exit('error: authentication failed')
        auth_token = response.json()['token']
        headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        return(headers)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get blueprints
@mcp.tool()
def get_bp() -> str:
    """Gets blueprint information"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json()['items'])
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get racks
@mcp.tool()
def get_racks(blueprint_id) -> str:
    """Gets rack information for a blueprint"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints/' + blueprint_id + '/racks'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json()['items'])
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Get routing zones
@mcp.tool()
def get_rz(blueprint_id) -> str:
    """Gets routing zone information for a blueprint"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints/' + blueprint_id + '/security-zones'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)


# Create virtual networks
@mcp.tool()
def create_vn(blueprint_id, security_zone_id, vn_name) -> str:
    """Creates a virtual network in a given blueprint and routing zone"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints/' + blueprint_id + '/virtual-networks'
        data = f'{{"label": "{vn_name}","vn_type":"vxlan","security_zone_id":"{security_zone_id}"}}'
        # print(data)
        response = httpx.post(url, data=data, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Check staging version through diff-status
@mcp.tool()
def get_diff_status(blueprint_id) -> str:
    """Gets the diff status for a blueprint"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints/' + blueprint_id + '/diff-status'
        response = httpx.get(url, headers=headers, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

# Deploy config
@mcp.tool()
def deploy(blueprint_id: str, description: str, staging_version:int) -> str:
    """Deploys the config for a blueprint"""
    try:
        headers = auth()
        url = 'https://' + aos_server + '/api/blueprints/' + blueprint_id + '/deploy'
        data = f'{{"version": {staging_version},"description":"{description}"}}'
        print(url)
        print(data)
        response = httpx.put(url, headers=headers, data=data, verify=False)
        return(response.json())
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

