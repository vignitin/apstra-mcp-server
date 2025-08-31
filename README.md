# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. Enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## Features

- **Blueprint Management**: Create, retrieve, and delete blueprint configurations
- **Infrastructure Queries**: Get rack, routing zone, and system information  
- **Network Provisioning**: Create virtual networks and remote gateways
- **Configuration Management**: Check deployment status and deploy configurations
- **Protocol Monitoring**: Monitor BGP and other protocol sessions
- **Anomaly Detection**: Retrieve and analyze blueprint anomalies
- **Native Streaming Support**: Real-time updates with Server-Sent Events

## Quick Start

### Local Usage (stdio)
```bash
# Create config file
cp apstra_config_sample.json apstra_config.json
# Edit with your Apstra server details

# Run with stdio transport
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

### Network Deployment (Streamable HTTP)

#### Docker (Recommended)
```bash
# Clone and configure
git clone <this-repo>
cd apstra-mcp-server
cp apstra_config_sample.json apstra_config.json
# Edit config with your Apstra details

# Start HTTP streaming server
docker-compose up -d
```

#### Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Start streamable HTTP server
python3 apstra_mcp.py -t streamable-http -H 0.0.0.0 -p 8080 -f apstra_config.json
```

## Installation

### Prerequisites
- Python 3.7+
- Access to Juniper Apstra server
- Valid Apstra credentials

### Dependencies
```bash
pip install -r requirements.txt
```

## Available Tools (18 total)

### Health & Status Tools (2 tools)
- `health()` - Server health check and Apstra connectivity status
- `formatting_guidelines()` - Get formatting guidelines for network data presentation

### Query Tools (10 tools)
- `get_bp()` - Get blueprint information
- `get_racks(blueprint_id)` - Get rack information  
- `get_rz(blueprint_id)` - Get routing zones
- `get_vn(blueprint_id)` - Get virtual networks
- `get_system_info(blueprint_id)` - Get system/device information
- `get_protocol_sessions(blueprint_id)` - Get protocol sessions
- `get_anomalies(blueprint_id)` - Get blueprint anomalies
- `get_remote_gw(blueprint_id)` - Get remote gateways
- `get_diff_status(blueprint_id)` - Get deployment diff status
- `get_templates()` - Get available templates

### Management Tools (2 tools)
- `deploy(blueprint_id, description, staging_version)` - Deploy configurations
- `delete_blueprint(blueprint_id)` - Delete blueprints

### Create Tools (4 tools)
- `create_vn(blueprint_id, security_zone_id, vn_name)` - Create virtual networks
- `create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, ...)` - Create remote gateways  
- `create_datacenter_blueprint(blueprint_name, template_id)` - Create datacenter blueprints
- `create_freeform_blueprint(blueprint_name)` - Create freeform blueprints

## Security Model

### stdio Transport (Default)
- Secure by default with no network exposure
- Uses configuration file credentials
- Ideal for Claude Desktop integration

### streamable-http Transport
- Network-accessible with native FastMCP streaming capabilities
- Automatic SSE upgrades for real-time updates
- Single container deployment

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "apstra": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp,httpx",
        "python3",
        "/path/to/apstra_mcp.py",
        "-f",
        "/path/to/apstra_config.json"
      ]
    }
  }
}
```

Update the paths to match your installation directory.

## Usage Examples

### With Claude Desktop
- "Show me all blueprints in the system"
- "Create a virtual network called 'web-tier'"
- "Deploy the staging configuration"
- "Check for any anomalies in blueprint X"

### Streaming HTTP Client
The server exposes native FastMCP endpoints on `/mcp/*` with automatic SSE upgrades for streaming responses.

## Architecture

- **FastMCP Framework**: Native transport system with automatic SSE streaming
- **Config-based Authentication**: Simple stateless operation with direct Apstra API auth
- **Single Container**: HTTP server on port 8080 with streamable-http transport

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide with examples
- **[CLAUDE.md](CLAUDE.md)** - Technical implementation details and development guide

## Command Line Options

```bash
python3 apstra_mcp.py [OPTIONS]

Options:
  -t, --transport {stdio,streamable-http}  Transport mode (default: stdio)
  -f, --config-file FILE                   Apstra config JSON file
  -H, --host HOST                          HTTP host (default: 127.0.0.1)  
  -p, --port PORT                          HTTP port (default: 8080)
```

## Troubleshooting

- **Authentication fails**: Check credentials and server connectivity
- **Tools not appearing**: Verify server startup in Claude Desktop logs
- **Transport errors**: Ensure FastMCP version compatibility
- **Docker issues**: Check `docker-compose logs`

## License

This project is provided as-is for educational and demonstration purposes.

---
**Blog Post**: [MCP for Datacenter Networks](https://medium.com/@vignitin/mcp-for-datacenter-networks-aa003de81256)