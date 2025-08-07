# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based MCP (Model Context Protocol) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. The server exposes datacenter network management capabilities through MCP tools.

## Architecture

The project consists of two main Python files:

### `apstra_mcp.py` - MCP Server Interface
- **FastMCP Server**: Built using the `fastmcp` framework
- **MCP Tool Definitions**: 17 MCP tools organized into logical groups
- **Parameter Validation**: Type hints and parameter validation for all tools

### `apstra_core.py` - Core Functionality
- **Authentication Layer**: Handles token-based authentication with Apstra server  
- **API Wrappers**: Core functions that wrap Apstra REST API endpoints
- **Error Handling**: Comprehensive error handling with proper exception propagation
- **JSON Response Formatting**: Consistent JSON formatting for all responses

### Tool Organization

**Query Tools (11 tools):**
- **Blueprint management**: Get blueprint information (`get_bp()`)
- **Node queries**: Get all nodes (`get_nodes()`) and specific node details (`get_node_id()`)
- **Infrastructure queries**: Get racks (`get_racks()`), routing zones (`get_rz()`)
- **Network queries**: Get virtual networks (`get_vn()`), remote gateways (`get_remote_gw()`)
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

**Basic Usage (No RBAC)**:
```bash
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

**With RBAC (Environment Variables)**:
```bash
# Set user-specific credentials
export APSTRA_USERNAME="john@company.com"
export APSTRA_PASSWORD="user_password"
export APSTRA_SERVER="apstra.company.com"
export APSTRA_PORT="443"

python3 apstra_mcp.py -t stdio
```

### Remote Deployment (SSE/HTTP transport)

```bash
# Start HTTP server with session-based authentication
python3 apstra_mcp.py -t sse -H 0.0.0.0 -p 8080 -f apstra_config.json
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Configuration

Before running, create a configuration file (see `apstra_config_sample.json` for reference):
- `aos_server`: IP address or hostname of the Apstra server
- `aos_port`: Port number for the Apstra server (optional, defaults to 443)
- `username`: Apstra username for authentication  
- `password`: Apstra password for authentication

**Flexible Port Configuration Options:**
1. **Separate server and port**: `"aos_server": "hostname", "aos_port": "8443"`
2. **Combined format**: `"aos_server": "hostname:8443"`  
3. **Default HTTPS**: `"aos_server": "hostname"` (uses port 443)

## Claude Desktop Integration

### Basic Integration (No RBAC)
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

### RBAC Integration (Per-User Authentication)
```json
{
  "mcpServers": {
    "apstra": {
      "command": "python3",
      "args": ["/path/to/apstra_mcp.py", "-t", "stdio"],
      "env": {
        "APSTRA_USERNAME": "your-username@company.com",
        "APSTRA_PASSWORD": "your-password",
        "APSTRA_SERVER": "your-apstra-server.com",
        "APSTRA_PORT": "443"
      }
    }
  }
}
```

**Note**: Each user should have their own Claude Desktop configuration with their specific Apstra credentials for true RBAC enforcement.

See `claude_desktop_config_examples.json` for complete configuration examples.

## Dependencies

- `fastmcp`: MCP server framework
- `httpx`: HTTP client for API requests
- `sys`: Standard library for system operations

## Security Notes

- Server uses `verify=False` for HTTPS requests (bypasses SSL verification)
- Credentials are stored in JSON configuration files
- Consider using encrypted credential storage for production use

## Recent Improvements (Current Implementation)

### Dual Transport Architecture
- **stdio Transport**: Local usage with Claude Desktop, backward compatible
- **SSE/HTTP Transport**: Remote deployment with HTTP/server-sent events
- **Unified Codebase**: Single script handles both transport modes via `-t` flag
- **Docker Support**: Complete containerization following Juniper patterns

### RBAC Authentication System
- **stdio RBAC**: Environment variable-based per-user authentication
- **SSE RBAC**: Session-based authentication with credential validation
- **True RBAC**: Each user authenticates with actual Apstra credentials
- **Audit Trail**: All API calls logged in Apstra with real user identity

### Session Management (SSE Transport)
- **Authentication Flow**: Login → Session Token → Authenticated API Calls → Logout
- **Automatic Validation**: Token validation and expiration handling
- **Secure Storage**: User credentials stored securely on server side
- **Session Cleanup**: Automatic cleanup of expired sessions

### Authentication Tools
- **login()**: Authenticate with Apstra and create session (SSE only)
- **logout()**: Invalidate user session (SSE only)
- **session_info()**: Show current authentication mode and user information
- **health()**: Server health monitoring with session statistics

### Docker Deployment
- **Production Ready**: Dockerfile, docker-compose.yml, nginx reverse proxy
- **SSL Termination**: HTTPS support with certificate management
- **Health Monitoring**: Built-in health checks for container orchestration
- **Security**: Non-root user, restrictive permissions, security headers

## Development Best Practices

### Function Organization
- **GET functions first**: All query operations grouped together
- **Management functions**: Deploy and delete operations  
- **CREATE functions last**: All creation operations grouped at the end

### Error Handling Standards
- Use `response.raise_for_status()` for HTTP error detection
- Print errors to `sys.stderr` before returning error messages
- Return formatted error messages instead of raising exceptions to MCP clients

### API Response Handling
- Always use `json.dumps(response.json(), indent=2)` for consistent formatting
- Handle different API response structures (some use 'items', others use specific keys like 'nodes')
- For single object endpoints, return the object directly without array wrapping

### Parameter Design Principles
- Required parameters first in function signature
- Optional parameters with sensible defaults last
- Use None for truly optional parameters that should be excluded from payload
- Use default values for parameters that should always be included