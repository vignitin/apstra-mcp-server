# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based MCP (Model Context Protocol) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. The server exposes datacenter network management capabilities through MCP tools.

## Architecture

The project consists of three main Python files:

### `apstra_mcp.py` - MCP Server Interface
- **FastMCP Server**: Built using the `fastmcp` framework
- **Transport Modes**: Supports stdio (Claude Desktop) and HTTP (Streamlit/API)
- **MCP Tool Definitions**: 20 MCP tools organized into logical groups
- **Conditional Imports**: FastAPI only loaded for HTTP transport

### `apstra_core.py` - Core Functionality
- **Authentication Layer**: Handles token-based authentication with Apstra server  
- **API Wrappers**: Core functions that wrap Apstra REST API endpoints
- **Error Handling**: Comprehensive error handling with proper exception propagation
- **JSON Response Formatting**: Consistent JSON formatting for all responses

### `session_manager.py` - Session Management (HTTP only)
- **Session Authentication**: Validates credentials against Apstra
- **Token Management**: Secure session token generation and validation
- **Session Cleanup**: Automatic expiration of old sessions

### Tool Organization

**Authentication Tools (4 tools):**
- **Session management**: Login (`login()`), logout (`logout()`) - HTTP transport only
- **Status**: Session info (`session_info()`), health check (`health()`)

**Query Tools (12 tools):**
- **Blueprint management**: Get blueprint information (`get_bp()`)
- **Node queries**: Get all nodes (`get_nodes()`) and specific node details (`get_node_id()`)
- **Infrastructure queries**: Get racks (`get_racks()`), routing zones (`get_rz()`)
- **Network queries**: Get virtual networks (`get_vn()`), remote gateways (`get_remote_gw()`)
- **System queries**: Get systems/devices (`get_systems()`)
- **Monitoring**: Get anomalies (`get_anomalies()`), protocol sessions (`get_protocol_sessions()`)
- **Configuration queries**: Check diff status (`get_diff_status()`), get templates (`get_templates()`)

**Management Tools (2 tools):**
- **Configuration management**: Deploy configurations (`deploy()`), delete blueprints (`delete_blueprint()`)

**Create Tools (4 tools):**
- **Network provisioning**: Create virtual networks (`create_vn()`), remote gateways (`create_remote_gw()`)
- **Blueprint creation**: Create datacenter (`create_datacenter_blueprint()`) and freeform blueprints (`create_freeform_blueprint()`)

### Key Components

- **Authentication function** (`auth()`): Manages API token retrieval and headers with flexible port configuration
- **Remote Gateway Management**: Comprehensive EVPN remote gateway creation with optional parameters
- **Flexible Configuration**: Support for various server:port configurations with 443 as default
- **Consistent Error Handling**: All functions use `response.raise_for_status()` and proper exception handling

## Running the Server

### Local Usage (stdio transport)

```bash
# For Claude Desktop - uses config file authentication
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

### HTTP Server (for Streamlit/API clients)

```bash
# Start HTTP server with session-based authentication
python3 apstra_mcp.py -t http -H 0.0.0.0 -p 8080 -f apstra_config.json
```

### Docker Deployment

```bash
# Build and run with Docker Compose
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

**Note**: stdio transport uses simple config file authentication. For RBAC, use the HTTP transport mode.

## Dependencies

- `fastmcp`: MCP server framework
- `httpx`: HTTP client for API requests
- `sys`: Standard library for system operations

## Security Notes

- Server uses `verify=False` for HTTPS requests (bypasses SSL verification)
- Credentials are stored in JSON configuration files
- Consider using encrypted credential storage for production use

## Recent Improvements (Simplified Architecture)

### Transport Modes
- **stdio Transport**: Simple config-based auth for Claude Desktop
- **HTTP Transport**: Session-based RBAC for Streamlit/API clients
- **Removed SSE**: Eliminated unnecessary complexity

### Authentication System
- **stdio**: Uses config file credentials (no RBAC)
- **HTTP**: Session-based authentication with tokens
- **Session Manager**: Validates against actual Apstra credentials
- **Audit Trail**: All API calls logged in Apstra

### Key Simplifications
- **Single Server**: No more dual-server complexity
- **Conditional Imports**: FastAPI only loaded when needed
- **Removed Workarounds**: No more simple_http_api.py
- **Clean Docker**: Single container deployment

### Authentication Tools
- **login()**: Create session (HTTP only)
- **logout()**: Invalidate session (HTTP only)
- **session_info()**: Show current auth status
- **health()**: Server health check

### Docker Deployment
- **Single Container**: Just apstra-mcp-server
- **Health Checks**: Built-in monitoring
- **Optional Nginx**: For SSL termination

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

**stdio mode (Claude Desktop)**:
```bash
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

**HTTP mode (Streamlit)**:
```bash
python3 apstra_mcp.py -t http -H 0.0.0.0 -p 8080 -f apstra_config.json
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