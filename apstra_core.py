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
    """Gets virtual networks information for a blueprint. 
    Also has information of the systems to which this virtual network is bound and on which VLAN ID"""
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

# Get connectivity templates
def get_ct(blueprint_id, server_url=None):
    """Gets the connectivity templates or endpoint policies for a blueprint.
    Also has information of the virtual network associated with this connectivity template
    Those policy IDs that are makred as "visible": true, will be used to assign interfaces to connectivity templates"""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/obj-policy-export'
        response = httpx.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

# Get application endpoints
def get_app_ep(blueprint_id, server_url=None):
    """Returns all possible application endpoints for connectivity templates in a blueprint."""
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/obj-policy-application-points'
        response = httpx.post(url, headers=headers, verify=False)
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

# Helper function to get individual leaf IDs from redundancy groups
def get_individual_leafs_from_system_ids(blueprint_id, system_ids, server_url=None):
    """
    Expand system IDs to individual leaf IDs for SVI IPs.
    
    For redundancy groups (leaf pairs), returns the individual leaf IDs.
    For single leafs, returns the same leaf ID.
    
    Args:
        blueprint_id: Blueprint ID
        system_ids: List of system IDs (may include redundancy groups)
        server_url: Optional server URL override
        
    Returns:
        List of individual leaf system IDs
    """
    try:
        # Get system information to build the mapping
        system_info_json = get_system_info(blueprint_id, server_url)
        system_info = json.loads(system_info_json)
        
        individual_leafs = []
        
        for system_id in system_ids:
            # Check if this system_id is a redundancy group
            is_redundancy_group = False
            
            for system in system_info['data']:
                if system['id'] == system_id and system['role'] == 'redundancy_group':
                    is_redundancy_group = True
                    break
            
            if is_redundancy_group:
                # Find all individual leafs that belong to this redundancy group
                for system in system_info['data']:
                    if (system['role'] == 'leaf' and 
                        system.get('redundancy_group_id') == system_id):
                        individual_leafs.append(system['id'])
            else:
                # Single leaf or already individual leaf
                individual_leafs.append(system_id)
        
        logger.info(f"Expanded system_ids {system_ids} to individual leafs: {individual_leafs}")
        return individual_leafs
        
    except Exception as e:
        logger.error(f"Failed to expand system IDs to individual leafs: {e}")
        # Fallback: return original system_ids
        return system_ids

# Normalization helper functions for layered architecture
def normalize_to_string_list(value):
    """Convert various inputs to list of strings"""
    if value is None or value == "":
        return None
    
    if isinstance(value, str):
        # Handle JSON array: '["sys1", "sys2"]'
        if value.strip().startswith('[') and value.strip().endswith(']'):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON array: {value}")
        # Handle single value: "sys1"
        return [value.strip()]
    
    if isinstance(value, list):
        return value
    
    raise ValueError(f"Invalid type for string list: {type(value)}")

def normalize_to_int_list(value, target_length):
    """Convert various inputs to list of integers"""
    if value is None or value == "":
        return None
    
    if isinstance(value, str):
        # Handle JSON array: "[300, 301]"
        if value.strip().startswith('[') and value.strip().endswith(']'):
            try:
                int_list = json.loads(value)
                return [int(x) for x in int_list]
            except (json.JSONDecodeError, ValueError):
                raise ValueError(f"Invalid JSON integer array: {value}")
        # Handle single value: "300" -> [300, 300, ...] (applied to all systems)
        try:
            single_int = int(value.strip())
            return [single_int] * target_length
        except ValueError:
            raise ValueError(f"Invalid integer: {value}")
    
    if isinstance(value, int):
        return [value] * target_length
    
    if isinstance(value, list):
        return [int(x) for x in value]
    
    raise ValueError(f"Invalid type for int list: {type(value)}")

def normalize_to_nested_list(value, target_length):
    """Convert various inputs to list of string lists"""
    if value is None or value == "":
        return [[] for _ in range(target_length)]  # Default empty lists
    
    if isinstance(value, str):
        # Handle nested JSON: '[["node1"], ["node2", "node3"]]'
        if value.strip().startswith('['):
            try:
                parsed = json.loads(value)
                if all(isinstance(item, list) for item in parsed):
                    return parsed  # Already nested
                else:
                    # Single list: '["node1", "node2"]' -> apply to all bindings
                    return [parsed] * target_length
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON for nested list: {value}")
        # Handle single value: "node1" -> [["node1"], ["node1"], ...]
        return [[value.strip()]] * target_length
    
    if isinstance(value, list):
        if len(value) > 0 and isinstance(value[0], list):
            return value  # Already nested
        else:
            return [value] * target_length  # Apply to all bindings
    
    return [[] for _ in range(target_length)]

# Create virtual networks
def create_vn(blueprint_id, security_zone_id, vn_name, virtual_gateway_ipv4, ipv4_subnet,
              system_ids=None, vlan_ids=None, access_switch_node_ids=None,
              svi_ips=None, vn_type="vxlan", ipv4_enabled=True, 
              dhcp_service="dhcpServiceDisabled", virtual_gateway_ipv4_enabled=True,
              create_policy_tagged=None, virtual_gateway_ipv6_enabled=False, ipv6_enabled=False,
              server_url=None):
    """Creates a virtual network using the virtual-networks-batch API endpoint
    
    Args:
        blueprint_id: The blueprint ID where the VN will be created (MANDATORY)
        security_zone_id: The security zone (routing zone) ID for the VN (MANDATORY)
        vn_name: The name/label for the virtual network (MANDATORY)
        virtual_gateway_ipv4: IPv4 address for the virtual gateway (MANDATORY, e.g., "10.1.1.1")
        ipv4_subnet: IPv4 subnet in CIDR format (MANDATORY, e.g., "10.1.1.0/24")
        system_ids: Optional system ID(s) to bind the VN to. Normalized from various inputs.
        vlan_ids: Optional VLAN ID(s) for binding. Normalized to integers.
        access_switch_node_ids: Optional access switch node IDs. Normalized to nested lists.
        svi_ips: Optional SVI IP configurations. Auto-generated from system_ids if not provided.
        vn_type: VN type (default: "vxlan"). Must be "vxlan" or "vlan".
        ipv4_enabled: Whether IPv4 is enabled (default: True)
        dhcp_service: DHCP service setting (default: "dhcpServiceDisabled")
        virtual_gateway_ipv4_enabled: Whether virtual gateway IPv4 is enabled (default: True)
        create_policy_tagged: Whether to create policy tagged (optional, no default)
        virtual_gateway_ipv6_enabled: Whether virtual gateway IPv6 is enabled (default: False)
        ipv6_enabled: Whether IPv6 is enabled (default: False)
        server_url: Optional server URL override
    
    Returns:
        JSON string containing the API response
        
    Raises:
        ValueError: If parameters are invalid or array lengths don't match
        
    Usage Examples:
        # Simple VN with gateway and subnet
        create_vn("bp-123", "zone-456", "my_vn", "10.1.1.1", "10.1.1.0/24")
        
        # VN with redundancy group (leaf pair) - auto-expands to individual leafs
        create_vn("bp-123", "zone-456", "pair_vn", "10.1.1.1", "10.1.1.0/24",
                  system_ids=["uc3ZiG_yU15gKSzovg"], vlan_ids=300)
        # bound_to: [{"system_id": "uc3ZiG_yU15gKSzovg", "vlan_id": 300}] (leaf pair)
        # svi_ips: [{"system_id": "leaf1_id"}, {"system_id": "leaf2_id"}] (individual leafs)
        
        # VN with single leaf
        create_vn("bp-123", "zone-456", "single_vn", "10.1.1.1", "10.1.1.0/24",
                  system_ids=["QmQU4o84uk5_8t7IhQ"], vlan_ids=300)
        # bound_to: [{"system_id": "QmQU4o84uk5_8t7IhQ", "vlan_id": 300}] (same)
        # svi_ips: [{"system_id": "QmQU4o84uk5_8t7IhQ"}] (same)
        
        # VN with mixed redundancy groups and single leafs
        create_vn("bp-123", "zone-456", "mixed_vn", "10.1.1.1", "10.1.1.0/24",
                  system_ids=["uc3ZiG_yU15gKSzovg", "QmQU4o84uk5_8t7IhQ"], vlan_ids=300)
        # bound_to: uses provided system_ids as-is
        # svi_ips: auto-expands redundancy groups to individual leafs
    
    Automatic Leaf Expansion:
        The function automatically handles the difference between bound_to and svi_ips requirements:
        - bound_to: Uses system_ids as provided (leaf pairs, single leafs)
        - svi_ips: Auto-expands redundancy groups to individual physical leaf IDs
        - Uses get_system_info() to query blueprint topology and build mapping
    """
    try:
        headers, server = auth(server_url)
        # Use the correct batch endpoint with async=full
        url = f'https://{server}/api/blueprints/{blueprint_id}/virtual-networks-batch?async=full'
        
        # Validate vn_type parameter
        if vn_type not in ["vxlan", "vlan"]:
            raise ValueError("vn_type must be either 'vxlan' or 'vlan'")
        
        # Normalize system_ids using helper function
        normalized_system_ids = normalize_to_string_list(system_ids) if system_ids is not None else None
        
        # Normalize vlan_ids and access_switch_node_ids
        if normalized_system_ids:
            target_length = len(normalized_system_ids)
            normalized_vlan_ids = normalize_to_int_list(vlan_ids, target_length) if vlan_ids is not None else None
            normalized_access_switches = normalize_to_nested_list(access_switch_node_ids, target_length)
        else:
            normalized_vlan_ids = None
            normalized_access_switches = None
        
        # Build bound_to list if system_ids provided
        bound_to = []
        if normalized_system_ids:
            for i, system_id in enumerate(normalized_system_ids):
                binding = {
                    "system_id": system_id,
                    "access_switch_node_ids": normalized_access_switches[i] if normalized_access_switches else []
                }
                if normalized_vlan_ids and i < len(normalized_vlan_ids):
                    binding["vlan_id"] = normalized_vlan_ids[i]
                bound_to.append(binding)
        
        # Auto-generate svi_ips if not provided but system_ids are
        if svi_ips is None and normalized_system_ids:
            # Get individual leaf IDs for SVI IPs (expand redundancy groups)
            individual_leaf_ids = get_individual_leafs_from_system_ids(blueprint_id, normalized_system_ids, server_url)
            
            svi_ips = []
            for leaf_id in individual_leaf_ids:
                svi_ips.append({
                    "system_id": leaf_id,
                    "ipv4_mode": "enabled" if ipv4_enabled else "disabled",
                    "ipv4_addr": None,
                    "ipv6_mode": "enabled" if ipv6_enabled else "disabled",
                    "ipv6_addr": None
                })
        elif svi_ips is None:
            svi_ips = []
        
        # Build the complete payload with virtual_networks array wrapper
        vn_config = {
            "label": vn_name,
            "vn_type": vn_type,
            "security_zone_id": security_zone_id,
            "virtual_gateway_ipv4": virtual_gateway_ipv4,
            "ipv4_subnet": ipv4_subnet,
            "svi_ips": svi_ips,
            "bound_to": bound_to,
            "virtual_gateway_ipv4_enabled": virtual_gateway_ipv4_enabled,
            "ipv4_enabled": ipv4_enabled,
            "dhcp_service": dhcp_service,
            "virtual_gateway_ipv6_enabled": virtual_gateway_ipv6_enabled,
            "ipv6_enabled": ipv6_enabled,
            # Required fields from working API call
            "vn_id": None,
            "vni_ids": [],
            "rt_policy": {"import_RTs": None, "export_RTs": None},
            "reserved_vlan_id": None,
            "ipv6_subnet": None,
            "virtual_gateway_ipv6": None
        }
        
        # Add create_policy_tagged only if provided (no default)
        if create_policy_tagged is not None:
            vn_config["create_policy_tagged"] = create_policy_tagged
        
        # Wrap in virtual_networks array as required by batch API
        payload = {
            "virtual_networks": [vn_config]
        }
        
        data = json.dumps(payload)
        logger.info(f"Sending payload to {url}: {data}")
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

# Apply connectivity template policies to application endpoints
def apply_ct_policies(blueprint_id, application_points, server_url=None):
    """Apply connectivity template policies to application endpoints using batch policy API
    
    Args:
        blueprint_id: The blueprint ID where policies will be applied (MANDATORY)
        application_points: Application points configuration. Can be:
                           - JSON string: '[{"id": "interface_id", "policies": [{"policy": "policy_id", "used": true}]}]'
                           - List of dicts: [{"id": "interface_id", "policies": [{"policy": "policy_id", "used": true}]}]
                           - Single dict: {"id": "interface_id", "policies": [{"policy": "policy_id", "used": true}]}
        server_url: Optional server URL override
    
    Returns:
        JSON string containing the API response
        
    Notes:
        - Uses obj-policy-batch-apply API endpoint with async=full and PATCH method
        - Each application point must have "id" (interface ID) and "policies" array
        - Each policy must have "policy" (policy ID) and "used" (boolean)
        - Set "used": true to apply policy, "used": false to remove policy
        - API endpoint: PATCH /api/blueprints/{blueprint_id}/obj-policy-batch-apply?async=full
        
    Example application_points:
        [
            {
                "id": "BfkK4q--O8CrlnBaPA",
                "policies": [
                    {
                        "policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d",
                        "used": true
                    }
                ]
            },
            {
                "id": "xVZXowwsRXVswg29xQ", 
                "policies": [
                    {
                        "policy": "46f3f09b-3645-4d2a-8cc3-624e7e46ef8d",
                        "used": false
                    }
                ]
            }
        ]
    """
    try:
        headers, server = auth(server_url)
        url = f'https://{server}/api/blueprints/{blueprint_id}/obj-policy-batch-apply?async=full'
        
        # Normalize application_points to list of dicts
        if isinstance(application_points, str):
            try:
                # Try to parse as JSON
                normalized_points = json.loads(application_points)
            except json.JSONDecodeError:
                raise ValueError("application_points string must be valid JSON")
        elif isinstance(application_points, dict):
            # Single dict, convert to list
            normalized_points = [application_points]
        elif isinstance(application_points, list):
            normalized_points = application_points
        else:
            raise ValueError("application_points must be a string, dict, or list")
        
        # Validate structure
        if not isinstance(normalized_points, list):
            raise ValueError("application_points must be a list after normalization")
            
        for point in normalized_points:
            if not isinstance(point, dict):
                raise ValueError("Each application point must be a dictionary")
            if "id" not in point:
                raise ValueError("Each application point must have an 'id' field")
            if "policies" not in point or not isinstance(point["policies"], list):
                raise ValueError("Each application point must have a 'policies' list")
            for policy in point["policies"]:
                if not isinstance(policy, dict):
                    raise ValueError("Each policy must be a dictionary")
                if "policy" not in policy or "used" not in policy:
                    raise ValueError("Each policy must have 'policy' and 'used' fields")
                if not isinstance(policy["used"], bool):
                    raise ValueError("Policy 'used' field must be a boolean")
        
        # Create the payload
        payload = {
            "application_points": normalized_points
        }
        
        # Convert to JSON string
        data = json.dumps(payload)
        
        logger.info(f"Applying connectivity template policies to {len(normalized_points)} application point(s)")
        
        response = httpx.patch(url, data=data, headers=headers, verify=False, timeout=30.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
        
    except Exception as e:
        error_msg = f"An unexpected error occurred: {e}"
        logger.error(error_msg)
        return error_msg

