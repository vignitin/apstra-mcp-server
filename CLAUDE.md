# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based MCP (Model Context Protocol) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. The server exposes datacenter network management capabilities through MCP tools.

## Architecture

The project consists of a single Python file (`apstra_mcp.py`) that implements:

- **FastMCP Server**: Built using the `fastmcp` framework
- **Authentication Layer**: Handles token-based authentication with Apstra server
- **API Tools**: Provides MCP tools that wrap Apstra REST API endpoints
- **Network Operations**: Tools for managing blueprints, racks, routing zones, virtual networks, and deployments

### Key Components

- **Authentication function** (`auth()`): Manages API token retrieval and headers
- **Blueprint management**: Get blueprint information (`get_bp()`)
- **Infrastructure queries**: Get racks (`get_racks()`) and routing zones (`get_rz()`) 
- **Network provisioning**: Create virtual networks (`create_vn()`)
- **Configuration management**: Check diff status (`get_diff_status()`) and deploy configurations (`deploy()`)

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
- `username`: Apstra username for authentication  
- `password`: Apstra password for authentication

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