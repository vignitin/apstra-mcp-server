from fastmcp import FastMCP
import apstra_core
import argparse
import sys

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Apstra MCP Server')
    parser.add_argument('-f', '--config-file', default='apstra_config.json',
                      help='Path to Apstra configuration JSON file (default: apstra_config.json)')
    return parser.parse_args()

# Initialize configuration
args = parse_args()
apstra_core.initialize_config(args.config_file)

# Create an MCP server
mcp = FastMCP("Apstra MCP server")

# Get blueprints
@mcp.tool()
def get_bp(server_url: str = None) -> str:
    """Gets blueprint information"""
    return apstra_core.get_bp(server_url)

# Get racks
@mcp.tool()
def get_racks(blueprint_id: str, server_url: str = None) -> str:
    """Gets rack information for a blueprint"""
    return apstra_core.get_racks(blueprint_id, server_url)

# Get routing zones
@mcp.tool()
def get_rz(blueprint_id: str, server_url: str = None) -> str:
    """Gets routing zone information for a blueprint"""
    return apstra_core.get_rz(blueprint_id, server_url)


# Create virtual networks
@mcp.tool()
def create_vn(blueprint_id: str, security_zone_id: str, vn_name: str, server_url: str = None) -> str:
    """Creates a virtual network in a given blueprint and routing zone"""
    return apstra_core.create_vn(blueprint_id, security_zone_id, vn_name, server_url)

# Check staging version through diff-status
@mcp.tool()
def get_diff_status(blueprint_id: str, server_url: str = None) -> str:
    """Gets the diff status for a blueprint"""
    return apstra_core.get_diff_status(blueprint_id, server_url)

# Deploy config
@mcp.tool()
def deploy(blueprint_id: str, description: str, staging_version: int, server_url: str = None) -> str:
    """Deploys the config for a blueprint"""
    return apstra_core.deploy(blueprint_id, description, staging_version, server_url)

# Get templates
@mcp.tool()
def get_templates(server_url: str = None) -> str:
    """Gets available templates for blueprint creation"""
    return apstra_core.get_templates(server_url)

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

# Delete blueprint
@mcp.tool()
def delete_blueprint(blueprint_id: str, server_url: str = None) -> str:
    """Deletes a blueprint by ID"""
    return apstra_core.delete_blueprint(blueprint_id, server_url)

