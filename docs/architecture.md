# MCP Architecture Documentation

## Overview

The Model Context Protocol (MCP) architecture provides a structured approach to managing large language model (LLM) interactions with various capabilities and resources. This document details the architecture's components, communication patterns, and implementation details.

## Architecture Components

### MCP Host

The MCP Host is the environment containing all components of the MCP architecture:

1. **MCP Client**: Interfaces with the LLM and handles user interactions
2. **Server**: Contains the Session Manager and MCP Servers
3. **Resources**: External tools and capabilities

### MCP Client

The client component contains:

- **LLM Interface**: Communicates with the language model
- **Standard Input/Output (STDIO)**: Handles input/output operations
- **Server Sent Events (SSE)**: Receives notifications
- **Connection Lifecycle**: Initialize → Exchange → Terminate

### Session Manager

The Session Manager is responsible for:

- **Session Management**: Creating, tracking, and closing client sessions
- **Request Dispatching**: Routing requests to appropriate MCP servers
- **Notification Handling**: Managing SSE notifications to clients

### MCP Servers

Each server is specialized for specific capabilities:

1. **Resources Server** (Server 1): Manages access to resources
2. **Sampling Server** (Server 2): Handles sampling operations
3. **Tools Server** (Server 3): Provides tool execution capabilities
4. **Database Server** (Server 4): Manages database operations
5. **Internet Server** (Server 5): Handles internet access
6. **Roots Server** (Server 6): Provides root operations
7. **Prompts Server** (Server 7): Manages prompt templates

### External Resources

The MCP architecture can access various external resources:

- **Database**: Persistent storage
- **APIs**: External services
- **Internet**: Web access
- **Sampling**: Randomization capabilities
- **Tools**: Specialized functionality
- **Roots**: System-level operations
- **Prompts**: Template management

## Communication Flow

1. **Client to Session Manager**:
   - Client sends request to Session Manager
   - Session Manager tracks the request and client session

2. **Session Manager to MCP Server**:
   - Session Manager determines appropriate server based on request type
   - Request is forwarded to the selected MCP Server

3. **MCP Server Processing**:
   - Server processes the request using its capabilities
   - Server may access external resources as needed

4. **Response Flow**:
   - Server sends response back to Session Manager
   - Session Manager forwards response to Client

5. **Notifications**:
   - Asynchronous updates sent via SSE
   - Can be triggered at any point in the process

## Protocol Format

The MCP Protocol defines standardized message formats:

### Requests
```json
{
  "id": "req-12345",
  "timestamp": "2023-04-27T10:15:30Z",
  "type": "tool-execution",
  "payload": {
    "tool": "calculator",
    "operation": "add",
    "params": { "a": 5, "b": 3 }
  },
  "metadata": {
    "version": "1.0",
    "source": "mcp-client"
  }
}
```

### Responses
```json
{
  "id": "res-67890",
  "requestId": "req-12345",
  "timestamp": "2023-04-27T10:15:31Z",
  "status": "success",
  "data": {
    "result": 8
  },
  "metadata": {
    "version": "1.0",
    "source": "mcp-server-3"
  }
}
```

### Notifications
```json
{
  "id": "notif-24680",
  "timestamp": "2023-04-27T10:15:32Z",
  "type": "processing-complete",
  "data": {
    "requestId": "req-12345",
    "processingTime": "50ms"
  },
  "metadata": {
    "version": "1.0",
    "source": "mcp-server"
  }
}
```

## Implementation Considerations

### Scalability

- Each MCP Server can be independently scaled
- Session Manager acts as a load balancer
- Stateless design allows for horizontal scaling

### Security

- Controlled access to external resources
- Request validation at multiple levels
- Authentication and authorization mechanisms

### Performance

- Asynchronous processing for non-blocking operations
- Request prioritization capabilities
- Connection pooling for external resources

### Extensibility

- New MCP Servers can be added for additional capabilities
- Existing servers can be extended with new operations
- Protocol versioning for backward compatibility

# MCP API Reference

## MCP Client API

### Initialization

**Endpoint:** `POST /initialize`  
**Description:** Initialize the MCP client and create a session  
**Response:** Session information

```json
{
  "success": true,
  "sessionId": "session-uuid"
}
```

### Processing LLM Prompts

**Endpoint:** `POST /process`  
**Description:** Process a prompt through the LLM  
**Request Body:**

```json
{
  "prompt": "Your prompt text here"
}
```

**Response:** LLM response with any additional processing

```json
{
  "status": "success",
  "data": {
    "prompt": "Your prompt text here",
    "response": "LLM response text"
  }
}
```

### Tool Execution

**Endpoint:** `POST /tools`  
**Description:** Execute a tool operation  
**Request Body:**

```json
{
  "tool": "calculator",
  "operation": "add",
  "params": {
    "a": 5,
    "b": 3
  }
}
```

**Response:** Tool operation result

```json
{
  "status": "success",
  "data": {
    "result": 8
  }
}
```

### Termination

**Endpoint:** `POST /terminate`  
**Description:** Terminate the client and close the session  
**Response:** Success status

```json
{
  "success": true
}
```

### Status

**Endpoint:** `GET /status`  
**Description:** Get client status  
**Response:** Client status information

```json
{
  "clientId": "client-id",
  "state": "connected",
  "sessionId": "session-uuid",
  "llmStatus": {
    "initialized": true,
    "status": "connected"
  }
}
```

## Session Manager API

### Session Creation

**Endpoint:** `POST /sessions`  
**Description:** Create a new session  
**Request Body:**

```json
{
  "clientId": "client-id"
}
```

**Response:** Session information

```json
{
  "sessionId": "session-uuid"
}
```
### Session Information 

**Response:** Session details

```json
{
  "id": "session-uuid",
  "clientId": "client-id",
  "created": "2023-04-27T10:15:30Z",
  "lastActivity": "2023-04-27T10:15:30Z",
  "activeRequestCount": 0
}
```

### Session Closure

**Endpoint:** `DELETE /sessions/{sessionId}`  
**Description:** Close a session  
**Response:** Empty response with status code 204

### Request Processing

**Endpoint:** `POST /sessions/{sessionId}/requests`  
**Description:** Process a request through the appropriate MCP server  
**Request Body:** MCP Protocol request object  
**Response:** MCP Protocol response object

### SSE Notifications

**Endpoint:** `GET /events/{clientId}`  
**Description:** Subscribe to server-sent events  
**Response:** SSE stream with notifications

## MCP Server APIs

### Common Endpoints

Each MCP server implements these endpoints:

#### Process Request

**Endpoint:** `POST /process`  
**Description:** Process a request according to server capabilities  
**Request Body:** MCP Protocol request object  
**Response:** MCP Protocol response object

#### Health Check

**Endpoint:** `GET /health`  
**Description:** Check server health  
**Response:** Health status

```json
{
  "status": "healthy",
  "serverId": "1",
  "capabilities": ["resources"],
  "timestamp": "2023-04-27T10:15:30Z"
}
```

### Server-Specific Operations

Each server supports different request types and operations based on its capabilities.

# MCP Development Guide

## Getting Started

This guide provides instructions for developing with the MCP architecture.

## Setup

1. Clone the repository
2. Install dependencies
3. Run the setup script
4. Start the development environment

## Adding New Tools

### 1. Create Tool Implementation

Create a new tool class in the `servers/tools_server/tools/` directory:

```python
class NewTool:
    def operation1(self, param1, param2):
        # Implementation
        return result
    
    def operation2(self, param1):
        # Implementation
        return result
```

### 2. Register Tool in Server

Add the tool to the available tools in `servers/tools_server/app.py`:

```python
# Initialize tools
new_tool = NewTool()

# Available tools
tools = {
    'calculator': calculator,
    'textProcessor': text_processor,
    'dataTransformer': data_transformer,
    'newTool': new_tool
}
```

### 3. Update Client Interface

Add the tool definition to `client/static/client.js`:

```javascript
const tools = {
  // Existing tools...
  
  newTool: {
    operations: ['operation1', 'operation2'],
    params: {
      operation1: [
        { name: 'param1', type: 'text', label: 'Parameter 1' },
        { name: 'param2', type: 'number', label: 'Parameter 2' }
      ],
      operation2: [
        { name: 'param1', type: 'text', label: 'Parameter 1' }
      ]
    }
  }
};
```

## Adding New Servers

### 1. Create Server Directory

```bash
mkdir -p servers/new_server
```

### 2. Implement Server Files

Create the necessary files for the server:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- Implementation files

### 3. Update Docker Compose

Add the new server to `docker-compose.yml`:

```yaml
new-server:
  build:
    context: .
    dockerfile: servers/new_server/Dockerfile
  environment:
    - PORT=5008
    - SERVER_ID=8
    - CAPABILITIES=new-capability
  ports:
    - "5008:5008"
  volumes:
    - ./servers/new_server:/app
```

### 4. Update Session Manager

Add the server URL to the Session Manager configuration:

```python
server_urls = {
    # Existing servers...
    '8': os.environ.get('SERVER_8_URL', 'http://localhost:5008'),
}

# Update request type mapping
REQUEST_TYPE_MAPPING = {
    # Existing mappings...
    'new-capability-request': '8',
}
```

## Integrating with LLMs

Update the LLM interface implementation in `client/llm.py`:

```python
def process(self, prompt):
    """Process a prompt through the LLM."""
    if self.status == 'connected':
        # Implementation for specific LLM provider
        headers = {
            'Authorization': f"Bearer {self.api_key}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'model-name',
            'prompt': prompt,
            'max_tokens': 1000
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        result = response.json()
        
        return {'result': result['choices'][0]['text'].strip()}
```

## Best Practices

1. **Error Handling**
   - Use appropriate error classes from `common/error_handling.py`
   - Return clear error messages
   - Log errors with sufficient context

2. **Logging**
   - Use the `MCPLogger` for consistent logging
   - Include relevant details in log messages
   - Use appropriate log levels

3. **Protocol Compliance**
   - Follow the MCP Protocol format for all messages
   - Validate incoming requests
   - Include required metadata

4. **Testing**
   - Write unit tests for components
   - Test error handling
   - Validate protocol compliance

5. **Documentation**
   - Document new tools and capabilities
   - Update API reference for new endpoints
   - Provide examples for new features

# MCP Troubleshooting Guide

## Common Issues

### Connection Errors

**Symptom:** Client cannot connect to Session Manager or fails during initialization.

**Possible Causes:**
- Services not running
- Network configuration issues
- Incorrect environment variables

**Solutions:**
1. Check that all services are running:
   ```bash
   docker-compose ps
   ```
2. Verify network settings in Docker Compose
3. Check logs for connection errors:
   ```bash
   docker-compose logs session-manager
   ```

### Protocol Errors

**Symptom:** Requests fail with protocol validation errors.

**Possible Causes:**
- Incorrect message format
- Missing required fields
- Invalid field values

**Solutions:**
1. Validate message format against protocol specification
2. Check for missing required fields
3. Review field values for correctness

### Server Errors

**Symptom:** Requests to specific servers fail.

**Possible Causes:**
- Server not running
- Server capabilities mismatch
- Implementation errors

**Solutions:**
1. Check server status:
   ```bash
   curl http://localhost:5003/health
   ```
2. Verify server capabilities against request type
3. Check server logs for errors:
   ```bash
   docker-compose logs mcp-server-3
   ```

### Rate Limiting

**Symptom:** Internet requests fail with rate limit errors.

**Possible Causes:**
- Too many requests in a short period
- Excessive data transfer

**Solutions:**
1. Implement request throttling
2. Optimize data transfer
3. Adjust rate limit settings if possible

## Debugging Techniques

### Check Logs

Examine logs for error messages:

```bash
docker-compose logs -f mcp-client
docker-compose logs -f session-manager
docker-compose logs -f mcp-server-3
```

### Test Individual Components

Test components in isolation:

```bash
# Test session creation
curl -X POST http://localhost:5000/sessions \
  -H "Content-Type: application/json" \
  -d '{"clientId": "test-client"}'

# Test server health
curl http://localhost:5003/health
```

### Monitor Request Flow

1. Enable debug logging:
   ```bash
   export LOG_LEVEL=DEBUG
   ```
2. Trace a request through the system
3. Check logs for each step in the process

### Check Network Configuration

Verify network settings and connectivity:

```bash
# Check if servers are reachable
docker-compose exec mcp-client ping session-manager
docker-compose exec session-manager ping mcp-server-3
```

## Common Error Codes

- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication failed
- **404 Not Found**: Resource or endpoint not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error
- **504 Gateway Timeout**: Request processing timeout

## Getting Help

If you encounter issues not covered in this guide:

1. Check the full documentation
2. Review recent changes for potential regressions
3. Search for similar issues in the issue tracker
4. Create a detailed bug report with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Logs and error messages