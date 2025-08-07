# Apstra MCP Server Deployment Guide

This guide covers deploying the Apstra MCP Server with dual transport support (stdio/SSE) and Docker containerization.

## Overview

The Apstra MCP Server now supports:
- **stdio transport**: For local usage with Claude Desktop
- **SSE/HTTP transport**: For remote deployment with session-based authentication
- **Docker containerization**: For scalable production deployment
- **True RBAC**: Each user authenticates with their own Apstra credentials

## Quick Start

### 1. Local Development (stdio transport)

```bash
# Traditional local usage
python3 apstra_mcp.py -t stdio -f apstra_config.json
```

### 2. Remote HTTP Server

```bash
# Start HTTP server with session auth
python3 apstra_mcp.py -t sse -H 0.0.0.0 -p 8080 -f apstra_config.json
```

### 3. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Configuration

### Apstra Configuration File

Create `apstra_config.json` (copy from `apstra_config_sample.json`):

```json
{
  "aos_server": "your-apstra-server.com",
  "aos_port": "443", 
  "username": "fallback_user",
  "password": "fallback_password"
}
```

**Note**: The fallback credentials are only used for stdio transport. Remote SSE transport uses per-user authentication.

## Authentication Flow (SSE Transport)

### 1. Login (Get Session Token)

```bash
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "login",
      "arguments": {
        "apstra_username": "john@company.com",
        "apstra_password": "user_password",
        "apstra_server": "apstra.company.com", 
        "apstra_port": "443"
      }
    }
  }'
```

**Response**:
```json
{
  "status": "success",
  "message": "Authentication successful", 
  "session_token": "abc123...",
  "expires_in": 3600
}
```

### 2. Use Session Token for API Calls

```bash
curl -X POST http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer abc123..." \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "get_bp"
    }
  }'
```

### 3. Session Management

```bash
# Check session info
curl -X POST http://localhost:8080/tools/call \
  -H "Authorization: Bearer abc123..." \
  -d '{
    "method": "tools/call", 
    "params": {
      "name": "session_info",
      "arguments": {"session_token": "abc123..."}
    }
  }'

# Logout
curl -X POST http://localhost:8080/tools/call \
  -H "Authorization: Bearer abc123..." \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "logout", 
      "arguments": {"session_token": "abc123..."}
    }
  }'
```

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed
- Valid `apstra_config.json` file

### Basic Deployment

```bash
# Clone repository
git clone <your-repo>
cd apstra-mcp-server

# Create configuration
cp apstra_config_sample.json apstra_config.json
# Edit apstra_config.json with your settings

# Build and start
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs apstra-mcp-server
```

### SSL/HTTPS Deployment

```bash
# Generate SSL certificates (example with self-signed)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Start with nginx proxy
docker-compose --profile with-nginx up -d
```

## Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8080/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {"name": "health"}
  }'
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Apstra MCP Server", 
  "transport": "sse",
  "active_sessions": 3,
  "timestamp": 1703123456.789
}
```

## RBAC Implementation

### How It Works

1. **User Authentication**: Each user provides their Apstra credentials
2. **Session Creation**: Server validates credentials against Apstra and creates session
3. **Request Authorization**: Each API call uses the user's Apstra credentials
4. **True RBAC**: Apstra enforces permissions based on the actual user account

### Benefits

- ✅ **Real RBAC**: Users see only what their Apstra account allows
- ✅ **Audit Trail**: All actions logged with actual user identity in Apstra
- ✅ **Secure**: User credentials stored securely on server side
- ✅ **Scalable**: Session-based approach supports multiple concurrent users

## Command Line Options

```bash
python3 apstra_mcp.py --help

Options:
  -f, --config-file   Path to Apstra config JSON (default: apstra_config.json)
  -t, --transport     Transport mode: stdio|sse (default: stdio)
  -H, --host          Host to bind for HTTP (default: 127.0.0.1) 
  -p, --port          Port to bind for HTTP (default: 8080)
```

## Environment Variables

```bash
# Docker environment variables
PYTHONUNBUFFERED=1    # Enable real-time logging
```

## Security Considerations

### Production Deployment

1. **Use HTTPS**: Deploy behind SSL termination (nginx example provided)
2. **Firewall**: Restrict access to trusted networks
3. **Monitoring**: Monitor active sessions and failed logins
4. **Session Timeout**: Default 1 hour, adjust based on needs
5. **Credential Storage**: Consider external secret management

### Network Security

```bash
# Example firewall rules (adjust for your environment)
sudo ufw allow from 10.0.0.0/8 to any port 8080
sudo ufw allow from 192.168.0.0/16 to any port 8080
```

## Troubleshooting

### Common Issues

**Authentication Fails**:
```bash
# Check Apstra connectivity
curl -k https://apstra-server:443/api/user/login

# Check server logs
docker-compose logs apstra-mcp-server
```

**Session Expired**:
- Sessions expire after 1 hour by default
- Call `/login` again to get new session token

**Connection Refused**:
- Verify server is running on correct host/port
- Check firewall rules
- For Docker: ensure port mapping is correct

### Debug Mode

```bash
# Run with debug output
python3 apstra_mcp.py -t sse -H 0.0.0.0 -p 8080

# Docker debug
docker-compose logs -f apstra-mcp-server
```

## Integration Examples

See the separate Streamlit MCP Client repository for a complete example of:
- Web-based chat interface
- MCP client implementation
- Session management
- Multi-user support

## Migration from v1

If migrating from the original stdio-only version:

1. **Backward Compatible**: Existing stdio usage unchanged
2. **New Features**: Add `-t sse` for HTTP transport
3. **Authentication**: New session-based auth for HTTP mode
4. **Docker**: New containerized deployment option

The server maintains full backward compatibility with existing Claude Desktop integrations while adding remote deployment capabilities.