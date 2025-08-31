# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based MCP (Model Context Protocol) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. The server exposes datacenter network management capabilities through MCP tools.

## Architecture

The project consists of two main Python files:

### `apstra_mcp.py` - MCP Server Interface
- **FastMCP Server**: Built using the `fastmcp` framework with native transport support
- **Transport Modes**: Supports stdio (secure) and streamable-http (with native FastMCP streaming)
- **MCP Tool Definitions**: 17 MCP tools organized into logical groups
- **Native FastMCP Transport**: Uses FastMCP's built-in HTTP and SSE capabilities

### `apstra_core.py` - Core Functionality
- **Authentication Layer**: Handles config-based authentication with Apstra server  
- **API Wrappers**: Core functions that wrap Apstra REST API endpoints
- **Error Handling**: Comprehensive error handling with proper exception propagation
- **JSON Response Formatting**: Consistent JSON formatting for all responses

### Tool Organization

**Health & Status Tools (2 tools):**
- **Health check**: Server status (`health()`)  
- **Formatting**: Formatting guidelines (`formatting_guidelines()`)

**Query Tools (9 tools):**
- **Blueprint management**: Get blueprint information (`get_bp()`)
- **Infrastructure queries**: Get racks (`get_racks()`), routing zones (`get_rz()`)
- **Network queries**: Get virtual networks (`get_vn()`), remote gateways (`get_remote_gw()`)
- **System queries**: Get systems/devices (`get_system_info()`)
- **Monitoring**: Get anomalies (`get_anomalies()`), protocol sessions (`get_protocol_sessions()`)
- **Configuration queries**: Check diff status (`get_diff_status()`), get templates (`get_templates()`)

**Management Tools (2 tools):**
- **Configuration management**: Deploy configurations (`deploy()`), delete blueprints (`delete_blueprint()`)

**Create Tools (4 tools):**
- **Network provisioning**: Create virtual networks (`create_vn()`), remote gateways (`create_remote_gw()`)
- **Blueprint creation**: Create datacenter (`create_datacenter_blueprint()`) and freeform blueprints (`create_freeform_blueprint()`)

### Key Components

- **Native FastMCP Transport**: Uses FastMCP's built-in streamable-http with automatic SSE upgrades
- **Config-based Authentication**: Simple authentication using configuration file credentials
- **Remote Gateway Management**: Comprehensive EVPN remote gateway creation with optional parameters
- **Flexible Configuration**: Support for various server:port configurations with 443 as default
- **Consistent Error Handling**: All functions use `response.raise_for_status()` and proper exception handling

## Running the Server

### Local Usage (stdio transport - Secure by default)

```bash
# For Claude Desktop - uses config file authentication
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

### Streaming HTTP Server (for network clients)

```bash
# Start streamable HTTP server with native FastMCP streaming
python3 apstra_mcp.py -t streamable-http -H 0.0.0.0 -p 8080 -f apstra_config.json
```

### Docker Deployment

```bash
# Start HTTP streaming server
docker-compose up -d
```

## Configuration

Before running, create a configuration file (see `apstra_config_sample.json` for reference):
- `server`: IP address or hostname of the Apstra server
- `port`: Port number for the Apstra server (optional, defaults to 443)
- `username`: Apstra username for authentication  
- `password`: Apstra password for authentication

**Flexible Port Configuration Options:**
1. **Separate server and port**: `"server": "hostname", "port": "8443"`
2. **Combined format**: `"server": "hostname:8443"`  
3. **Default HTTPS**: `"server": "hostname"` (uses port 443)

**Legacy Support:** The configuration also supports legacy field names (`aos_server`, `aos_port`) for backward compatibility.

## Claude Desktop Integration

```json
{
  "mcpServers": {
    "apstra": {
      "command": "python3",
      "args": ["/path/to/apstra_mcp.py", "-t", "stdio", "-f", "/path/to/apstra_config.json"]
    }
  }
}
```

**Security Note**: 
- **stdio transport** (default): Secure by default, no network exposure
- **streamable-http transport**: Network-accessible, use reverse proxy with authentication for production

## Dependencies

- `fastmcp`: MCP server framework
- `httpx`: HTTP client for API requests
- `sys`: Standard library for system operations

## Security Notes

- Server uses `verify=False` for HTTPS requests (bypasses SSL verification)
- Credentials are stored in JSON configuration files
- Consider using encrypted credential storage for production use

## Architecture Overview

### Transport Modes
- **stdio Transport**: Secure local communication for Claude Desktop integration
- **streamable-http Transport**: Network-accessible transport with native FastMCP streaming capabilities

### Authentication System
- **Configuration-based**: Uses credentials from JSON configuration file
- **Stateless Operation**: No session management or token persistence required
- **Apstra Integration**: Direct authentication against Apstra Fabric Manager

### Key Features
- **Native FastMCP Integration**: Leverages FastMCP framework's built-in transport capabilities
- **Automatic SSE Support**: Streaming responses with Server-Sent Events for real-time updates
- **Simplified Architecture**: Single server process with minimal dependencies
- **Container Support**: Docker deployment with configurable transport modes

## Development Best Practices

### Function Organization
- **GET functions first**: All query operations grouped together
- **Management functions**: Deploy and delete operations  
- **CREATE functions last**: All creation operations grouped at the end

### Error Handling Standards
- Use `response.raise_for_status()` for HTTP error detection
- Print errors to `sys.stderr` before returning error messages
- Return formatted error messages instead of raising exceptions to MCP clients

### Testing Commands

**stdio mode**:
```bash
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

**streamable-http mode**:
```bash
python3 apstra_mcp.py -t streamable-http -H 0.0.0.0 -p 8080 -f apstra_config.json
```

**Docker deployment**:
```bash
docker-compose up -d
```

### API Response Handling
- Always use `json.dumps(response.json(), indent=2)` for consistent formatting
- Handle different API response structures (some use 'items', others use specific keys like 'nodes')
- For single object endpoints, return the object directly without array wrapping

### Parameter Design Principles
- Required parameters first in function signature
- Optional parameters with sensible defaults last
- Use None for truly optional parameters that should be excluded from payload
- Use default values for parameters that should always be included