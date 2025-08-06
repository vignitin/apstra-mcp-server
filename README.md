# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. This enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## Features

- **Blueprint Management**: Retrieve, create, and delete blueprint configurations
- **Infrastructure Queries**: Get rack, routing zone, and system information
- **Network Provisioning**: Create virtual networks and remote gateways for datacenter interconnection
- **Configuration Management**: Check deployment status and deploy configurations
- **Template Management**: Get available templates for blueprint creation
- **Remote Gateway Management**: Create and manage EVPN remote gateways between datacenters
- **System Information**: Query system details within blueprints
- **Protocol Session Monitoring**: Monitor BGP and other protocol sessions
- **Port Configuration**: Flexible server connection with custom port support (defaults to 443)
- **Enhanced Output Formatting**: All tools return data with comprehensive formatting guidelines including tables, icons, and structured layouts
- **Robust Error Handling**: Comprehensive error reporting and debugging capabilities
- **Seamless Integration**: Works with Claude Desktop and other MCP clients

## Available Tools

### Query Tools
- `get_bp()` - Get blueprint information
- `get_racks(blueprint_id)` - Get rack information for a blueprint
- `get_rz(blueprint_id)` - Get routing zone information for a blueprint
- `get_vn(blueprint_id)` - Get virtual network information for a blueprint
- `get_system_info(blueprint_id)` - Get system information for devices in a blueprint
- `get_diff_status(blueprint_id)` - Get deployment diff status
- `get_templates()` - Get available templates for blueprint creation
- `get_anomalies(blueprint_id)` - Get anomaly information for a blueprint
- `get_remote_gw(blueprint_id)` - Get remote gateway information for a blueprint
- `get_protocol_sessions(blueprint_id)` - Get protocol session information for a blueprint

### Management Tools
- `deploy(blueprint_id, description, staging_version)` - Deploy configurations
- `delete_blueprint(blueprint_id)` - Delete blueprints by ID

### Create Tools
- `create_vn(blueprint_id, security_zone_id, vn_name)` - Create virtual networks
- `create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, ...)` - Create remote gateways for datacenter interconnection
- `create_datacenter_blueprint(blueprint_name, template_id)` - Create new datacenter blueprints
- `create_freeform_blueprint(blueprint_name)` - Create new freeform blueprints

## Prerequisites

- Python 3.7+
- Access to a Juniper Apstra server
- Valid Apstra credentials

## Installation

1. Install required dependencies:
```bash
pip install fastmcp httpx
```

Or using uv (recommended):
```bash
uv add fastmcp httpx
```

2. Clone or download this repository

3. Configure your Apstra server connection by editing `apstra_config.json` (see `apstra_config_sample.json` for reference):

**Option 1: Separate server and port (recommended)**
```json
{
  "aos_server": "your-apstra-server-ip-or-hostname",
  "aos_port": "your-apstra-server-port",
  "username": "your-username", 
  "password": "your-password"
}
```

**Option 2: Combined server:port format**
```json
{
  "aos_server": "your-apstra-server-ip-or-hostname:port",
  "username": "your-username",
  "password": "your-password"
}
```

**Option 3: Default HTTPS port (443)**
```json
{
  "aos_server": "your-apstra-server-ip-or-hostname",
  "username": "your-username",
  "password": "your-password"
}
```

> **Note**: If no port is specified, the server defaults to port 443 (standard HTTPS).

## Running the Server

### Using uv (recommended):
```bash
uv run --with fastmcp,httpx python3 apstra_mcp.py -f apstra_config.json
```

### Using pip:
```bash
python3 apstra_mcp.py -f apstra_config.json
```

> **Note**: The server will start and wait for MCP client connections. Debug information will be printed to stderr to help with troubleshooting.

## Claude Desktop Integration

To use this MCP server with Claude Desktop, add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "Apstra MCP server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp,httpx",
        "python3",
        "/path/to/your/apstra_mcp.py",
        "-f",
        "/path/to/your/apstra_config.json"
      ]
    }
  }
}
```

Make sure to update the path to match your actual file location.

## Security Considerations

⚠️ **Important Security Notes:**
- This implementation stores credentials in plaintext
- SSL verification is disabled (`verify=False`)
- For production use, consider:
  - Using environment variables for credentials
  - Implementing proper certificate validation
  - Adding authentication/authorization layers

## Remote Gateway Management

The server provides comprehensive support for creating and managing EVPN remote gateways to interconnect datacenters:

### create_remote_gw Function
Creates remote gateways with flexible parameter options:

**Required Parameters:**
- `blueprint_id` - Target blueprint ID
- `gw_ip` - Remote gateway IP address (prefer loopback addresses)  
- `gw_asn` - Remote gateway ASN (1-4294967295)
- `gw_name` - Gateway name identifier
- `local_gw_nodes` - List of local gateway node IDs

**Optional Parameters (with defaults):**
- `evpn_route_types="all"` - EVPN route types (all, type5_only)
- `password=None` - BGP session password
- `keepalive_timer=10` - BGP keepalive timer (1-65535)
- `evpn_interconnect_group_id=None` - EVPN interconnect group ID
- `holdtime_timer=30` - BGP holdtime timer (3-65535)
- `ttl=30` - BGP TTL value (2-255)

### Usage Examples

**Minimal remote gateway creation:**
```python
create_remote_gw(
    blueprint_id="blueprint-123",
    gw_ip="192.168.2.4",
    gw_asn=65002,
    gw_name="DC2-Gateway", 
    local_gw_nodes=["node1", "node2"]
)
```

**With optional parameters:**
```python
create_remote_gw(
    blueprint_id="blueprint-123",
    gw_ip="192.168.2.4",
    gw_asn=65002,
    gw_name="DC2-Gateway",
    local_gw_nodes=["node1", "node2"],
    password="bgp_secret",
    ttl=255,
    evpn_route_types="type5_only"
)
```

## Usage Examples

Once connected to Claude Desktop, you can use natural language commands like:

### Basic Queries
- "Show me all blueprints in the Apstra system"
- "List the racks for blueprint [blueprint-id]"
- "Show me the system information for blueprint [blueprint-id]"
- "Show me the virtual networks in blueprint [blueprint-id]"
- "Get protocol sessions for blueprint [blueprint-id]"
- "Get anomalies for blueprint [blueprint-id]"

### Network Provisioning
- "Create a virtual network called 'web-tier' in routing zone [zone-id]"
- "Create a remote gateway connecting DC1 to DC2 using IP 192.168.2.4"
- "Show me existing remote gateways in blueprint [blueprint-id]"

### Configuration Management
- "Deploy the staging configuration for blueprint [blueprint-id] with description 'Production deployment'"
- "Check the diff status for blueprint [blueprint-id]"

### Blueprint Management
- "Get available templates for creating new blueprints"
- "Create a new datacenter blueprint called 'production-dc' using template [template-id]"
- "Delete blueprint [blueprint-id]"

## Output Formatting

All query tools now return enhanced formatted output with:
- **Structured Tables**: Device information, protocol sessions, and anomalies are displayed in well-organized tables
- **Status Icons**: Visual indicators for health status (✅ ❌ ⚠️), severity levels (🔴 🟡 🟢), and network elements (🌐 🏢 🔀)
- **Summary Sections**: Quick overview with key metrics and status counts
- **Consistent Layout**: All responses follow a standardized format for easy scanning and analysis

This formatting helps you quickly identify issues, understand network state, and take appropriate actions.

## Troubleshooting

### Server Connection Issues
- **Port Configuration**: Ensure your Apstra server port is correctly specified in the config file
- **Authentication**: Verify your username and password are correct
- **Network Access**: Check that your client can reach the Apstra server on the specified port

### MCP Server Issues
- **Tools Not Appearing**: Ensure the server started successfully by checking Claude Desktop logs

### Debug Information
The server includes comprehensive debug logging to stderr. Check Claude Desktop logs for detailed error information when troubleshooting connection or API issues.

## Blog Post

For more details and background, see the accompanying blog post: [MCP for Datacenter Networks](https://medium.com/@vignitin/mcp-for-datacenter-networks-aa003de81256)

## License

This project is provided as-is for educational and demonstration purposes.
