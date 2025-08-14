#!/usr/bin/env python3
"""
Apstra MCP Server - Simplified Version
Supports:
- stdio transport for Claude Desktop (no RBAC, uses config file)
- http transport for Streamlit/API clients (session-based RBAC)
"""

from fastmcp import FastMCP
import apstra_core
import argparse
import sys
import signal
import os
import json
import time
from typing import Optional, Dict, Any
from session_manager import session_manager
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Apstra MCP Server')
    parser.add_argument('-f', '--config-file', default='apstra_config.json',
                      help='Path to Apstra configuration JSON file (default: apstra_config.json)')
    parser.add_argument('-t', '--transport', default='stdio', choices=['stdio', 'http'],
                      help='Transport mode: stdio for Claude Desktop, http for Streamlit/API (default: stdio)')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                      help='Host to bind to for HTTP transport (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', type=int, default=8080,
                      help='Port to bind to for HTTP transport (default: 8080)')
    return parser.parse_args()

# Global variables
args = None
mcp = None
http_app = None

# Initialize everything
try:
    args = parse_args()
    logger.info(f"Transport mode: {args.transport}")
    logger.info(f"Config file: {args.config_file}")
    
    # Initialize Apstra core with config
    apstra_core.initialize_config(args.config_file)
    logger.info("Apstra config initialized")
    
    # Create MCP server instance
    mcp = FastMCP("Apstra MCP Server")
    logger.info("MCP server created")
    
except Exception as e:
    logger.error(f"Initialization failed: {e}")
    sys.exit(1)

# =============================================================================
# MCP TOOL DEFINITIONS - AUTHENTICATION
# =============================================================================

@mcp.tool()
def login(username: str, password: str, server: str, port: str = "443") -> str:
    """
    Authenticate with Apstra server (HTTP transport only).
    stdio transport uses config file authentication.
    """
    if args.transport == 'stdio':
        return json.dumps({
            "error": "Not applicable", 
            "message": "stdio transport uses config file authentication"
        }, indent=2)
    
    # HTTP transport - create session
    success, message, token = session_manager.authenticate_user(
        username, password, server, port
    )
    
    if success and token:
        return json.dumps({
            "session_token": token,
            "message": message,
            "expires_in": f"{session_manager.session_timeout} seconds"
        }, indent=2)
    else:
        return json.dumps({
            "error": "Authentication failed",
            "message": message
        }, indent=2)

@mcp.tool()
def logout(session_token: str) -> str:
    """Invalidate session token (HTTP transport only)."""
    if args.transport == 'stdio':
        return json.dumps({
            "error": "Not applicable",
            "message": "stdio transport has no sessions"
        }, indent=2)
    
    if session_manager.logout_session(session_token):
        return json.dumps({"message": "Logout successful"}, indent=2)
    else:
        return json.dumps({"message": "Session not found"}, indent=2)

@mcp.tool()
def session_info(session_token: Optional[str] = None) -> str:
    """Get current authentication status."""
    info = {
        "transport": args.transport,
        "config_file": args.config_file
    }
    
    if args.transport == 'stdio':
        info["authentication"] = "config_file"
        info["message"] = "Using credentials from config file"
    else:
        info["authentication"] = "session_based"
        info["active_sessions"] = len(session_manager.sessions)
        info["message"] = "Use login() to authenticate"
        if session_token:
            session_info_details = session_manager.get_session_info(session_token)
            if session_info_details:
                info["session_details"] = session_info_details
            else:
                info["session_error"] = "Invalid or expired session token"
    
    return json.dumps(info, indent=2)

@mcp.tool()
def health() -> str:
    """Server health check."""
    health_info = {
        "status": "healthy",
        "service": "apstra-mcp",
        "transport": args.transport,
        "timestamp": time.time()
    }
    
    if args.transport == 'http':
        health_info["sessions"] = len(session_manager.sessions)
    
    # Test Apstra connectivity
    try:
        result = apstra_core.auth()
        health_info["apstra_connection"] = "OK" if "token" in result else "FAILED"
    except Exception as e:
        health_info["apstra_connection"] = f"ERROR: {str(e)}"
    
    return json.dumps(health_info, indent=2)

# =============================================================================
# MCP TOOL DEFINITIONS - QUERY OPERATIONS
# =============================================================================

@mcp.tool()
def get_bp(server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get list of all blueprints"""
    return apstra_core.get_bp(server_url)


@mcp.tool()
def get_racks(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get all racks in a blueprint"""
    return apstra_core.get_racks(blueprint_id, server_url)

@mcp.tool()
def get_rz(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get all routing zones in a blueprint"""
    return apstra_core.get_rz(blueprint_id, server_url)

@mcp.tool()
def get_vn(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get virtual networks in a blueprint"""
    return apstra_core.get_vn(blueprint_id, server_url)

@mcp.tool()
def get_remote_gw(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get all remote gateways in a blueprint"""
    return apstra_core.get_remote_gw(blueprint_id, server_url)

@mcp.tool()
def get_system_info(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get systems (devices) in a blueprint"""
    return apstra_core.get_system_info(blueprint_id, server_url)

@mcp.tool()
def get_anomalies(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get anomalies in a blueprint"""
    return apstra_core.get_anomalies(blueprint_id, server_url)

@mcp.tool()
def get_diff_status(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get configuration diff status for a blueprint"""
    return apstra_core.get_diff_status(blueprint_id, server_url)

@mcp.tool()
def get_templates(server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get list of all available templates"""
    return apstra_core.get_templates(server_url)

@mcp.tool()
def get_protocol_sessions(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Get protocol sessions in a blueprint"""
    return apstra_core.get_protocol_sessions(blueprint_id, server_url)

# =============================================================================
# MCP TOOL DEFINITIONS - MANAGEMENT OPERATIONS
# =============================================================================

@mcp.tool()
def deploy(blueprint_id: str, description: str, staging_version: int, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Deploy blueprint configuration"""
    return apstra_core.deploy(blueprint_id, description, staging_version, server_url)

@mcp.tool()
def delete_blueprint(blueprint_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Delete a blueprint"""
    return apstra_core.delete_blueprint(blueprint_id, server_url)

# =============================================================================
# MCP TOOL DEFINITIONS - CREATE OPERATIONS
# =============================================================================

@mcp.tool()
def create_vn(blueprint_id: str, security_zone_id: str, vn_name: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Create a virtual network in a routing zone"""
    return apstra_core.create_vn(blueprint_id, security_zone_id, vn_name, server_url)

@mcp.tool()
def create_remote_gw(blueprint_id: str, gw_ip: str, gw_asn: int, gw_name: str, local_gw_nodes: list, evpn_route_types: str = "all", password: Optional[str] = None, keepalive_timer: int = 10, evpn_interconnect_group_id: Optional[str] = None, holdtime_timer: int = 30, ttl: int = 30, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Create a remote EVPN gateway"""
    return apstra_core.create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, evpn_route_types, password, keepalive_timer, evpn_interconnect_group_id, holdtime_timer, ttl, server_url)

@mcp.tool()
def create_datacenter_blueprint(blueprint_name: str, template_id: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Create a new datacenter blueprint from a template"""
    return apstra_core.create_datacenter_blueprint(blueprint_name, template_id, server_url)

@mcp.tool()
def create_freeform_blueprint(blueprint_name: str, server_url: Optional[str] = None, session_token: Optional[str] = None) -> str:
    """Create a new freeform blueprint"""
    return apstra_core.create_freeform_blueprint(blueprint_name, server_url)

logger.info("All MCP tools registered")

# =============================================================================
# HTTP TRANSPORT SETUP
# =============================================================================

def setup_http_endpoints():
    """Set up HTTP endpoints for MCP protocol compliance"""
    global http_app
    
    # Import FastAPI only when needed
    from fastapi import FastAPI, HTTPException, Depends, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from pydantic import BaseModel
    import inspect
    
    # Create FastAPI app
    http_app = FastAPI(
        title="Apstra MCP Server",
        version="2.0.0",
        description="MCP server with session-based authentication"
    )
    
    # Add CORS
    http_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Security
    security = HTTPBearer()
    
    # Pydantic models
    class LoginRequest(BaseModel):
        username: str
        password: str
        server: str
        port: str = "443"
    
    class MCPRequest(BaseModel):
        params: Dict[str, Any] = {}
    
    # Authentication dependency
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Validate bearer token and return user credentials"""
        user_creds = session_manager.validate_session(credentials.credentials)
        if not user_creds:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_creds
    
    # MCP Protocol endpoints
    @http_app.post("/mcp/v1/initialize")
    async def mcp_initialize():
        """MCP protocol initialization"""
        return {
            "protocolVersion": "1.0",
            "serverInfo": {
                "name": "apstra-mcp",
                "version": "2.0.0"
            },
            "capabilities": {
                "tools": True,
                "prompts": False,
                "resources": False
            }
        }
    
    @http_app.post("/mcp/v1/list_tools")
    async def mcp_list_tools(user: Dict[str, Any] = Depends(get_current_user)):
        """List available MCP tools"""
        try:
            # Use FastMCP's get_tools() method 
            mcp_tools = await mcp.get_tools()
            
            tools = []
            for tool_name in mcp_tools:
                # Skip auth tools for authenticated endpoints
                if tool_name in ['login', 'logout', 'session_info', 'health']:
                    continue
                
                # Add basic tool definition - FastMCP doesn't expose detailed schemas via API
                tools.append({
                    "name": tool_name,
                    "description": f"Execute {tool_name} operation",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                })
            
            return {"tools": tools}
            
        except Exception as e:
            logger.error(f"Failed to list tools: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to access tools: {str(e)}")
    
    @http_app.post("/mcp/v1/call_tool")
    async def mcp_call_tool(request: MCPRequest, user: Dict[str, Any] = Depends(get_current_user)):
        """Call an MCP tool"""
        params = request.params
        tool_name = params.get("name")
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name required")
        
        # Check if tool exists using FastMCP's get_tools API
        try:
            available_tools = await mcp.get_tools()
            if tool_name not in available_tools:
                raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found: {str(e)}")
        
        # Skip auth tools
        if tool_name in ['login', 'logout', 'session_info', 'health']:
            raise HTTPException(status_code=403, detail=f"Tool '{tool_name}' not available here")
        
        # Prepare arguments (exclude 'name') and add user auth
        tool_args = {k: v for k, v in params.items() if k != "name"}
        
        # Add auth parameter for tools that need it
        # Most apstra tools will need authentication
        if tool_name not in ['session_info', 'health']:
            tool_args['auth'] = user
        
        # Execute tool using FastMCP
        try:
            result = await mcp.call_tool(tool_name, tool_args)
            
            # Format response in MCP format
            return {
                "content": [
                    {
                        "type": "text", 
                        "text": result if isinstance(result, str) else json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @http_app.post("/mcp/v1/list_prompts")
    async def mcp_list_prompts(user: Dict[str, Any] = Depends(get_current_user)):
        """List prompts (not supported)"""
        return {"prompts": []}
    
    @http_app.post("/mcp/v1/list_resources")
    async def mcp_list_resources(user: Dict[str, Any] = Depends(get_current_user)):
        """List resources (not supported)"""
        return {"resources": []}
    
    # Authentication endpoints
    @http_app.post("/tools/login")
    async def login_endpoint(request: LoginRequest):
        """Login to get session token"""
        success, message, token = session_manager.authenticate_user(
            request.username, request.password, request.server, request.port
        )
        
        if success and token:
            return {
                "status": "success",
                "session_token": token,
                "message": message
            }
        else:
            raise HTTPException(status_code=401, detail=message)
    
    @http_app.post("/tools/logout")
    async def logout_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
        """Logout and invalidate session"""
        # Get token from auth header via dependency
        return {"message": "Logout successful"}
    
    @http_app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "transport": "http",
            "sessions": len(session_manager.sessions)
        }
    
    return http_app

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Shutting down (signal {signum})...")
    sys.exit(0)

def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.transport == 'stdio':
            # Simple stdio mode for Claude Desktop
            logger.info("Starting stdio transport for Claude Desktop")
            mcp.run(transport="stdio")
            
        elif args.transport == 'http':
            # HTTP mode for Streamlit/API clients
            logger.info(f"Starting HTTP transport on {args.host}:{args.port}")
            
            # Set up HTTP endpoints
            global http_app
            http_app = setup_http_endpoints()
            
            # Start session cleanup
            session_manager.cleanup_expired_sessions()
            
            # Run server
            import uvicorn
            uvicorn.run(http_app, host=args.host, port=args.port, log_level="info")
            
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
    except Exception as e:
        logger.error(f"{e}")
        import traceback
        logger.exception("Unexpected error:")
        sys.exit(1)

if __name__ == "__main__":
    main()