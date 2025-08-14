# Apstra MCP Server

A Model Context Protocol (MCP) server that provides tools for interacting with Juniper Apstra Fabric Manager APIs. Enables Claude and other MCP clients to manage datacenter network infrastructure through natural language commands.

## 🚀 Features

- **Blueprint Management**: Create, retrieve, and delete blueprint configurations
- **Infrastructure Queries**: Get rack, routing zone, and system information  
- **Network Provisioning**: Create virtual networks and remote gateways
- **Configuration Management**: Check deployment status and deploy configurations
- **Protocol Monitoring**: Monitor BGP and other protocol sessions
- **Anomaly Detection**: Retrieve and analyze blueprint anomalies

## 🏃‍♂️ Quick Start

### Local Usage (Claude Desktop)
```bash
# Create config file
cp apstra_config_sample.json apstra_config.json
# Edit with your Apstra server details

# Run with stdio transport
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

### Remote Deployment
```bash
# HTTP server
python3 apstra_mcp.py -t http -H 0.0.0.0 -p 8080 -f apstra_config.json

# Docker
docker-compose up -d
```

## 🔧 Installation

### Prerequisites
- Python 3.7+
- Access to Juniper Apstra server
- Valid Apstra credentials

### Dependencies
```bash
pip install fastmcp httpx
```

## 📋 Available Tools

### Authentication & Status (4 tools)
- `login()` - Create session (HTTP transport only)
- `logout()` - End session (HTTP transport only)
- `session_info()` - Show authentication status
- `health()` - Server health check

### Query Tools (10 tools)
- `get_bp()` - Get blueprint information
- `get_racks()` - Get rack information  
- `get_rz()` - Get routing zones
- `get_vn()` - Get virtual networks
- `get_system_info()` - Get system/device information
- `get_protocol_sessions()` - Get protocol sessions
- `get_anomalies()` - Get blueprint anomalies
- `get_remote_gw()` - Get remote gateways
- `get_diff_status()` - Get deployment diff status
- `get_templates()` - Get available templates

### Management Tools (2 tools)
- `deploy()` - Deploy configurations
- `delete_blueprint()` - Delete blueprints

### Create Tools (4 tools)
- `create_vn()` - Create virtual networks
- `create_remote_gw()` - Create remote gateways  
- `create_datacenter_blueprint()` - Create datacenter blueprints
- `create_freeform_blueprint()` - Create freeform blueprints

## 🔐 Authentication

### stdio Transport (Claude Desktop)
Uses config file credentials - simple and secure for local use.

### HTTP Transport (Remote/API)
Session-based authentication with real Apstra credentials:
1. Call `login()` with credentials → get session token
2. Use session token with any tool
3. All actions logged in Apstra with real user identity

**Example Implementation**: See the [Streamlit Chat App](https://github.com/vignitin/streamlit-chat-app) for a complete web-based interface that demonstrates HTTP transport usage with session authentication.

## 🐳 Docker Deployment

```bash
git clone <this-repo>
cd apstra-mcp-server
cp apstra_config_sample.json apstra_config.json
# Edit config with your Apstra details
docker-compose up -d
```

## 💡 Usage Examples

### With Claude Desktop
- "Show me all blueprints in the system"
- "Create a virtual network called 'web-tier'"
- "Deploy the staging configuration"
- "Check for any anomalies in blueprint X"

### HTTP API
```bash
# Login
curl -X POST http://server:8080/tools/call \
  -d '{"method":"tools/call","params":{"name":"login","arguments":{"username":"user@company.com","password":"password","server":"apstra.company.com"}}}'

# Use any tool with session token
curl -X POST http://server:8080/tools/call \
  -d '{"method":"tools/call","params":{"name":"get_bp","arguments":{"session_token":"your-token"}}}'
```

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Technical implementation details and development guide
- **[TESTING.md](TESTING.md)** - Test framework documentation
- **[claude_desktop_config_examples.json](claude_desktop_config_examples.json)** - Configuration examples

## 🔗 Related Projects

- **[Streamlit Chat App](https://github.com/vignitin/streamlit-chat-app)** - Web-based chat interface that integrates with this MCP server via HTTP transport

## 🛠️ Command Line Options

```bash
python3 apstra_mcp.py [OPTIONS]

Options:
  -t, --transport {stdio,http}    Transport mode (default: stdio)
  -f, --config-file FILE          Apstra config JSON file
  -H, --host HOST                 HTTP host (default: 127.0.0.1)  
  -p, --port PORT                 HTTP port (default: 8080)
```

## 🔍 Troubleshooting

- **Authentication fails**: Check credentials and server connectivity
- **Tools not appearing**: Verify server startup in Claude Desktop logs
- **Session expired**: Call `login()` again for new token
- **Docker issues**: Check `docker-compose logs`

## 📝 License

This project is provided as-is for educational and demonstration purposes.

---
**Blog Post**: [MCP for Datacenter Networks](https://medium.com/@vignitin/mcp-for-datacenter-networks-aa003de81256)