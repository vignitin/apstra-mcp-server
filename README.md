# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. This enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## Features

- **Blueprint Management**: Retrieve, create, and delete blueprint configurations
- **Infrastructure Queries**: Get rack and routing zone details
- **Network Provisioning**: Create virtual networks within blueprints
- **Configuration Management**: Check deployment status and deploy configurations
- **Template Management**: Get available templates for blueprint creation
- **Port Configuration**: Flexible server connection with custom port support (defaults to 443)
- **Robust Error Handling**: Comprehensive error reporting and debugging capabilities
- **Seamless Integration**: Works with Claude Desktop and other MCP clients

## Available Tools

- `get_bp()` - Get blueprint information
- `get_racks(blueprint_id)` - Get rack information for a blueprint
- `get_rz(blueprint_id)` - Get routing zone information for a blueprint
- `create_vn(blueprint_id, security_zone_id, vn_name)` - Create virtual networks
- `get_diff_status(blueprint_id)` - Get deployment diff status
- `deploy(blueprint_id, description, staging_version)` - Deploy configurations
- `get_templates()` - Get available templates for blueprint creation
- `create_datacenter_blueprint(blueprint_name, template_id)` - Create new datacenter blueprints
- `create_freeform_blueprint(blueprint_name)` - Create new freeform blueprints
- `delete_blueprint(blueprint_id)` - Delete blueprints by ID

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

## Usage Examples

Once connected to Claude Desktop, you can use natural language commands like:

- "Show me all blueprints in the Apstra system"
- "List the racks for blueprint [blueprint-id]"
- "Create a virtual network called 'web-tier' in routing zone [zone-id]"
- "Deploy the staging configuration for blueprint [blueprint-id] with description 'Production deployment'"
- "Get available templates for creating new blueprints"
- "Create a new datacenter blueprint called 'production-dc' using template [template-id]"
- "Delete blueprint [blueprint-id]"

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
