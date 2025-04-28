# Model Context Protocol (MCP) - Python Implementation

A scalable and modular architecture for managing large language model (LLM) interactions using Python.

## Overview

The Model Context Protocol (MCP) architecture provides a structured approach to managing LLM interactions with various capabilities and resources. This Python implementation follows the architectural diagram, with clear separation between components:

- **MCP Client**: Interfaces with the LLM and provides a web UI for interaction
- **Session Manager**: Routes requests to appropriate servers and manages sessions
- **MCP Servers**: Specialized servers for different capabilities
  - Resources Server (Server 1)
  - Sampling Server (Server 2)
  - Tools Server (Server 3)
  - Database Server (Server 4)
  - Internet Server (Server 5)
  - Roots Server (Server 6)
  - Prompts Server (Server 7)
- **MCP Protocol**: Standardized communication format

## Features

- **Modular Architecture**: Clear separation of concerns between components
- **Standardized Communication**: Consistent message format across all components
- **Extensible Design**: Easily add new tools and capabilities
- **Web UI**: Browser-based interface for LLM interaction
- **Docker Integration**: Ready for containerized deployment
- **Asynchronous Notifications**: Real-time updates via Server-Sent Events (SSE)

## Getting Started

### Prerequisites

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- Flask and Requests libraries

### Quick Start

1. Clone this repository:
```bash
git clone https://github.com/your-username/python-mcp.git
cd python-mcp
```

2. Run the setup script to create all necessary files:
```bash
chmod +x setup-mcp.sh
./setup-mcp.sh
```

3. Start the system using Docker Compose:
```bash
docker-compose up --build
```

4. Access the MCP Client in your browser:
```
http://localhost:8080
```

### Running Without Docker

To run individual components for development:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the client:
```bash
python client/app.py
```

3. Run the session manager:
```bash
python session_manager/app.py
```

4. Run specific servers:
```bash
python servers/tools_server/app.py
```

## Architecture

### Components

#### MCP Client
- Flask web application
- LLM integration
- Web UI for interaction
- SSE client for notifications

#### Session Manager
- Request routing
- Session management
- SSE notifications handler

#### MCP Servers
1. **Resources Server**: Manages resource access
2. **Sampling Server**: Handles sampling operations
3. **Tools Server**: Provides tool execution capabilities
   - Calculator
   - Text Processor
   - Data Transformer
4. **Database Server**: Manages database operations
5. **Internet Server**: Handles internet access
6. **Roots Server**: Provides root operations
7. **Prompts Server**: Manages prompt templates

### Communication Flow

1. Client sends request to Session Manager
2. Session Manager routes request to appropriate MCP Server
3. MCP Server processes request, using external resources if needed
4. Response is sent back through Session Manager to Client
5. Notifications can be sent asynchronously via SSE

## Directory Structure

```# Python MCP Complete Directory Structure

```
python-mcp/
│
├── README.md                        # Project overview and documentation
├── setup-mcp.sh                     # Setup script to create all files
├── requirements.txt                 # Main project dependencies
├── docker-compose.yml               # Docker configuration for all services
│
├── common/                          # Shared utilities across all components
│   ├── __init__.py
│   ├── protocol.py                  # MCP Protocol implementation
│   ├── logging_utils.py             # Logging utilities
│   └── error_handling.py            # Error handling utilities
│
├── client/                          # MCP Client implementation
│   ├── Dockerfile                   # Client container configuration
│   ├── requirements.txt             # Client-specific dependencies
│   ├── app.py                       # Main client application
│   ├── llm.py                       # LLM interface
│   ├── stdio_handler.py             # Standard I/O handler
│   ├── sse_client.py                # SSE client for notifications
│   ├── templates/                   # HTML templates
│   │   └── index.html               # Main client UI template
│   └── static/                      # Static assets
│       ├── styles.css               # CSS styles
│       └── client.js                # Client-side JavaScript
│
├── session_manager/                 # Session Manager implementation
│   ├── Dockerfile                   # Session manager container config
│   ├── requirements.txt             # Session manager dependencies
│   ├── app.py                       # Main session manager application
│   ├── dispatcher.py                # Request dispatcher
│   ├── session.py                   # Session management
│   └── notifications.py             # SSE notifications handler
│
├── servers/                         # MCP Servers implementation
│   │
│   ├── resources_server/            # Server 1: Resources
│   │   ├── Dockerfile               # Server container configuration
│   │   ├── requirements.txt         # Server dependencies
│   │   ├── app.py                   # Main server application
│   │   └── resources.py             # Resources implementation
│   │
│   ├── sampling_server/             # Server 2: Sampling
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── sampling.py              # Sampling implementation
│   │
│   ├── tools_server/                # Server 3: Tools
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── tools/                   # Tool implementations
│   │       ├── __init__.py
│   │       ├── calculator.py        # Calculator tool
│   │       ├── text_processor.py    # Text processor tool
│   │       └── data_transformer.py  # Data transformer tool
│   │
│   ├── database_server/             # Server 4: Database
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── database.py              # Database connector
│   │
│   ├── internet_server/             # Server 5: Internet
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── internet.py              # Internet connector
│   │
│   ├── roots_server/                # Server 6: Roots
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── roots.py                 # Roots implementation
│   │
│   └── prompts_server/              # Server 7: Prompts
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py
│       └── prompts.py               # Prompts implementation
│
└── docs/                            # Additional documentation
    ├── architecture.md              # Architecture details
    ├── api_reference.md             # API documentation
    ├── development_guide.md         # Development guidelines
    └── troubleshooting.md           # Troubleshooting guide
```

## File Content Summary

### Common Files

- **protocol.py**: Implements the MCP Protocol with methods for creating and validating requests, responses, and notifications
- **logging_utils.py**: Provides consistent logging across all components
- **error_handling.py**: Defines error classes and handling utilities

### Client Files

- **app.py**: Main Flask application with REST API endpoints and web UI
- **llm.py**: Interface for integrating with language models
- **stdio_handler.py**: Handles standard input/output operations
- **sse_client.py**: Manages Server-Sent Events (SSE) for notifications
- **index.html**: Web interface for client interaction
- **client.js**: Client-side logic for the web interface

### Session Manager Files

- **app.py**: Main Flask application for session management and request routing
- **dispatcher.py**: Routes requests to appropriate MCP servers
- **session.py**: Manages client sessions
- **notifications.py**: Handles SSE notifications to clients

### Server Files

Each server has:
- **app.py**: Main Flask application with request processing logic
- **[capability].py**: Implementation of the server's specific capability

### Tools Server Files

- **calculator.py**: Implementation of calculator functions
- **text_processor.py**: Implementation of text processing functions
- **data_transformer.py**: Implementation of data transformation functions

## Docker Configuration

- **docker-compose.yml**: Configures all services (client, session manager, servers, database)
- **Dockerfile** (in each component): Specifies container configuration

## Documentation

- **README.md**: Project overview and getting started guide
- **architecture.md**: Detailed explanation of MCP architecture
- **api_reference.md**: Documentation of all API endpoints
- **development_guide.md**: Guidelines for development and extension
- **troubleshooting.md**: Common issues and solutions
```

## Extending the System

### Adding New Tools

1. Create a new tool class in `servers/tools_server/tools/`:
```python
class NewTool:
    def operation1(self, param1, param2):
        # Implementation
        return result
```

2. Add the tool to available tools in `servers/tools_server/app.py`
3. Update client interface in `client/static/client.js`

### Adding New Servers

1. Create a new server directory with implementation
2. Add the server to `docker-compose.yml`
3. Update the session manager to route requests to the new server

### Integrating with LLMs

Update the LLM interface implementation in `client/llm.py` to integrate with your preferred LLM provider (OpenAI, Anthropic, etc.).

## API Reference

### MCP Client API

- `POST /initialize`: Initialize the client and create a session
- `POST /process`: Process an LLM prompt
- `POST /tools`: Execute a tool operation
- `POST /terminate`: Terminate the client and close the session
- `GET /status`: Get client status

### MCP Protocol

Standard message formats for:
- **Requests**: `{id, timestamp, type, payload, metadata}`
- **Responses**: `{id, requestId, timestamp, status, data, metadata}`
- **Notifications**: `{id, timestamp, type, data, metadata}`

## Troubleshooting

Common issues and solutions:

1. **Connection Errors**:
   - Ensure all services are running
   - Check network settings in Docker Compose

2. **Protocol Errors**:
   - Ensure message formats follow the MCP Protocol
   - Check request/response validation

3. **Server Errors**:
   - Check server logs for error messages
   - Verify server capabilities match the request types

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This implementation is based on the Model Context Protocol (MCP) architecture diagram
- Uses Flask for web services and SSE for notifications