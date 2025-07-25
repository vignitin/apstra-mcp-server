# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. This enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## Features

- **Blueprint Management**: Retrieve blueprint information and configurations
- **Infrastructure Queries**: Get rack and routing zone details
- **Network Provisioning**: Create virtual networks within blueprints
- **Configuration Management**: Check deployment status and deploy configurations
- **Seamless Integration**: Works with Claude Desktop and other MCP clients

## Available Tools

- `get_bp()` - Get blueprint information
- `get_racks(blueprint_id)` - Get rack information for a blueprint
- `get_rz(blueprint_id)` - Get routing zone information for a blueprint
- `create_vn(blueprint_id, security_zone_id, vn_name)` - Create virtual networks
- `get_diff_status(blueprint_id)` - Get deployment diff status
- `deploy(blueprint_id, description, staging_version)` - Deploy configurations

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
```json
{
  "aos_server": "your-apstra-server-ip-or-hostname",
  "username": "your-username",
  "password": "your-password"
}
```

## Running the Server

### Using uv (recommended):
```bash
uv run --with fastmcp fastmcp run apstra_mcp.py -f apstra_config.json
```

### Using pip:
```bash
python3 apstra_mcp.py -f apstra_config.json
```

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
        "fastmcp",
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

## Usage Examples

Once connected to Claude Desktop, you can use natural language commands like:

- "Show me all blueprints in the Apstra system"
- "List the racks for blueprint [blueprint-id]"
- "Create a virtual network called 'web-tier' in routing zone [zone-id]"
- "Deploy the staging configuration for blueprint [blueprint-id] with description 'Production deployment'"

## Blog Post

For more details and background, see the accompanying blog post: [MCP for Datacenter Networks](https://medium.com/@vignitin/mcp-for-datacenter-networks-aa003de81256)

## License

This project is provided as-is for educational and demonstration purposes.
