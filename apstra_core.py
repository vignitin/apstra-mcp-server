"""
Core Apstra functions without MCP decorators for testing and reuse
"""
import httpx
import sys
import json
import os
from logger_config import setup_logger

# Set up logger
logger = setup_logger(__name__, os.environ.get('LOG_LEVEL', 'INFO'))

# Helper function for formatting guidelines
def get_formatting_guidelines():
    """Returns comprehensive formatting guidelines for presenting network infrastructure data in tables with proper icons and structure."""
    return """
# OUTPUT FORMATTING GUIDELINES

When displaying network infrastructure information, always follow these formatting standards:

## Table Format for Device Information
Always present device/system information in well-structured tables with these standard columns:

### Device Overview Table
| Status | Device Name | IP Address | Loopback IP | ASN | Role | Model | OS Version |
|--------|-------------|------------|-------------|-----|------|-------|------------|
| ✅ | spine-01 | 192.168.1.10 | 10.0.0.1 | 65001 | Spine | QFX5200 | 21.4R1 |
| ❌ | leaf-02 | 192.168.1.22 | 10.0.0.22 | 65002 | Leaf | EX4650 | 20.4R3 |

### Protocol Sessions Table
| Status | Local Device | Remote Device | Session Type | State | Uptime | Routes Rx/Tx |
|--------|--------------|---------------|--------------|-------|--------|---------------|
| ✅ | spine-01 | leaf-01 | eBGP | Established | 2d 14h | 150/75 |
| ⚠️ | spine-02 | leaf-03 | eBGP | Connect | 0h 0m | 0/0 |

### Anomaly/Issues Table
| Severity | Device | Issue Type | Description | Duration | Actions |
|----------|--------|------------|-------------|----------|---------|
| 🔴 | leaf-01 | BGP | Session Down | 2h 15m | Check connectivity |
| 🟡 | spine-02 | Interface | High Utilization | 45m | Monitor traffic |

## Status Icons Guide
Use these icons consistently across all outputs:

### Health Status
- ✅ **Healthy/Good/Up/Active/Connected**
- ❌ **Critical/Failed/Down/Disconnected** 
- ⚠️ **Warning/Degraded/Flapping/Pending**
- 🔄 **In Progress/Syncing/Updating**
- ⏸️ **Paused/Suspended/Maintenance**
- ❓ **Unknown/Unmonitored**

### Severity Levels
- 🔴 **Critical** - Immediate attention required
- 🟡 **Warning** - Attention needed
- 🟢 **Info** - Informational only
- 🔵 **Debug** - Troubleshooting info

### Network Elements
- 🌐 **WAN/Internet** connections
- 🏢 **Datacenter/Campus** networks  
- 🔀 **Switch/Router** devices
- 💾 **Storage** systems
- 🖥️ **Servers/Compute** resources

## Summary Sections
Always include summary sections for complex data:

### 📊 **Summary**
- **Total Devices**: 24 (✅ 22 healthy, ❌ 2 issues)
- **BGP Sessions**: 48 (✅ 46 established, ⚠️ 2 connecting) 
- **Anomalies**: 3 (🔴 1 critical, 🟡 2 warnings)

## Data Organization Guidelines
- **Group related information** together (e.g., all spine switches, then leaf switches)
- **Sort by criticality** when showing issues (critical first, then warnings)
- **Use consistent column ordering** across similar tables
- **Include units** for metrics (Mbps, %, ms, etc.)
- **Show timestamps** in consistent format (YYYY-MM-DD HH:MM:SS or relative time)

## Response Structure
Structure all responses with:
1. **Quick Summary** with key metrics and status icons
2. **Detailed Tables** with comprehensive information  
3. **Notable Issues** highlighting problems requiring attention
4. **Recommendations** for next steps or actions needed

## ⚠️ CRITICAL: Tool Usage and Change Management
**NEVER make configuration changes, deployments, or commits without explicit user confirmation.**

### Prohibited Actions Without Confirmation:
- ❌ **DO NOT** use `deploy()` tool without explicit user approval
- ❌ **DO NOT** use `delete_blueprint()` tool without explicit user approval  
- ❌ **DO NOT** create any network objects (`create_vn()`, `create_remote_gw()`, etc.) without explicit user approval
- ❌ **DO NOT** make any changes to production infrastructure without explicit user approval

### Required User Confirmation Format:
Before executing any change operation, you MUST:
1. **Describe** the exact change you plan to make
2. **Show** the specific command/tool that will be executed
3. **Ask** for explicit confirmation: "Do you want me to proceed with this change? (yes/no)"
4. **Wait** for clear user approval before proceeding

### Example Interaction:
User: "Deploy the configuration"
Assistant: "I'm ready to deploy the configuration to blueprint 'prod-datacenter-01'. This will:
- Deploy staging version 5 with description 'Update routing policies'
- Apply changes to all devices in the blueprint
- This action cannot be easily undone

Command to be executed: `deploy(blueprint_id='prod-datacenter-01', description='Update routing policies', staging_version=5)`

Do you want me to proceed with this deployment? (yes/no)"

## 🔍 MANDATORY: Post-Change Verification
**ALWAYS verify the success of any change operation using appropriate query tools.**

### Required Verification Steps After Changes:
1. **After `deploy()`**: 
   - Use `get_diff_status()` to confirm deployment completed
   - Use `get_anomalies()` to check for any new issues
   - Use `get_protocol_sessions()` to verify BGP/protocol stability

2. **After `create_vn()`**:
   - Use `get_vn()` to confirm virtual network was created
   - Verify the VN appears with correct parameters

3. **After `create_remote_gw()`**:
   - Use `get_remote_gw()` to confirm gateway creation
   - Use `get_protocol_sessions()` to check BGP establishment

4. **After `delete_blueprint()`**:
   - Use `get_bp()` to confirm blueprint no longer exists
   - Verify the blueprint_id is not in the list

5. **After any blueprint creation**:
   - Use `get_bp()` to confirm new blueprint exists
   - Verify the blueprint has correct name and parameters

### Verification Response Format:
After executing any change, immediately report:
```
✅ Change Status: [Success/Failed]
📊 Verification Results:
- [Tool used]: [Key findings]
- [Tool used]: [Key findings]
⚠️ Issues Found: [Any anomalies or unexpected results]
```

### Example Verification:
```
✅ Change Status: Deployment successful
📊 Verification Results:
- get_diff_status(): No pending changes (staging_version: 5, active_version: 5)
- get_anomalies(): No new anomalies detected
- get_protocol_sessions(): All BGP sessions established (48/48)
⚠️ Issues Found: None
```

## 🚀 IMPORTANT: Post-Change Deployment Prompt
**After making any configuration changes that require deployment, ALWAYS ask the user if they want to deploy.**

### When to Prompt for Deployment:
After successfully completing any of these operations:
- ✅ Creating virtual networks (`create_vn()`)
- ✅ Creating remote gateways (`create_remote_gw()`)
- ✅ Making any blueprint modifications
- ✅ Any configuration changes that show pending in `get_diff_status()`

### Required Deployment Prompt Format:
```
📝 Configuration changes have been made successfully.

Current Status:
- Changes made: [Brief description of what was created/modified]
- Staging version: [X] (from get_diff_status)
- Pending changes: [Yes/No]

Would you like me to deploy these changes to make them active? 

⚠️ Note: Changes will not take effect on the network devices until deployed.

Reply with:
- "yes" or "deploy" to proceed with deployment
- "no" or "skip" to leave changes in staging
- "review" to see the pending changes first
```

### Example Post-Change Interaction:
```
User: "Create a virtual network called prod-web"
Assistant: [Creates the VN successfully]

✅ Virtual network 'prod-web' created successfully in routing zone 'default-rz'

📝 Configuration changes have been made successfully.

Current Status:
- Changes made: Created virtual network 'prod-web' 
- Staging version: 12
- Pending changes: Yes

Would you like me to deploy these changes to make them active?

⚠️ Note: Changes will not take effect on the network devices until deployed.

Reply with:
- "yes" or "deploy" to proceed with deployment
- "no" or "skip" to leave changes in staging
- "review" to see the pending changes first
```

### Deployment Workflow:
1. **If user says "yes"/"deploy"**: Follow the change confirmation process for deploy()
2. **If user says "no"/"skip"**: Acknowledge and remind about staging
3. **If user says "review"**: Use get_diff_status() to show pending changes

This formatting ensures consistent, scannable, and actionable network infrastructure information while maintaining strict change control, verification, and deployment workflows.
"""

# Modular guideline functions for targeted responses
def get_base_guidelines():
    """Returns base formatting guidelines with essential icons and structure."""
    return """
# OUTPUT FORMATTING GUIDELINES

## Status Icons Guide
- ✅ **Healthy/Good/Up/Active**
- ❌ **Critical/Failed/Down**
- ⚠️ **Warning/Degraded**
- 🔄 **In Progress/Syncing**
- ❓ **Unknown**

## Response Structure
1. **Quick Summary** with key metrics
2. **Detailed Information** as needed
3. **Notable Issues** if any exist
"""

def get_device_guidelines():
    """Returns device/system specific formatting guidelines."""
    return """
## Device Information Table Format
| Status | Device Name | IP Address | Role | Model | OS Version |
|--------|-------------|------------|------|-------|------------|
| ✅ | spine-01 | 192.168.1.10 | Spine | QFX5200 | 21.4R1 |

Include: ASN, Loopback IP, and other relevant device details as columns.
"""

def get_network_guidelines():
    """Returns network configuration formatting guidelines."""
    return """
## Network Configuration Display
- **Virtual Networks**: Show VN name, ID, routing zone, VNI
- **Routing Zones**: Display zone name, VRF, VNI range
- **Remote Gateways**: Show GW name, IP, ASN, status

Use tables for multiple items, structured JSON for single items.
"""

def get_status_guidelines():
    """Returns status and protocol session formatting guidelines."""
    return """
## Protocol Sessions Table
| Status | Local | Remote | Type | State | Uptime |
|--------|-------|--------|------|-------|--------|
| ✅ | spine-01 | leaf-01 | eBGP | Established | 2d 14h |

## Configuration Status
- Show active vs staging versions clearly
- Highlight pending changes
- Display deployment history if relevant
"""

def get_anomaly_guidelines():
    """Returns anomaly and issue reporting guidelines."""
    return """
## Anomaly Display Format
| Severity | Device | Issue | Duration | Impact |
|----------|--------|-------|----------|---------|
| 🔴 Critical | leaf-01 | BGP Down | 2h 15m | Traffic loss |
| 🟡 Warning | spine-02 | High CPU | 45m | Performance |

Severity Levels:
- 🔴 **Critical** - Immediate action required
- 🟡 **Warning** - Attention needed
- 🟢 **Info** - Informational only
"""

def get_change_mgmt_guidelines():
    """Returns change management and deployment guidelines."""
    return """
## ⚠️ CRITICAL: Change Management Requirements

**NEVER make changes without explicit user confirmation.**

Before ANY change operation:
1. **Describe** the exact change
2. **Show** the command to be executed
3. **Ask** "Do you want me to proceed? (yes/no)"
4. **Wait** for explicit approval

## Post-Change Actions
1. **Verify** the change succeeded
2. **Check** for any anomalies
3. **Ask** if user wants to deploy (if applicable)

Example prompt after changes:
"Configuration changes made. Would you like to deploy? (yes/no)"
"""

def get_auth_guidelines():
    """Returns authentication-specific formatting guidelines."""
    return """
## Authentication Response Format
- Show session status clearly
- Include expiration time if applicable
- Display transport mode (stdio/http)
- Indicate credential source
"""

def get_blueprint_guidelines():
    """Returns blueprint-specific formatting guidelines."""
    return """
## Blueprint Information Display
| Status | Name | ID | Design | Version |
|--------|------|----|---------|---------| 
| ✅ | prod-dc | uuid-123 | two_stage | v5 |

Include creation date, last modified, and node count when available.
"""

# Global configuration variables
server = ''
port = ''
username = ''
password = ''

# Load configuration from JSON file
def load_config(config_file=None):
    """
    Load Apstra configuration from JSON file.
    Args:
        config_file: Optional path to config file. Defaults to 'apstra_config.json'
    """
    if config_file is None:
        config_file = 'apstra_config.json'
    
    # If not absolute path, look in same directory as this script
    if not os.path.isabs(config_file):
        config_file = os.path.join(os.path.dirname(__file__), config_file)
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file}")
        logger.error(f"Please create a config file based on apstra_config_sample.json")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file: {config_file}")
        return {}

def initialize_config(config_file=None):
    """Initialize global configuration variables from specified config file"""
    global server, port, username, password
    config = load_config(config_file)
    # Support both generic and legacy field names for backward compatibility
    server = config.get('server') or config.get('aos_server', '')
    port = config.get('port') or config.get('aos_port', '')
    username = config.get('username', '')
    password = config.get('password', '')

# Load default configuration
initialize_config()

# Session-based credential storage for user sessions
_user_sessions = {}

# The authentication function using global config
def auth(server_url=None, user=None, passwd=None):
    """
    Authenticate with Apstra server using either provided credentials or global config.
    
    Args:
        server_url: Optional server URL override
        user: Optional username override  
        passwd: Optional password override
    
    Returns:
        Tuple of (headers, server) for API requests
    """
    # Use provided parameters or fall back to global config
    auth_user = user or username
    auth_pass = passwd or password
    server_override = None
    port_override = None
    
    # Handle server URL construction
    if server_url:
        server = server_url
    elif server_override:
        # Use server from user credentials
        if port_override:
            server = f"{server_override}:{port_override}"
        elif ':' in server_override:
            server = server_override
        else:
            server = f"{server_override}:443"
    else:
        # Use global config (fallback for backward compatibility)
        global_server = globals().get('server', '')
        global_port = globals().get('port', '')
        if ':' in global_server:
            server = global_server
        else:
            if global_port:
                server = f"{global_server}:{global_port}"
            else:
                server = f"{global_server}:443"
    try:
        url_login = f'https://{server}/api/user/login'
        headers_init = { 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        data = f'{{"username": "{auth_user}","password":"{auth_pass}"}}'
        response = httpx.post(url_login, data=data, headers=headers_init, verify=False)
        if response.status_code != 201:
            raise Exception(f'Authentication failed: HTTP {response.status_code} - {response.text}')
        auth_token = response.json()['token']
        headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
        return(headers, server)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise  # Re-raise the exception instead of returning None


# Get blueprints
def get_bp(server_url=None):
    """Gets blueprint information"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json()['items'], indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get racks
def get_racks(blueprint_id, server_url=None):
    """Gets rack information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/racks'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json()['items'], indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get routing zones
def get_rz(blueprint_id, server_url=None):
    """Gets routing zone information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/security-zones'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get virtual networks
def get_vn(blueprint_id, server_url=None):
    """Gets virtual networks information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get system info
def get_system_info(blueprint_id, server_url=None):
    """Gets information about systems inside the blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/experience/web/system-info'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Check staging version through diff-status
def get_diff_status(blueprint_id, server_url=None):
    """Gets the diff status for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/diff-status'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Deploy config
def deploy(blueprint_id, description, staging_version, server_url=None):
    """Deploys the config for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/deploy'
        data = f'{{"version": {staging_version},"description":"{description}"}}'
        response = httpx.put(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get templates
def get_templates(server_url=None):
    """Gets available templates for blueprint creation"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/design/templates'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg


# Delete blueprint
def delete_blueprint(blueprint_id, server_url=None):
    """Deletes a blueprint by ID"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}'
        response = httpx.delete(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.text if response.text else "Blueprint deleted successfully"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get anomalies
def get_anomalies(blueprint_id, server_url=None):
    """Gets anomalies information for a blueprint"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/anomalies'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get remote gateways
def get_remote_gw(blueprint_id, server_url=None):
    """Gets a list of all remote gateways within a blueprint, keyed by remote gateway node ID."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/remote_gateways'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get protocol sessions
def get_protocol_sessions(blueprint_id, server_url=None):
    """Return a list of all protocol sessions from the specified blueprint."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/protocol-sessions'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# # Get system info

# CREATE FUNCTIONS - All create operations grouped together

# Create virtual networks
def create_vn(blueprint_id, security_zone_id, vn_name, server_url=None):
    """Creates a virtual network in a given blueprint and routing zone"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks'
        data = f'{{"label": "{vn_name}","vn_type":"vxlan","security_zone_id":"{security_zone_id}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False, timeout=30.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Create remote gateways
def create_remote_gw(blueprint_id, gw_ip, gw_asn, gw_name, local_gw_nodes, evpn_route_types="all", password=None, keepalive_timer=10, evpn_interconnect_group_id=None, holdtime_timer=30, ttl=30, server_url=None):
    """Creates a remote gateway in a given blueprint. Remote EVPN Gateway is a logical function that you could instantiate anywhere and on any device. 
    It requires BGP support in general, L2VPN/EVPN AFI/SAFI specifically. To establish a BGP session with an EVPN gateway, IP connectivity, 
    as well as connectivity to TCP port 179 (IANA allocates BGP TCP ports), should be available."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/remote_gateways'
        payload = {
            "gw_name": gw_name,
            "gw_ip": gw_ip,
            "gw_asn": gw_asn,
            "evpn_route_types": evpn_route_types,
            "local_gw_nodes": local_gw_nodes if isinstance(local_gw_nodes, list) else [local_gw_nodes]
        }
        
        # Add optional parameters only if they are provided
        if password is not None:
            payload["password"] = password
        if evpn_interconnect_group_id is not None:
            payload["evpn_interconnect_group_id"] = evpn_interconnect_group_id
            
        # Add optional parameters with their default values
        payload["keepalive_timer"] = keepalive_timer
        payload["holdtime_timer"] = holdtime_timer
        payload["ttl"] = ttl
        data = json.dumps(payload)
        response = httpx.post(url, data=data, headers=headers, verify=False, timeout=30.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Create datacenter blueprint
def create_datacenter_blueprint(blueprint_name, template_id, server_url=None):
    """Creates a new datacenter blueprint with the specified name and template"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"two_stage_l3clos","init_type":"template_reference","template_id":"{template_id}","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False, timeout=30.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Create freeform blueprint
def create_freeform_blueprint(blueprint_name, server_url=None):
    """Creates a new freeform blueprint with the specified name"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints'
        data = f'{{"design":"freeform","init_type":"none","label":"{blueprint_name}"}}'
        response = httpx.post(url, data=data, headers=headers, verify=False, timeout=30.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

