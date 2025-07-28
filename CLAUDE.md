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

The server is designed to run with `uv` (though not currently available in this environment):

```bash
uv run --with fastmcp python3 apstra_mcp.py -f apstra_config.json
```

Alternative approach using pip:
```bash
pip install fastmcp httpx
python3 apstra_mcp.py -f apstra_config.json
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

The `claude_desktop_config.json` shows how this MCP server integrates with Claude Desktop. Note that the file paths need to be updated to match the actual locations of `apstra_mcp.py` and your config file.

## Dependencies

- `fastmcp`: MCP server framework
- `httpx`: HTTP client for API requests
- `sys`: Standard library for system operations

## Security Notes

- Server uses `verify=False` for HTTPS requests (bypasses SSL verification)
- Credentials are stored in JSON configuration files
- Consider using encrypted credential storage for production use

## Recent Improvements (Latest Session)

### New Tools Added
- **get_nodes()**: Get all nodes in a blueprint with proper API response handling
- **get_node_id()**: Get specific node details by ID
- **get_protocol_sessions()**: Monitor BGP and other protocol sessions

### Enhanced Remote Gateway Management
- **Flexible Parameters**: Made 5 parameters optional in `create_remote_gw()` with sensible defaults
- **Improved Usability**: Required parameters first, optional parameters with defaults
- **Smart Payload Construction**: Conditionally includes optional fields only when provided

### Code Organization Improvements
- **Logical Grouping**: Organized all 17 tools into Query, Management, and Create groups
- **Consistent Ordering**: Functions in `apstra_core.py` match the order in `apstra_mcp.py`
- **Better Documentation**: Enhanced docstrings with parameter descriptions and examples

### Error Handling Enhancements
- **Consistent Patterns**: All functions use `response.raise_for_status()` for HTTP error handling
- **Proper Exception Propagation**: Replaced `sys.exit()` calls with proper exception raising
- **JSON Response Handling**: Fixed API response structure handling for different endpoints

### Parameter Type Corrections
- **Data Type Alignment**: Fixed parameter types to match API requirements (int, str, list)
- **Optional Parameter Handling**: Proper default value assignment and conditional payload inclusion
- **API Response Structure**: Corrected response parsing for different endpoint patterns

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