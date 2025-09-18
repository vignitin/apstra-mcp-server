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
from typing import Optional, Dict, Any, Union, List
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
def get_ct(blueprint_id: str) -> str:
    """Get connectivity templates in a blueprint"""
    data = apstra_core.get_ct(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_network_guidelines()
    return f"{guidelines}\n\n## Connectivity Templates Data:\n{data}"

@mcp.tool()
def get_app_ep(blueprint_id: str) -> str:
    """Get application endpoints for connectivity templates in a blueprint"""
    data = apstra_core.get_app_ep(blueprint_id)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_network_guidelines()
    return f"{guidelines}\n\n## Application endpoints Data:\n{data}"

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
def create_vn(blueprint_id: str, security_zone_id: str, vn_name: str, 
              virtual_gateway_ipv4: str, ipv4_subnet: str,
              system_ids: Optional[str] = None, 
              vlan_ids: Optional[str] = None, 
              access_switch_node_ids: Optional[str] = None,
              svi_ips: Optional[str] = None,
              vn_type: str = "vxlan",
              ipv4_enabled: Optional[str] = "true",
              dhcp_service: str = "dhcpServiceDisabled", 
              virtual_gateway_ipv4_enabled: Optional[str] = "true",
              create_policy_tagged: Optional[str] = None,
              virtual_gateway_ipv6_enabled: Optional[str] = "false",
              ipv6_enabled: Optional[str] = "false") -> str:
    """Create a virtual network using the virtual-networks-batch API with layered normalization
    
    This tool creates a virtual network (VN) using the correct Apstra batch API endpoint.
    Uses layered normalization to handle MCP parameter type conversion issues.
    
    Args:
        blueprint_id: The blueprint ID where the VN will be created (MANDATORY)
        security_zone_id: The security zone (routing zone) ID for the VN (MANDATORY)
        vn_name: The name/label for the virtual network (MANDATORY)
        virtual_gateway_ipv4: IPv4 address for virtual gateway (MANDATORY, e.g., "10.1.1.1")
        ipv4_subnet: IPv4 subnet in CIDR format (MANDATORY, e.g., "10.1.1.0/24")
        system_ids: Optional system ID(s) as JSON string or single value:
                    - Single: "uc3ZiG_yU15gKSzovg"
                    - JSON array: '["uc3ZiG_yU15gKSzovg", "QmQU4o84uk5_8t7IhQ"]'
        vlan_ids: Optional VLAN ID(s) as string:
                  - Single: "400" (applied to all systems)
                  - JSON array: "[400, 401]" (must match system_ids length)
        access_switch_node_ids: Optional access switch node IDs as JSON string:
                               - Single list: '["node1", "node2"]' (applied to all bindings)
                               - Nested lists: '[["node1"], ["node2", "node3"]]' (one per binding)
        svi_ips: Optional SVI IP configurations as JSON string (auto-generated if not provided)
        vn_type: VN type (default: "vxlan"). Must be "vxlan" or "vlan"
        ipv4_enabled: Whether IPv4 is enabled as string (default: "true"). Use "true" or "false"
        dhcp_service: DHCP service setting (default: "dhcpServiceDisabled")
        virtual_gateway_ipv4_enabled: Whether virtual gateway IPv4 is enabled as string (default: "true"). Use "true" or "false"
        create_policy_tagged: Whether to create policy tagged as string (optional, no default). Use "true" or "false"
        virtual_gateway_ipv6_enabled: Whether virtual gateway IPv6 is enabled as string (default: "false"). Use "true" or "false"
        ipv6_enabled: Whether IPv6 is enabled as string (default: "false"). Use "true" or "false"
    
    MCP Client Usage Examples:
        
        Simple VXLAN VN (no bindings):
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456", 
            "vn_name": "simple_network",
            "vn_type": "vxlan"
        }
        
        Simple VLAN VN:
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456", 
            "vn_name": "vlan_network",
            "vn_type": "vlan"
        }
        
        Single system binding:
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456",
            "vn_name": "server_network",
            "vn_type": "vxlan",
            "system_ids": "uc3ZiG_yU15gKSzovg",
            "vlan_ids": 400
        }
        NOTE: vlan_ids must be integer 400, not string "400"
        
        Multiple systems, same VLAN:
        {
            "blueprint_id": "bp-123", 
            "security_zone_id": "zone-456",
            "vn_name": "shared_network",
            "vn_type": "vxlan",
            "system_ids": ["uc3ZiG_yU15gKSzovg", "QmQU4o84uk5_8t7IhQ"],
            "vlan_ids": 300
        }
        
        Multiple systems, different VLANs:
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456", 
            "vn_name": "multi_vlan_network",
            "vn_type": "vxlan",
            "system_ids": ["uc3ZiG_yU15gKSzovg", "QmQU4o84uk5_8t7IhQ"],
            "vlan_ids": [400, 401]
        }
        NOTE: vlan_ids must be integers [400, 401], not strings ["400", "401"]
        
        With gateway and subnet:
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456",
            "vn_name": "gateway_network",
            "vn_type": "vxlan", 
            "system_ids": "uc3ZiG_yU15gKSzovg",
            "vlan_ids": 400,
            "virtual_gateway_ipv4": "192.168.1.1",
            "ipv4_subnet": "192.168.1.0/24"
        }
        
        With access switches:
        {
            "blueprint_id": "bp-123",
            "security_zone_id": "zone-456",
            "vn_name": "access_network",
            "vn_type": "vxlan",
            "system_ids": ["uc3ZiG_yU15gKSzovg", "QmQU4o84uk5_8t7IhQ"], 
            "vlan_ids": [400, 400],
            "access_switch_node_ids": [["access1"], ["access2", "access3"]]
        }
    
    Important Notes:
        - Uses virtual-networks-batch API endpoint with async=full
        - Layered normalization handles MCP type conversion automatically
        - virtual_gateway_ipv4 and ipv4_subnet are now MANDATORY parameters
        - system_ids, vlan_ids can be JSON strings to handle arrays
        - Boolean parameters accept "true"/"false" strings and convert to proper booleans
        - SVI IPs are auto-generated from system_ids if not provided
        - create_policy_tagged is optional with no default (only set if explicitly provided)
        
    Automatic Leaf Expansion:
        The function intelligently handles redundancy groups vs individual leafs:
        - You can provide leaf pair IDs (e.g., "uc3ZiG_yU15gKSzovg") 
        - bound_to uses your provided system_ids as-is (leaf pairs work here)
        - svi_ips automatically expands leaf pairs to individual leaf IDs
        - Uses get_system_info() to query blueprint topology for mapping
        - Works with mixed scenarios (leaf pairs + single leafs)
    
    Returns:
        JSON string with virtual network creation results and change management guidelines
    """
    # Parse svi_ips if provided as JSON string
    parsed_svi_ips = None
    if svi_ips:
        try:
            import json
            parsed_svi_ips = json.loads(svi_ips) if isinstance(svi_ips, str) else svi_ips
        except json.JSONDecodeError:
            pass  # Keep as None if invalid JSON
    
    # Convert boolean strings to actual booleans (MCP client sends "true"/"false" as strings)
    def normalize_boolean(value):
        if isinstance(value, str):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
        return value
    
    # Normalize all boolean parameters (now all are strings)
    normalized_ipv4_enabled = normalize_boolean(ipv4_enabled)
    normalized_virtual_gateway_ipv4_enabled = normalize_boolean(virtual_gateway_ipv4_enabled)
    normalized_create_policy_tagged = normalize_boolean(create_policy_tagged) if create_policy_tagged is not None else None
    normalized_virtual_gateway_ipv6_enabled = normalize_boolean(virtual_gateway_ipv6_enabled)
    normalized_ipv6_enabled = normalize_boolean(ipv6_enabled)
    
    data = apstra_core.create_vn(blueprint_id, security_zone_id, vn_name, 
                                virtual_gateway_ipv4, ipv4_subnet,
                                system_ids, vlan_ids, access_switch_node_ids,
                                parsed_svi_ips, vn_type, normalized_ipv4_enabled, 
                                dhcp_service, normalized_virtual_gateway_ipv4_enabled,
                                normalized_create_policy_tagged, normalized_virtual_gateway_ipv6_enabled, normalized_ipv6_enabled)
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

@mcp.tool()
def apply_ct_policies(blueprint_id: str, application_points: str) -> str:
    """Apply connectivity template policies to application endpoints using batch policy API
    
    This tool applies or removes connectivity template policies from application endpoints (interfaces).
    Uses the obj-policy-batch-apply API endpoint with PATCH method.
    
    Args:
        blueprint_id: The blueprint ID where policies will be applied (MANDATORY)
        application_points: JSON string containing application points configuration (MANDATORY)
                           
    Application Points Format:
        The application_points parameter must be a JSON string with the following structure:
        
        '[
            {
                "id": "interface_id_1",
                "policies": [
                    {
                        "policy": "policy_id_1", 
                        "used": true
                    }
                ]
            },
            {
                "id": "interface_id_2",
                "policies": [
                    {
                        "policy": "policy_id_1",
                        "used": false
                    }
                ]
            }
        ]'
        
    Field Descriptions:
        - id: Interface ID of the application endpoint to modify
        - policy: Policy ID of the connectivity template to apply/remove
        - used: Boolean flag (true = apply policy, false = remove policy)
        
    MCP Client Usage Examples:
        
        Apply single policy to single interface:
        {
            "blueprint_id": "91de3df7-4ac4-44e6-8374-3fca09126704",
            "application_points": '[{"id": "BfkK4q--O8CrlnBaPA", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": true}]}]'
        }
        
        Apply policy to multiple interfaces:
        {
            "blueprint_id": "91de3df7-4ac4-44e6-8374-3fca09126704", 
            "application_points": '[
                {"id": "BfkK4q--O8CrlnBaPA", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": true}]},
                {"id": "xVZXowwsRXVswg29xQ", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": true}]}
            ]'
        }
        
        Remove policy from interface:
        {
            "blueprint_id": "91de3df7-4ac4-44e6-8374-3fca09126704",
            "application_points": '[{"id": "g3960_IYrqzdZbPkQg", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": false}]}]'
        }
        
        Mixed operations (apply to some, remove from others):
        {
            "blueprint_id": "91de3df7-4ac4-44e6-8374-3fca09126704",
            "application_points": '[
                {"id": "BfkK4q--O8CrlnBaPA", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": true}]},
                {"id": "g3960_IYrqzdZbPkQg", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": false}]},
                {"id": "xVZXowwsRXVswg29xQ", "policies": [{"policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d", "used": true}]}
            ]'
        }
    
    Important Notes:
        - Uses PATCH method with obj-policy-batch-apply endpoint
        - Supports async=full for asynchronous processing
        - Each interface can have multiple policies applied/removed in one call
        - Interface IDs can be found using get_app_ep() tool
        - Policy IDs can be found using get_ct() tool
        - Boolean "used" field determines whether policy is applied (true) or removed (false)
        
    Returns:
        JSON string with policy application results and change management guidelines
    """
    data = apstra_core.apply_ct_policies(blueprint_id, application_points)
    guidelines = apstra_core.get_base_guidelines() + apstra_core.get_change_mgmt_guidelines()
    return f"{guidelines}\n\n## Connectivity Template Policy Application Result:\n{data}"

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