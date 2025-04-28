# Python MCP Implementation Guide

This guide walks you through implementing the Model Context Protocol (MCP) architecture using Python. The MCP architecture provides a structured approach to managing large language model interactions with various capabilities and resources.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Architecture Components](#architecture-components)
5. [Implementation Details](#implementation-details)
6. [Running the System](#running-the-system)
7. [Development and Extension](#development-and-extension)
8. [Troubleshooting](#troubleshooting)

## Overview

The Python implementation of the MCP architecture consists of several key components:

- **MCP Client**: Interfaces with the LLM and provides a web UI for interaction
- **Session Manager**: Routes requests to appropriate servers and manages sessions
- **MCP Servers**: Specialized servers handling different capabilities:
  - Resources Server (Server 1)
  - Sampling Server (Server 2)
  - Tools Server (Server 3)
  - Database Server (Server 4)
  - Internet Server (Server 5)
  - Roots Server (Server 6)
  - Prompts Server (Server 7)
- **Common Utilities**: Shared protocol, logging, and error handling

## Prerequisites

- **Python 3.9+**
- **Docker** and **Docker Compose** (for containerized deployment)
- **Flask** and **Requests** libraries
- Basic knowledge of REST APIs and web development

## Quick Start

1. **Download and run the setup script**:

```bash
# Create the setup script
cat > setup-mcp.sh << 'EOF'
#!/bin/bash
# Setup script content here (copy from the Python MCP Setup Script)
EOF

# Make it executable
chmod +x setup-mcp.sh

# Run the script
./setup-mcp.sh
```

2. **Navigate to the project directory**:

```bash
cd python-mcp
```

3. **Start the system using Docker Compose**:

```bash
docker-compose up --build
```

4. **Access the MCP Client**:
   - Open a web browser and navigate to `http://localhost:8080`

## Architecture Components

### MCP Protocol

The MCP Protocol defines standardized message formats for communication between components:

```python
class MCPProtocol:
    @staticmethod
    def create_request(type_name, payload, **options):
        # Create a request object
        ...
    
    @staticmethod
    def create_response(request_id, status, data, **options):
        # Create a response object
        ...
    
    @staticmethod
    def create_notification(type_name, data, **options):
        # Create a notification object
        ...
```

### MCP Client

The client component consists of:

1. **Flask Web Application**: Provides REST API and web interface
2. **LLM Interface**: Handles interaction with language models
3. **STDIO Handler**: Manages input/output operations
4. **SSE Client**: Receives server-sent events for notifications

Key functionality:
- Initialize client and create session
- Process LLM prompts
- Execute tools
- Manage connection lifecycle

### Session Manager

The session manager handles:

1. **Session Management**: Create, retrieve, and close sessions
2. **Request Dispatching**: Route requests to appropriate servers
3. **SSE Notifications**: Send event notifications to clients
4. **Session Cleanup**: Automatically clean up inactive sessions

### MCP Servers

Each server is responsible for specific capabilities:

1. **Resources Server**: Manages resource access
2. **Sampling Server**: Handles sampling operations
3. **Tools Server**: Provides tool execution capabilities
4. **Database Server**: Manages database operations
5. **Internet Server**: Handles internet access
6. **Roots Server**: Provides root operations
7. **Prompts Server**: Manages prompt templates

## Implementation Details

### Directory Structure

```
python-mcp/
├── docker-compose.yml
├── requirements.txt
├── client/
│   ├── app.py              # Main client application
│   ├── llm.py              # LLM interface
│   └── ...
├── session_manager/
│   ├── app.py              # Main session manager
│   ├── dispatcher.py       # Request dispatcher
│   └── ...
├── servers/
│   ├── resources_server/   # Server 1
│   ├── sampling_server/    # Server 2
│   ├── tools_server/       # Server 3 with calculator, text processor, etc.
│   └── ...
└── common/
    ├── protocol.py         # MCP Protocol implementation
    ├── logging_utils.py    # Logging utilities
    └── error_handling.py   # Error handling utilities
```

### Key Implementation Files

#### Common Protocol (common/protocol.py)

The protocol implementation ensures standardized communication:

```python
class MCPProtocol:
    @staticmethod
    def create_request(type_name, payload, **options):
        request_id = options.get('id', f"req-{uuid.uuid4()}")
        source = options.get('source', 'mcp-client')
        
        return {
            'id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type_name,
            'payload': payload,
            'metadata': {
                'version': '1.0',
                'source': source,
                **options.get('metadata', {})
            }
        }
```

#### Client Application (client/app.py)

The client provides a REST API for LLM interactions:

```python
@app.route('/process', methods=['POST'])
def process_prompt():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        # Process through LLM
        llm_result = llm.process(prompt)
        
        # Send result through MCP
        result = process_request('llm-response', {
            'prompt': prompt,
            'response': llm_result['result']
        })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### Session Manager (session_manager/app.py)

The session manager routes requests to appropriate servers:

```python
@app.route('/sessions/<session_id>/requests', methods=['POST'])
def handle_request(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    # Update session activity
    session = sessions[session_id]
    session['lastActivity'] = datetime.utcnow().isoformat()
    
    # Get request data and dispatch to server
    request_data = request.json
    response = dispatcher.dispatch(request_data)
    
    return jsonify(response)
```

#### Tools Server (servers/tools_server/app.py)

The tools server handles tool execution:

```python
@app.route('/process', methods=['POST'])
def process_request():
    request_data = request.json
    
    try:
        if request_data.get('type') == 'tool-execution':
            payload = request_data.get('payload', {})
            tool_name = payload.get('tool')
            operation = payload.get('operation')
            params = payload.get('params', {})
            
            # Execute the tool operation
            tool = tools[tool_name]
            method = getattr(tool, operation)
            result = method(**params)
            
            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result},
                source=f"mcp-server-{SERVER_ID}"
            )
            
            return jsonify(response)
    except Exception as e:
        # Error handling
```

## Running the System

### Using Docker Compose

The easiest way to run the complete system:

```bash
# Start all services
docker-compose up --build

# Start specific services
docker-compose up --build mcp-client session-manager tools-server

# Stop all services
docker-compose down
```

### Running Individual Components

For development, you can run each component separately:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the client
python client/app.py

# Run the session manager
python session_manager/app.py

# Run a specific server
python servers/tools_server/app.py
```

## Development and Extension

### Adding New Tools

To add a new tool to the tools server:

1. Create a new tool class in the `servers/tools_server/tools/` directory:

```python
# servers/tools_server/tools/new_tool.py
class NewTool:
    def operation1(self, param1, param2):
        # Implementation
        return result
    
    def operation2(self, param1):
        # Implementation
        return result
```

2. Import and add the tool to the available tools in `servers/tools_server/app.py`:

```python
from tools.new_tool import NewTool

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

3. Update the client interface to include the new tool (in `client/static/client.js`):

```javascript
const tools = {
  // Existing tools
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

### Adding New Servers

To add a new server to the architecture:

1. Create a new server directory and implementation
2. Add the server to `docker-compose.yml`
3. Update the session manager's request dispatcher to route requests to the new server

### Integrating with LLMs

To integrate with a specific LLM provider:

1. Update the LLM interface implementation in `client/llm.py`:

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
            'model': 'text-davinci-003',  # Example model name
            'prompt': prompt,
            'max_tokens': 1000
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        result = response.json()
        
        return {'result': result['choices'][0]['text'].strip()}
```

2. Set the LLM API credentials as environment variables:

```bash
export LLM_API_KEY=your_api_key
export LLM_API_URL=https://api.example.com/v1/completions
```

## Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Ensure all services are running
   - Check network settings in Docker Compose
   - Verify port configurations

2. **Protocol Errors**:
   - Ensure message formats follow the MCP Protocol
   - Check request/response validation

3. **Server Errors**:
   - Check server logs for error messages
   - Verify server capabilities match the request types

### Debugging Tips

1. **Enable Debug Logging**:
   ```bash
   export LOG_LEVEL=DEBUG
   ```

2. **Check Container Logs**:
   ```bash
   docker-compose logs mcp-client
   docker-compose logs session-manager
   ```

3. **Test Endpoints with curl**:
   ```bash
   # Create a session
   curl -X POST http://localhost:5000/sessions \
     -H "Content-Type: application/json" \
     -d '{"clientId": "test-client"}'
   ```

## Conclusion

This Python implementation of the MCP architecture provides a flexible and modular system for managing LLM interactions. By following the structured approach outlined in this guide, you can implement, extend, and customize the system to meet your specific requirements.

The architecture allows for:

- Clear separation of concerns between components
- Standardized communication through the MCP Protocol
- Extensibility through adding new tools and servers
- Scalability through containerized deployment

For support or questions, please refer to the documentation or reach out to the development team.