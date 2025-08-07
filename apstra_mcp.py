from fastmcp import FastMCP
import apstra_core
import argparse
import sys
import asyncio
import signal
import os
import json
import time
from typing import Optional
from session_manager import session_manager


# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Apstra MCP Server')
    parser.add_argument('-f', '--config-file', default='apstra_config.json',
                      help='Path to Apstra configuration JSON file (default: apstra_config.json)')
    parser.add_argument('-t', '--transport', default='stdio', choices=['stdio', 'sse'],
                      help='Transport mode: stdio for local/Claude Desktop, sse for remote HTTP clients (default: stdio)')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                      help='Host to bind to for HTTP transport (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', type=int, default=8080,
                      help='Port to bind to for HTTP transport (default: 8080)')
    return parser.parse_args()

# Global variables for server state
args = None
authentication_enabled = False

def get_user_credentials_from_request() -> Optional[dict]:
    """Extract user credentials from current request context"""
    # For stdio transport, check environment variables for per-user RBAC
    if args and args.transport == 'stdio':
        env_creds = {
            'apstra_username': os.getenv('APSTRA_USERNAME'),
            'apstra_password': os.getenv('APSTRA_PASSWORD'), 
            'apstra_server': os.getenv('APSTRA_SERVER'),
            'apstra_port': os.getenv('APSTRA_PORT', '443')
        }
        # Only return env credentials if all required fields are present
        if env_creds['apstra_username'] and env_creds['apstra_password'] and env_creds['apstra_server']:
            print(f"DEBUG: Using environment credentials for {env_creds['apstra_username']}", file=sys.stderr)
            return env_creds
        else:
            print("DEBUG: No environment credentials found, using global config", file=sys.stderr)
    
    # For SSE transport, use session tokens
    elif args and args.transport == 'sse':
        session_token = getattr(mcp, '_current_session_token', None)
        if session_token:
            return session_manager.validate_session(session_token)
    
    # Fallback to None (will use global config credentials)
    return None

# Initialize configuration
try:
    print("DEBUG: Starting server initialization...", file=sys.stderr)
    args = parse_args()
    print(f"DEBUG: Parsed args: {args}", file=sys.stderr)
    print(f"DEBUG: Transport mode: {args.transport}", file=sys.stderr)
    
    # Check authentication requirements
    if args.transport != 'stdio':
        tokens = load_user_tokens()
        authentication_enabled = bool(tokens)
        if authentication_enabled:
            print("DEBUG: Authentication enabled for HTTP transport", file=sys.stderr)
        else:
            print("DEBUG: WARNING - No authentication tokens found. HTTP transport will be unprotected!", file=sys.stderr)
    
    print(f"DEBUG: Initializing config from: {args.config_file}", file=sys.stderr)
    apstra_core.initialize_config(args.config_file)
    print("DEBUG: Config initialized successfully", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Error during initialization: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise

# Create an MCP server
try:
    print("DEBUG: Creating FastMCP server...", file=sys.stderr)
    mcp = FastMCP("Apstra MCP server")
    print("DEBUG: FastMCP server created successfully", file=sys.stderr)
except Exception as e:
    print(f"DEBUG: Error creating FastMCP server: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    raise

# HEALTH CHECK ENDPOINT

@mcp.tool()
def health() -> str:
    """
    Health check endpoint for monitoring and load balancers
    
    Returns:
        JSON response with server status
    """
    try:
        active_sessions = len(session_manager.sessions)
        return json.dumps({
            "status": "healthy",
            "service": "Apstra MCP Server",
            "transport": args.transport if args else "unknown",
            "active_sessions": active_sessions,
            "timestamp": time.time()
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": time.time()
        }, indent=2)

# AUTHENTICATION ENDPOINTS - For session management

@mcp.tool()
def login(apstra_username: str, apstra_password: str, apstra_server: str, apstra_port: str = "443") -> str:
    """
    Authenticate with Apstra server and create session (SSE transport only)
    
    Args:
        apstra_username: Apstra username
        apstra_password: Apstra password
        apstra_server: Apstra server hostname or IP
        apstra_port: Apstra server port (default: 443)
        
    Returns:
        JSON response with session token or error
        
    Note:
        For stdio transport (Claude Desktop), use environment variables instead:
        APSTRA_USERNAME, APSTRA_PASSWORD, APSTRA_SERVER, APSTRA_PORT
    """
    try:
        # Check transport mode
        if args and args.transport == 'stdio':
            return json.dumps({
                "status": "info",
                "message": "Login not needed for stdio transport. Use environment variables for RBAC:",
                "instructions": {
                    "APSTRA_USERNAME": "your-username@company.com",
                    "APSTRA_PASSWORD": "your-password", 
                    "APSTRA_SERVER": "your-apstra-server.com",
                    "APSTRA_PORT": "443"
                },
                "note": "Set these in your Claude Desktop MCP server configuration"
            }, indent=2)
        
        # SSE transport - proceed with session creation
        success, message, session_token = session_manager.authenticate_user(
            apstra_username, apstra_password, apstra_server, apstra_port
        )
        
        if success:
            return json.dumps({
                "status": "success",
                "message": message,
                "session_token": session_token,
                "expires_in": 3600  # 1 hour
            }, indent=2)
        else:
            return json.dumps({
                "status": "error", 
                "message": message
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Login failed: {str(e)}"
        }, indent=2)

@mcp.tool()
def logout(session_token: str) -> str:
    """
    Logout and invalidate session (SSE transport only)
    
    Args:
        session_token: Session token to invalidate
        
    Returns:
        JSON response with logout status
        
    Note:
        For stdio transport (Claude Desktop), sessions are not used.
        Authentication is handled via environment variables.
    """
    try:
        # Check transport mode
        if args and args.transport == 'stdio':
            return json.dumps({
                "status": "info",
                "message": "Logout not applicable for stdio transport.",
                "note": "Authentication is handled via environment variables. No sessions to logout."
            }, indent=2)
        
        # SSE transport - proceed with logout
        success = session_manager.logout_session(session_token)
        
        if success:
            return json.dumps({
                "status": "success",
                "message": "Session logged out successfully"
            }, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "Invalid session token"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Logout failed: {str(e)}"
        }, indent=2)

@mcp.tool()
def session_info(session_token: str = None) -> str:
    """
    Get information about current session or transport mode
    
    Args:
        session_token: Session token to check (SSE transport only)
        
    Returns:
        JSON response with session/transport information
    """
    try:
        # Check transport mode
        if args and args.transport == 'stdio':
            # Show environment-based auth info
            env_creds = get_user_credentials_from_request()
            if env_creds:
                return json.dumps({
                    "status": "success",
                    "transport": "stdio",
                    "auth_mode": "environment_variables",
                    "apstra_username": env_creds.get('apstra_username'),
                    "apstra_server": env_creds.get('apstra_server'),
                    "apstra_port": env_creds.get('apstra_port')
                }, indent=2)
            else:
                return json.dumps({
                    "status": "info",
                    "transport": "stdio", 
                    "auth_mode": "global_config",
                    "message": "Using global configuration credentials. Set APSTRA_USERNAME, APSTRA_PASSWORD, APSTRA_SERVER environment variables for RBAC."
                }, indent=2)
        
        # SSE transport - check session
        if not session_token:
            return json.dumps({
                "status": "error",
                "message": "session_token parameter required for SSE transport"
            }, indent=2)
            
        info = session_manager.get_session_info(session_token)
        
        if info:
            return json.dumps({
                "status": "success",
                "transport": "sse",
                "auth_mode": "session_based",
                "session_info": info
            }, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "Invalid or expired session token"
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Session info failed: {str(e)}"
        }, indent=2)

# QUERY TOOLS - All query operations grouped together

# Get blueprints
@mcp.tool()
def get_bp(server_url: str = None) -> str:
    """Gets blueprint information"""
    user_credentials = get_user_credentials_from_request()
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_bp(server_url, user_credentials=user_credentials)
    return f"{formatting}\n\n--- BLUEPRINT DATA ---\n{data}"

# # Get nodes
# @mcp.tool()
# def get_nodes(blueprint_id: str, server_url: str = None) -> str:
#     """Gets node information for a blueprint"""
#     return apstra_core.get_nodes(blueprint_id, server_url)

# # Get node by ID
# @mcp.tool()
# def get_node_id(blueprint_id: str, node_id: str, server_url: str = None) -> str:
#     """Gets specific node information by ID for a blueprint"""
#     return apstra_core.get_node_id(blueprint_id, node_id, server_url)

# Get racks
@mcp.tool()
def get_racks(blueprint_id: str, server_url: str = None) -> str:
    """Gets rack information for a blueprint"""
    user_credentials = get_user_credentials_from_request()
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_racks(blueprint_id, server_url, user_credentials=user_credentials)
    return f"{formatting}\n\n--- RACK DATA ---\n{data}"

# Get routing zones
@mcp.tool()
def get_rz(blueprint_id: str, server_url: str = None) -> str:
    """Gets routing zone information for a blueprint"""
    user_credentials = get_user_credentials_from_request()
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_rz(blueprint_id, server_url, user_credentials=user_credentials)
    return f"{formatting}\n\n--- ROUTING ZONE DATA ---\n{data}"

# Get virtual networks
@mcp.tool()
def get_vn(blueprint_id: str, server_url: str = None) -> str:
    """Gets virtual network information for a blueprint"""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_vn(blueprint_id, server_url)
    return f"{formatting}\n\n--- VIRTUAL NETWORK DATA ---\n{data}"

# Get system info
@mcp.tool()
def get_system_info(blueprint_id: str, server_url: str = None) -> str:
    """Gets information about the systems in the blueprint"""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_system_info(blueprint_id, server_url)
    return f"{formatting}\n\n--- SYSTEM DATA ---\n{data}"

# # Get system info
# @mcp.tool()
# def get_systems(server_url: str = None) -> str:
#     """Return a list of all devices in Apstra and their key facts"""
#     return apstra_core.get_systems(server_url)

# Check staging version through diff-status
@mcp.tool()
def get_diff_status(blueprint_id: str, server_url: str = None) -> str:
    """Gets the diff status for a blueprint"""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_diff_status(blueprint_id, server_url)
    return f"{formatting}\n\n--- DIFF STATUS DATA ---\n{data}"

# Get templates
@mcp.tool()
def get_templates(server_url: str = None) -> str:
    """Gets available templates for blueprint creation"""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_templates(server_url)
    return f"{formatting}\n\n--- TEMPLATE DATA ---\n{data}"

# Get anomalies
@mcp.tool()
def get_anomalies(blueprint_id: str, server_url: str = None) -> str:
    """Gets anomalies information for a blueprint"""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_anomalies(blueprint_id, server_url)
    return f"{formatting}\n\n--- ANOMALY DATA ---\n{data}"

# Get remote gateways
@mcp.tool()
def get_remote_gw(blueprint_id: str, server_url: str = None) -> str:
    """Gets a list of all remote gateways within a blueprint, keyed by remote gateway node ID."""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_remote_gw(blueprint_id, server_url)
    return f"{formatting}\n\n--- REMOTE GATEWAY DATA ---\n{data}"

# Get protocol sessions
@mcp.tool()
def get_protocol_sessions(blueprint_id: str, server_url: str = None) -> str:
    """Return a list of all protocol sessions from the specified blueprint."""
    formatting = apstra_core.get_formatting_guidelines()
    data = apstra_core.get_protocol_sessions(blueprint_id, server_url)
    return f"{formatting}\n\n--- PROTOCOL SESSION DATA ---\n{data}"

# MANAGEMENT TOOLS - Deploy and delete operations

# Deploy config
@mcp.tool()
def deploy(blueprint_id: str, description: str, staging_version: int, server_url: str = None) -> str:
    """Deploys the config for a blueprint. Always use the staging version from the diff-status tool.
    Args:
        blueprint_id (str): The ID of the blueprint to deploy.
        description (str): Description for the deployment.
        staging_version (int): The staging version to deploy.
        server_url (str, optional): The URL of the Apstra server. Defaults to None.
    """
    return apstra_core.deploy(blueprint_id, description, staging_version, server_url)

# Delete blueprint
@mcp.tool()
def delete_blueprint(blueprint_id: str, server_url: str = None) -> str:
    """Deletes a blueprint by ID"""
    return apstra_core.delete_blueprint(blueprint_id, server_url)

# CREATE TOOLS - All create operations grouped together

# Create virtual networks
@mcp.tool()
def create_vn(blueprint_id: str, security_zone_id: str, vn_name: str, server_url: str = None) -> str:
    """Creates a virtual network in a given blueprint and routing zone"""
    return apstra_core.create_vn(blueprint_id, security_zone_id, vn_name, server_url)

# Create remote gateways
@mcp.tool()
def create_remote_gw(blueprint_id: str, gw_ip: str, gw_asn: int, gw_name: str, local_gw_nodes: list, evpn_route_types: str = "all", password: str = None, keepalive_timer: int = 10, evpn_interconnect_group_id: str = None, holdtime_timer: int = 30, ttl: int = 30, server_url: str = None) -> str:
    """Creates remote gateways in a given blueprint to interconnect Datacenters. Request body schema:
            {
            "gw_ip": "string (required, prefer loopback addresses)",
            "local_gw_nodes": ["array of strings (required, unique, min 1, use this effectively to specify multiple local gateway nodes)"],
            "password": "string (optional)",
            "evpn_interconnect_group_id": "string (optional)",
            "gw_name": "string (required)",
            "gw_asn": "integer (required, 1-4294967295, get this imformatiom from the router configuration)",
            "ttl": "integer (optional, 2-255, default 30)",
            "keepalive_timer": "integer (optional, 1-65535, default 10)",
            "holdtime_timer": "integer (optional, 3-65535, default 30)",
            "evpn_route_types": "string (optional, enum: all, type5_only, default all)"
            }
    """
    return apstra_core.create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, evpn_route_types, password, keepalive_timer, evpn_interconnect_group_id, holdtime_timer, ttl, server_url)

# Create datacenter blueprint
@mcp.tool()
def create_datacenter_blueprint(blueprint_name: str, template_id: str, server_url: str = None) -> str:
    """Creates a new datacenter blueprint with the specified name and template"""
    return apstra_core.create_datacenter_blueprint(blueprint_name, template_id, server_url)

# Create freeform blueprint
@mcp.tool()
def create_freeform_blueprint(blueprint_name: str, server_url: str = None) -> str:
    """Creates a new freeform blueprint with the specified name"""
    return apstra_core.create_freeform_blueprint(blueprint_name, server_url)

print("DEBUG: All tools registered successfully", file=sys.stderr)
print("DEBUG: Server setup complete, waiting for connections...", file=sys.stderr)

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...", file=sys.stderr)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main function to run the MCP server"""
    print("DEBUG: Starting main() function...", file=sys.stderr)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    try:
        if args.transport == 'stdio':
            print("DEBUG: Starting stdio transport (for Claude Desktop)...", file=sys.stderr)
            mcp.run(transport="stdio")
            
        elif args.transport == 'sse':
            print(f"DEBUG: Starting SSE transport on {args.host}:{args.port}...", file=sys.stderr)
            print("DEBUG: Session-based authentication enabled for HTTP transport", file=sys.stderr)
            
            # Add session authentication middleware
            @mcp.middleware  
            async def session_auth_middleware(request, call_next):
                # Skip auth for login endpoint
                if hasattr(request, 'method') and request.method == 'POST':
                    request_data = getattr(request, 'json', {})
                    if isinstance(request_data, dict) and request_data.get('method') == 'tools/call':
                        tool_name = request_data.get('params', {}).get('name', '')
                        if tool_name == 'login':
                            return await call_next(request)
                
                # Check for session token in Authorization header
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return {
                        'error': 'Authentication required. Please login first to get a session token.',
                        'code': 401
                    }
                
                session_token = auth_header[7:]  # Remove 'Bearer ' prefix
                user_creds = session_manager.validate_session(session_token)
                if not user_creds:
                    return {
                        'error': 'Invalid or expired session token. Please login again.',
                        'code': 401
                    }
                
                # Store session token in request context for tools to use
                setattr(mcp, '_current_session_token', session_token)
                
                return await call_next(request)
            
            # Clean up expired sessions periodically
            session_manager.cleanup_expired_sessions()
            
            # Run HTTP/SSE server
            mcp.run(transport="sse", host=args.host, port=args.port)
            
        else:
            raise ValueError(f"Unsupported transport: {args.transport}")
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user", file=sys.stderr)
    except Exception as e:
        print(f"DEBUG: Error in main(): {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise

if __name__ == "__main__":
    main()

