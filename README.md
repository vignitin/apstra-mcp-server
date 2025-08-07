# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. This enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## 🚀 Features

### Core Capabilities
- **Blueprint Management**: Retrieve, create, and delete blueprint configurations
- **Infrastructure Queries**: Get rack, routing zone, and system information  
- **Network Provisioning**: Create virtual networks and remote gateways
- **Configuration Management**: Check deployment status and deploy configurations
- **Protocol Monitoring**: Monitor BGP and other protocol sessions
- **Enhanced Output Formatting**: Tables, icons, and structured layouts

### Architecture
- **Dual Transport Support**: stdio (Claude Desktop) + SSE/HTTP (remote deployment)
- **True RBAC**: Per-user authentication with Apstra credential pass-through
- **Docker Ready**: Complete containerization for production deployment
- **Session Management**: Secure token-based authentication for remote access
- **Backward Compatible**: Existing Claude Desktop integrations work unchanged

## 🏃‍♂️ Quick Start

### Local Usage (Claude Desktop)
```bash
# Basic usage (shared credentials)
python3 apstra_mcp.py -t stdio -f apstra_config.json

# RBAC usage (per-user credentials via environment)
export APSTRA_USERNAME="your-user@company.com"
export APSTRA_PASSWORD="your-password"
export APSTRA_SERVER="apstra.company.com"
python3 apstra_mcp.py -t stdio
```

### Remote Deployment
```bash
# HTTP server with session authentication
python3 apstra_mcp.py -t sse -H 0.0.0.0 -p 8080

# Docker deployment
docker-compose up -d
```

## 📋 Available Tools

### 🔍 Query Tools (11 tools)
- `get_bp()` - Get blueprint information
- `get_racks()` - Get rack information
- `get_rz()` - Get routing zones  
- `get_vn()` - Get virtual networks
- `get_system_info()` - Get system information
- `get_protocol_sessions()` - Get protocol sessions
- `get_anomalies()` - Get anomalies
- `get_remote_gw()` - Get remote gateways
- `get_diff_status()` - Get deployment diff status
- `get_templates()` - Get available templates

### ⚙️ Management Tools (2 tools)
- `deploy()` - Deploy configurations
- `delete_blueprint()` - Delete blueprints

### ✨ Create Tools (4 tools)
- `create_vn()` - Create virtual networks
- `create_remote_gw()` - Create remote gateways
- `create_datacenter_blueprint()` - Create datacenter blueprints
- `create_freeform_blueprint()` - Create freeform blueprints

### 🔐 Authentication Tools (SSE transport only)
- `login()` - Authenticate and create session
- `logout()` - Invalidate session
- `session_info()` - Get session/auth information
- `health()` - Server health monitoring

## 🔧 Installation & Setup

### Prerequisites
- Python 3.7+
- Access to Juniper Apstra server
- Valid Apstra credentials

### Install Dependencies
```bash
pip install fastmcp httpx
```

### Configuration
1. **Copy sample config**: `cp apstra_config_sample.json apstra_config.json`  
2. **Edit with your Apstra server details**
3. **For RBAC**: See configuration examples in [`claude_desktop_config_examples.json`](claude_desktop_config_examples.json)

## 📖 Documentation

| File | Purpose |
|------|---------|
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Complete deployment guide (Docker, HTTP, authentication) |
| **[claude_desktop_config_examples.json](claude_desktop_config_examples.json)** | Claude Desktop configuration examples for RBAC |
| **[CLAUDE.md](CLAUDE.md)** | Technical implementation details and development guide |

## 🔐 Authentication & RBAC

### stdio Transport (Claude Desktop)
- **No RBAC**: Uses global config file credentials
- **With RBAC**: Uses environment variables (`APSTRA_USERNAME`, `APSTRA_PASSWORD`, etc.)

### SSE Transport (Remote Deployment)  
- **Session-based**: Login with Apstra credentials → Get session token → Use for API calls
- **True RBAC**: Each user authenticates with their actual Apstra account
- **Audit Trail**: All actions logged in Apstra with real user identity

## 🐳 Docker Deployment

```bash
# Quick start
git clone <this-repo>
cd apstra-mcp-server
cp apstra_config_sample.json apstra_config.json
# Edit apstra_config.json with your settings
docker-compose up -d

# With HTTPS (SSL termination)
docker-compose --profile with-nginx up -d
```

## 🔧 Command Line Options

```bash
python3 apstra_mcp.py [OPTIONS]

Options:
  -t, --transport {stdio,sse}     Transport mode (default: stdio)
  -f, --config-file FILE          Apstra config JSON file (default: apstra_config.json)
  -H, --host HOST                 HTTP host (default: 127.0.0.1)  
  -p, --port PORT                 HTTP port (default: 8080)
```

## ⚡ Usage Examples

### Claude Desktop Commands
- "Show me all blueprints in the Apstra system"
- "Create a virtual network called 'web-tier' in blueprint X"
- "Deploy the staging configuration with description 'Production rollout'"
- "Get protocol session status for blueprint Y"

### HTTP API (after login)
```bash
# Login
curl -X POST http://server:8080/tools/call \
  -d '{"method":"tools/call","params":{"name":"login","arguments":{"apstra_username":"user@company.com","apstra_password":"password","apstra_server":"apstra.company.com"}}}'

# Get blueprints with session token  
curl -X POST http://server:8080/tools/call \
  -H "Authorization: Bearer <session_token>" \
  -d '{"method":"tools/call","params":{"name":"get_bp"}}'
```

## 🛠️ Troubleshooting

### Common Issues
- **Authentication fails**: Check credentials and Apstra server connectivity
- **Tools not appearing**: Verify server startup logs in Claude Desktop
- **Session expired**: Call `login` again to get new session token
- **Docker issues**: Check `docker-compose logs apstra-mcp-server`

### Debug Mode
```bash
# Run with debug output
python3 apstra_mcp.py -t sse -H 0.0.0.0 -p 8080

# Check authentication mode  
# In Claude Desktop or via API: use session_info tool
```

## 📝 License

This project is provided as-is for educational and demonstration purposes.

---

**Blog Post**: [MCP for Datacenter Networks](https://medium.com/@vignitin/mcp-for-datacenter-networks-aa003de81256)