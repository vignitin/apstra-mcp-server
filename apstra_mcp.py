#!/usr/bin/env python3
"""
Apstra MCP Server with Native FastMCP HTTP Transport
Supports:
- stdio transport for Claude Desktop
- streamable-http transport with native FastMCP streaming support
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
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Apstra MCP Server')
    parser.add_argument('-f', '--config-file', default='apstra_config.json',
                      help='Path to Apstra configuration JSON file (default: apstra_config.json)')
    parser.add_argument('-t', '--transport', default='stdio', choices=['stdio', 'streamable-http'],
                      help='Transport mode: stdio for Claude Desktop, streamable-http for streaming API (default: stdio)')
    parser.add_argument('-H', '--host', default='127.0.0.1',
                      help='Host to bind to for HTTP transport (default: 127.0.0.1)')
    parser.add_argument('-p', '--port', type=int, default=8080,
                      help='Port to bind to for HTTP transport (default: 8080)')
    return parser.parse_args()

# Global variables
args = None
mcp = None

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
# MCP TOOL DEFINITIONS - QUERY OPERATIONS
# =============================================================================

@mcp.tool()
def health() -> str:
    """Server health check."""
    health_info = {
        "status": "healthy",
        "service": "apstra-mcp",
        "transport": args.transport,
        "timestamp": time.time()
    }
    
    # Test Apstra connectivity
    try:
        result = apstra_core.auth()
        health_info["apstra_connection"] = "OK" if "token" in result else "FAILED"
    except Exception as e:
        health_info["apstra_connection"] = f"ERROR: {str(e)}"
    
    return json.dumps(health_info, indent=2)

@mcp.tool()
def formatting_guidelines() -> str:
    """Get formatting guidelines for presenting network infrastructure data with tables and icons"""
    return apstra_core.get_formatting_guidelines()

@mcp.tool()
def get_bp() -> str:
    """Get list of all blueprints"""
    data = apstra_core.get_bp()
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_blueprint_guidelines()
    return f"{guidelines}\n\n## Blueprint Data:\n{data}"


@mcp.tool()
def get_racks(blueprint_id: str) -> str:
    """Get all racks in a blueprint"""
    data = apstra_core.get_racks(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_device_guidelines()
    return f"{guidelines}\n\n## Rack Data:\n{data}"

@mcp.tool()
def get_rz(blueprint_id: str) -> str:
    """Get all routing zones in a blueprint"""
    data = apstra_core.get_rz(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_network_guidelines()
    return f"{guidelines}\n\n## Routing Zones Data:\n{data}"

@mcp.tool()
def get_vn(blueprint_id: str) -> str:
    """Get virtual networks in a blueprint"""
    data = apstra_core.get_vn(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_network_guidelines()
    return f"{guidelines}\n\n## Virtual Networks Data:\n{data}"

@mcp.tool()
def get_remote_gw(blueprint_id: str) -> str:
    """Get all remote gateways in a blueprint"""
    data = apstra_core.get_remote_gw(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_network_guidelines()
    return f"{guidelines}\n\n## Remote Gateways Data:\n{data}"

@mcp.tool()
def get_system_info(blueprint_id: str) -> str:
    """Get systems (devices) in a blueprint"""
    data = apstra_core.get_system_info(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_device_guidelines()
    return f"{guidelines}\n\n## System Information Data:\n{data}"

@mcp.tool()
def get_anomalies(blueprint_id: str) -> str:
    """Get anomalies in a blueprint"""
    data = apstra_core.get_anomalies(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_anomaly_guidelines()
    return f"{guidelines}\n\n## Anomaly Data:\n{data}"

@mcp.tool()
def get_diff_status(blueprint_id: str) -> str:
    """Get configuration diff status for a blueprint"""
    data = apstra_core.get_diff_status(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_status_guidelines()
    return f"{guidelines}\n\n## Configuration Diff Status:\n{data}"

@mcp.tool()
def get_templates() -> str:
    """Get list of all available templates"""
    data = apstra_core.get_templates()
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_blueprint_guidelines()
    return f"{guidelines}\n\n## Templates Data:\n{data}"

@mcp.tool()
def get_protocol_sessions(blueprint_id: str) -> str:
    """Get protocol sessions in a blueprint"""
    data = apstra_core.get_protocol_sessions(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_status_guidelines()
    return f"{guidelines}\n\n## Protocol Sessions Data:\n{data}"

# =============================================================================
# MCP TOOL DEFINITIONS - MANAGEMENT OPERATIONS
# =============================================================================

@mcp.tool()
def deploy(blueprint_id: str, description: str, staging_version: int) -> str:
    """Deploy blueprint configuration"""
    data = apstra_core.deploy(blueprint_id, description, staging_version)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Deployment Result:\n{data}"

@mcp.tool()
def delete_blueprint(blueprint_id: str) -> str:
    """Delete a blueprint"""
    data = apstra_core.delete_blueprint(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Deletion Result:\n{data}"

# =============================================================================
# MCP TOOL DEFINITIONS - CREATE OPERATIONS
# =============================================================================

@mcp.tool()
def create_vn(blueprint_id: str, security_zone_id: str, vn_name: str) -> str:
    """Create a virtual network in a routing zone"""
    data = apstra_core.create_vn(blueprint_id, security_zone_id, vn_name)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Virtual Network Creation Result:\n{data}"

@mcp.tool()
def create_remote_gw(blueprint_id: str, gw_ip: str, gw_asn: int, gw_name: str, local_gw_nodes: list, evpn_route_types: str = "all", password: Optional[str] = None, keepalive_timer: int = 10, evpn_interconnect_group_id: Optional[str] = None, holdtime_timer: int = 30, ttl: int = 30) -> str:
    """Create a remote EVPN gateway"""
    data = apstra_core.create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, evpn_route_types, password, keepalive_timer, evpn_interconnect_group_id, holdtime_timer, ttl)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Remote Gateway Creation Result:\n{data}"

@mcp.tool()
def create_datacenter_blueprint(blueprint_name: str, template_id: str) -> str:
    """Create a new datacenter blueprint from a template"""
    data = apstra_core.create_datacenter_blueprint(blueprint_name, template_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Blueprint Creation Result:\n{data}"

@mcp.tool()
def create_freeform_blueprint(blueprint_name: str) -> str:
    """Create a new freeform blueprint"""
    data = apstra_core.create_freeform_blueprint(blueprint_name)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Blueprint Creation Result:\n{data}"

logger.info("All MCP tools registered")

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
            logger.info("Starting stdio transport")
            mcp.run(transport="stdio")
            
        elif args.transport == 'streamable-http':
            # Native FastMCP streamable HTTP mode with SSE support
            logger.info(f"Starting native FastMCP streamable HTTP transport on {args.host}:{args.port}")
            logger.info("This transport supports automatic SSE upgrades for streaming responses")
            
            # Use FastMCP's native streamable HTTP transport
            # This automatically handles:
            # - MCP protocol endpoints
            # - Automatic SSE upgrades for streaming
            # - Bidirectional communication
            # - Long-running operation progress
            mcp.run(transport="streamable-http", host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        logger.info("Shutdown by user")
    except Exception as e:
        logger.error(f"{e}")
        import traceback
        logger.exception("Unexpected error:")
        sys.exit(1)

if __name__ == "__main__":
    main()