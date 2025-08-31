# Deployment Guide

## Quick Start

### 1. Clone and Configure
```bash
git clone <this-repo>
cd apstra-mcp-server
cp apstra_config_sample.json apstra_config.json
# Edit apstra_config.json with your Apstra server details
```

### 2. Deploy with Docker
```bash
# Build and run the HTTP streaming server
docker-compose up -d
```

### 3. Verify Deployment
```bash
# Check container status
docker ps

# Test the endpoint
curl -H "Accept: text/event-stream" http://localhost:8080/mcp
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| HTTP API | `http://localhost:8080/mcp` | FastMCP streamable-http server |
| Claude Desktop | Local via `uv` command | Uses stdio transport |

## Client Configuration

### Streamlit Chat App
- Server URL: `http://host.docker.internal:8080/mcp`
- Authentication: none

### Claude Desktop
Add to `~/.claude/claude_desktop_config.json`:
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
        "/path/to/apstra_mcp.py",
        "-f",
        "/path/to/apstra_config.json"
      ]
    }
  }
}
```

## Troubleshooting

### Container Issues
```bash
# Check logs
docker-compose logs -f apstra-mcp-streaming

# Restart service
docker-compose restart
```

### Common Problems
1. **Port conflicts**: Ensure port 8080 is available
2. **Config missing**: Verify `apstra_config.json` exists
3. **Connection errors**: Check Apstra server connectivity

## Production Considerations

- Use environment variables for sensitive configuration
- Configure proper logging and monitoring
- Set up automated backups of configuration
- Consider using a container orchestration platform for high availability