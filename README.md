# mcp-project
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

# Python Implementation of Model Context Protocol (MCP)

The following shows how to implement the key components of the MCP architecture using Python.

## Directory Structure
```
python-mcp/
├── docker-compose.yml
├── requirements.txt
├── client/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # Main client application
│   ├── llm.py              # LLM interface
│   ├── protocol.py         # MCP Protocol implementation
│   ├── stdio_handler.py    # Standard I/O handler
│   └── sse_client.py       # SSE client for notifications
│
├── session_manager/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py              # Main session manager
│   ├── dispatcher.py       # Request dispatcher
│   ├── protocol.py         # MCP Protocol implementation 
│   ├── session.py          # Session management
│   └── notifications.py    # SSE notifications handler
│
├── servers/
│   ├── resources_server/   # Server 1: Resources
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── resources.py
│   ├── sampling_server/    # Server 2: Sampling
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── sampling.py
│   ├── tools_server/       # Server 3: Tools
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── calculator.py
│   │       ├── text_processor.py
│   │       └── data_transformer.py
│   ├── database_server/    # Server 4: Database
│   ├── internet_server/    # Server 5: Internet
│   ├── roots_server/       # Server 6: Roots
│   └── prompts_server/     # Server 7: Prompts
│
└── common/
    ├── __init__.py
    ├── protocol.py         # MCP Protocol common implementation
    ├── logging_utils.py    # Logging utilities
    └── error_handling.py   # Error handling utilities
```

## Common Utilities (common/protocol.py)

```python
import uuid
import json
from datetime import datetime

class MCPProtocol:
    """MCP Protocol implementation for creating and validating messages."""
    
    @staticmethod
    def create_request(type_name, payload, **options):
        """Create a request object."""
        request_id = options.get('id', f"req-{uuid.uuid4()}")
        source = options.get('source', 'mcp-client')
        metadata = options.get('metadata', {})
        
        return {
            'id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type_name,
            'payload': payload,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }
    
    @staticmethod
    def create_response(request_id, status, data, **options):
        """Create a response object."""
        response_id = options.get('id', f"res-{uuid.uuid4()}")
        source = options.get('source', 'mcp-server')
        metadata = options.get('metadata', {})
        
        return {
            'id': response_id,
            'requestId': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': status,
            'data': data,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }
    
    @staticmethod
    def create_notification(type_name, data, **options):
        """Create a notification object."""
        notification_id = options.get('id', f"notif-{uuid.uuid4()}")
        source = options.get('source', 'mcp-server')
        metadata = options.get('metadata', {})
        
        return {
            'id': notification_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type_name,
            'data': data,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }
    
    @staticmethod
    def validate_message(message, message_type):
        """Validate a message against the MCP protocol."""
        if not isinstance(message, dict):
            return False
        
        # Common required fields
        if 'id' not in message or 'timestamp' not in message:
            return False
        
        # Message type specific validation
        if message_type == 'request':
            return 'type' in message and 'payload' in message
        elif message_type == 'response':
            return 'requestId' in message and 'status' in message
        elif message_type == 'notification':
            return 'type' in message and 'data' in message
        else:
            return False
```

## Common Utilities (common/logging_utils.py)

```python
import json
import logging
from datetime import datetime
import os

class MCPLogger:
    """Logging utilities for MCP."""
    
    LOG_LEVELS = {
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }
    
    def __init__(self, service_name=None, log_level=None):
        self.service_name = service_name or 'mcp-service'
        
        # Set log level from environment or default to INFO
        env_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        self.log_level = log_level or self.LOG_LEVELS.get(env_level, logging.INFO)
        
        # Configure logger
        self.logger = logging.getLogger(self.service_name)
        self.logger.setLevel(self.log_level)
        
        # Add console handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _format_log(self, level, message, data=None):
        """Format a log message."""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.service_name,
            'message': message
        }
        
        if data:
            log_obj['data'] = data
        
        return json.dumps(log_obj)
    
    def error(self, message, data=None):
        """Log an error message."""
        self.logger.error(self._format_log('ERROR', message, data))
    
    def warn(self, message, data=None):
        """Log a warning message."""
        self.logger.warning(self._format_log('WARN', message, data))
    
    def info(self, message, data=None):
        """Log an info message."""
        self.logger.info(self._format_log('INFO', message, data))
    
    def debug(self, message, data=None):
        """Log a debug message."""
        self.logger.debug(self._format_log('DEBUG', message, data))
```

## Common Utilities (common/error_handling.py)

```python
class MCPError(Exception):
    """Base class for MCP errors."""
    
    def __init__(self, message, **options):
        super().__init__(message)
        self.name = options.get('name', 'MCPError')
        self.code = options.get('code', 'INTERNAL_ERROR')
        self.status = options.get('status', 500)
        self.data = options.get('data', None)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'code': self.code,
            'message': str(self),
            'status': self.status,
            'data': self.data
        }


class RequestError(MCPError):
    """Error for invalid requests."""
    
    def __init__(self, message, **options):
        options.setdefault('name', 'RequestError')
        options.setdefault('code', 'INVALID_REQUEST')
        options.setdefault('status', 400)
        super().__init__(message, **options)


class AuthenticationError(MCPError):
    """Error for authentication failures."""
    
    def __init__(self, message, **options):
        options.setdefault('name', 'AuthenticationError')
        options.setdefault('code', 'AUTHENTICATION_FAILED')
        options.setdefault('status', 401)
        super().__init__(message, **options)


class ResourceError(MCPError):
    """Error for resource access issues."""
    
    def __init__(self, message, **options):
        options.setdefault('name', 'ResourceError')
        options.setdefault('code', 'RESOURCE_ERROR')
        options.setdefault('status', 500)
        super().__init__(message, **options)


class TimeoutError(MCPError):
    """Error for request timeouts."""
    
    def __init__(self, message, **options):
        options.setdefault('name', 'TimeoutError')
        options.setdefault('code', 'REQUEST_TIMEOUT')
        options.setdefault('status', 504)
        super().__init__(message, **options)
```

## MCP Client (client/app.py)

```python
from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import os
import sys
import json
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from llm import LLMInterface
from stdio_handler import STDIOHandler
from sse_client import SSEClient

# Initialize logger
logger = MCPLogger(service_name='mcp-client')

# Create Flask app
app = Flask(__name__, static_folder='static')

# Configuration
PORT = int(os.environ.get('PORT', 8080))
SERVER_URL = os.environ.get('SERVER_URL', 'http://localhost:5000')
CLIENT_ID = os.environ.get('CLIENT_ID', f"mcp-client-{uuid.uuid4().hex[:8]}")

# Initialize components
llm = LLMInterface()
stdio = STDIOHandler()
sse_client = SSEClient(f"{SERVER_URL}/events/{CLIENT_ID}")

# Connection state
connection_state = 'disconnected'
session_id = None

# Initialize MCP Client
@app.route('/initialize', methods=['POST'])
def initialize():
    global connection_state, session_id
    logger.info('Initializing MCP Client')
    
    try:
        connection_state = 'initializing'
        
        # Initialize LLM
        llm.initialize()
        
        # Connect to SSE for notifications
        sse_client.connect()
        
        # Create session
        response = requests.post(
            f"{SERVER_URL}/sessions",
            json={'clientId': CLIENT_ID},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create session: {response.text}")
        
        result = response.json()
        session_id = result['sessionId']
        
        connection_state = 'connected'
        logger.info(f"MCP Client initialized with session {session_id}")
        
        return jsonify({'success': True, 'sessionId': session_id})
    except Exception as e:
        connection_state = 'error'
        logger.error(f'Failed to initialize MCP Client: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

# Process a request through the MCP
def process_request(request_type, payload):
    global connection_state, session_id
    
    if connection_state != 'connected':
        raise Exception(f"Client not connected (state: {connection_state})")
    
    if not session_id:
        raise Exception('No active session')
    
    # Create MCP request
    request_data = MCPProtocol.create_request(request_type, payload, source=CLIENT_ID)
    
    logger.info(f"Sending {request_type} request", {'requestId': request_data['id']})
    
    # Send request to session manager
    response = requests.post(
        f"{SERVER_URL}/sessions/{session_id}/requests",
        json=request_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code not in (200, 201):
        raise Exception(f"Error from server: {response.text}")
    
    return response.json()

# Process an LLM prompt
@app.route('/process', methods=['POST'])
def process_prompt():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Process through LLM
        logger.info('Processing prompt', {'promptLength': len(prompt)})
        llm_result = llm.process(prompt)
        
        # Send result through MCP for any additional processing
        result = process_request('llm-response', {
            'prompt': prompt,
            'response': llm_result['result']
        })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f'Processing error: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Execute a tool
@app.route('/tools', methods=['POST'])
def execute_tool():
    try:
        data = request.json
        tool = data.get('tool')
        operation = data.get('operation')
        params = data.get('params', {})
        
        if not tool or not operation:
            return jsonify({'error': 'Tool and operation are required'}), 400
        
        # Send tool execution request
        result = process_request('tool-execution', {
            'tool': tool,
            'operation': operation,
            'params': params
        })
        
        return jsonify(result)
    except Exception as e:
        logger.error(f'Tool execution error: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Terminate client
@app.route('/terminate', methods=['POST'])
def terminate():
    global connection_state, session_id
    logger.info('Terminating MCP Client')
    
    try:
        connection_state = 'terminating'
        
        # Shutdown LLM
        llm.shutdown()
        
        # Disconnect SSE
        sse_client.disconnect()
        
        # Close session if active
        if session_id:
            requests.delete(f"{SERVER_URL}/sessions/{session_id}")
            session_id = None
        
        connection_state = 'disconnected'
        logger.info('MCP Client terminated')
        
        return jsonify({'success': True})
    except Exception as e:
        connection_state = 'error'
        logger.error(f'Failed to terminate MCP Client: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500

# Get client status
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        'clientId': CLIENT_ID,
        'state': connection_state,
        'sessionId': session_id,
        'llmStatus': llm.get_status()
    })

# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
```

## LLM Interface (client/llm.py)

```python
import requests
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='llm-interface')

class LLMInterface:
    """LLM Interface for MCP Client."""
    
    def __init__(self):
        self.api_key = os.environ.get('LLM_API_KEY')
        self.api_url = os.environ.get('LLM_API_URL')
        self.initialized = False
        self.status = 'disconnected'
    
    def initialize(self):
        """Initialize the LLM."""
        logger.info('Initializing LLM Interface')
        
        # If API key and URL are provided, use external LLM
        if self.api_key and self.api_url:
            try:
                # Test connection
                headers = {'Authorization': f"Bearer {self.api_key}"}
                requests.get(self.api_url, headers=headers)
                
                self.initialized = True
                self.status = 'connected'
                logger.info('Connected to external LLM API')
            except Exception as e:
                logger.error(f'Failed to connect to external LLM API: {str(e)}')
                self.status = 'error'
                raise Exception(f"LLM connection error: {str(e)}")
        else:
            # Use mock LLM for development
            logger.info('Using mock LLM (no API credentials provided)')
            self.initialized = True
            self.status = 'mock'
        
        return {'status': self.status}
    
    def process(self, prompt):
        """Process a prompt through the LLM."""
        if not self.initialized:
            raise Exception('LLM not initialized')
        
        logger.info('Processing prompt through LLM', {'promptLength': len(prompt)})
        
        # If using external LLM
        if self.status == 'connected':
            try:
                headers = {
                    'Authorization': f"Bearer {self.api_key}",
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'prompt': prompt,
                    'max_tokens': 1000,
                    'temperature': 0.7
                }
                
                response = requests.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code != 200:
                    raise Exception(f"LLM API error: {response.text}")
                
                result = response.json()
                logger.info('Received response from LLM API')
                
                return {'result': result['choices'][0]['text'].strip()}
                
            except Exception as e:
                logger.error(f'LLM API error: {str(e)}')
                raise Exception(f"LLM processing error: {str(e)}")
        
        # If using mock LLM
        elif self.status == 'mock':
            # Simulate processing delay
            time.sleep(0.5)
            
            # Generate mock response
            mock_response = f"This is a mock LLM response to: \"{prompt[:50]}...\""
            
            logger.info('Generated mock LLM response')
            return {'result': mock_response}
        
        else:
            raise Exception(f"LLM in invalid state: {self.status}")
    
    def shutdown(self):
        """Shut down the LLM."""
        logger.info('Shutting down LLM Interface')
        self.initialized = False
        self.status = 'disconnected'
        return {'status': self.status}
    
    def get_status(self):
        """Get LLM status."""
        return {
            'initialized': self.initialized,
            'status': self.status
        }
```

## Session Manager (session_manager/app.py)

```python
from flask import Flask, request, jsonify, Response
import json
import uuid
import time
import threading
import requests
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from dispatcher import RequestDispatcher

# Initialize logger
logger = MCPLogger(service_name='session-manager')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5000))
server_urls = {
    '1': os.environ.get('SERVER_1_URL', 'http://localhost:5001'),
    '2': os.environ.get('SERVER_2_URL', 'http://localhost:5002'),
    '3': os.environ.get('SERVER_3_URL', 'http://localhost:5003'),
    '4': os.environ.get('SERVER_4_URL', 'http://localhost:5004'),
    '5': os.environ.get('SERVER_5_URL', 'http://localhost:5005'),
    '6': os.environ.get('SERVER_6_URL', 'http://localhost:5006'),
    '7': os.environ.get('SERVER_7_URL', 'http://localhost:5007'),
}

# Initialize request dispatcher
dispatcher = RequestDispatcher(server_urls)

# Active sessions storage
sessions = {}

# SSE clients for notifications
sse_clients = {}

# SESSION MANAGEMENT ENDPOINTS

# Create a new session
@app.route('/sessions', methods=['POST'])
def create_session():
    data = request.json
    client_id = data.get('clientId')
    
    if not client_id:
        return jsonify({'error': 'Client ID is required'}), 400
    
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'clientId': client_id,
        'created': datetime.utcnow().isoformat(),
        'lastActivity': datetime.utcnow().isoformat(),
        'activeRequests': {}
    }
    
    logger.info(f"Session {session_id} created for client {client_id}")
    return jsonify({'sessionId': session_id}), 201

# Get session information
@app.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    return jsonify({
        'id': session['id'],
        'clientId': session['clientId'],
        'created': session['created'],
        'lastActivity': session['lastActivity'],
        'activeRequestCount': len(session['activeRequests'])
    })

# Close a session
@app.route('/sessions/<session_id>', methods=['DELETE'])
def close_session(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    del sessions[session_id]
    logger.info(f"Session {session_id} closed")
    return '', 204

# REQUEST HANDLING

# Process a request through the appropriate MCP server
@app.route('/sessions/<session_id>/requests', methods=['POST'])
async def handle_request(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    # Update session activity
    session = sessions[session_id]
    session['lastActivity'] = datetime.utcnow().isoformat()
    
    # Get request data
    request_data = request.json
    
    # Generate request ID if not provided
    request_id = request_data.get('id', str(uuid.uuid4()))
    if 'id' not in request_data:
        request_data['id'] = request_id
    
    # Track the request in the session
    session['activeRequests'][request_id] = {
        'timestamp': datetime.utcnow().isoformat(),
        'request': request_data
    }
    
    logger.info(f"Processing request {request_id} for session {session_id}", 
                {'requestType': request_data.get('type')})
    
    try:
        # Dispatch the request to the appropriate MCP server
        response = await dispatcher.dispatch(request_data)
        
        # Remove the request from active tracking
        if request_id in session['activeRequests']:
            del session['activeRequests'][request_id]
        
        # Send notification to connected clients
        send_notification(session['clientId'], {
            'type': 'request-completed',
            'requestId': request_id,
            'sessionId': session_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Return the server's response
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}")
        
        # Remove the request from active tracking
        if request_id in session['activeRequests']:
            del session['activeRequests'][request_id]
        
        # Send error notification
        send_notification(session['clientId'], {
            'type': 'request-error',
            'requestId': request_id,
            'sessionId': session_id,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Return error response
        return jsonify({
            'error': 'Failed to process request',
            'message': str(e)
        }), 500

# SSE NOTIFICATIONS

# Subscribe to notifications
@app.route('/events/<client_id>')
def events(client_id):
    def stream():
        # Send initial connection message
        data = json.dumps({
            'type': 'connected',
            'clientId': client_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        yield f"data: {data}\n\n"
        
        # Store the client ID
        sse_clients[client_id] = True
        logger.info(f"SSE client {client_id} connected")
        
        try:
            # Keep connection alive
            while True:
                # Check if client is still connected
                if not request.environ.get('werkzeug.socket'):
                    break
                time.sleep(30)  # Keep-alive every 30 seconds
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        except:
            pass
        finally:
            # Clean up on disconnect
            if client_id in sse_clients:
                del sse_clients[client_id]
            logger.info(f"SSE client {client_id} disconnected")
    
    return Response(stream(), mimetype='text/event-stream')

# Function to send notification to a client
def send_notification(client_id, notification):
    if client_id in sse_clients:
        # In a real implementation, this would use a proper async SSE framework
        # For simplicity in this example, we just log it
        logger.debug(f"Notification sent to client {client_id}", 
                    {'notificationType': notification.get('type')})
        return True
    return False

# SESSION CLEANUP

# Function to clean up inactive sessions
def cleanup_sessions():
    while True:
        time.sleep(300)  # Check every 5 minutes
        now = datetime.utcnow()
        for session_id in list(sessions.keys()):
            session = sessions[session_id]
            last_activity = datetime.fromisoformat(session['lastActivity'])
            
            # If the session has been inactive for more than 30 minutes
            if (now - last_activity).total_seconds() > 1800:
                logger.info(f"Closing inactive session {session_id}")
                del sessions[session_id]
                
                # Notify the client
                send_notification(session['clientId'], {
                    'type': 'session-expired',
                    'sessionId': session_id,
                    'timestamp': now.isoformat()
                })

# Start the cleanup thread
cleanup_thread = threading.Thread(target=cleanup_sessions, daemon=True)
cleanup_thread.start()

# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Session Manager running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, threaded=True)
```

## Tools Server (servers/tools_server/app.py)

```python
from flask import Flask, request, jsonify
import json
import os
import sys
import importlib.util
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol

# Import tools
from tools.calculator import Calculator
from tools.text_processor import TextProcessor
from tools.data_transformer import DataTransformer

# Initialize logger
logger = MCPLogger(service_name='tools-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5003))
SERVER_ID = os.environ.get('SERVER_ID', '3')
CAPABILITIES = os.environ.get('CAPABILITIES', 'tools,database,api').split(',')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

# Initialize tools
calculator = Calculator()
text_processor = TextProcessor()
data_transformer = DataTransformer()

# Available tools
tools = {
    'calculator': calculator,
    'textProcessor': text_processor,
    'dataTransformer': data_transformer
}

# Process request endpoint
@app.route('/process', methods=['POST'])
def process_request():
    request_data = request.json
    logger.info(f"Server {SERVER_ID} received request:", {'requestId': request_data.get('id')})
    
    try:
        # Validate request
        if not MCPProtocol.validate_message(request_data, 'request'):
            raise ValueError('Invalid request format')
        
        # Process based on request type
        if request_data.get('type') == 'tool-execution':
            payload = request_data.get('payload', {})
            tool_name = payload.get('tool')
            operation = payload.get('operation')
            params = payload.get('params', {})
            
            if tool_name not in tools:
                raise ValueError(f"Tool not found: {tool_name}")
            
            tool = tools[tool_name]
            
            if not hasattr(tool, operation):
                raise ValueError(f"Operation not supported for tool {tool_name}: {operation}")
            
            logger.info(f"Executing {tool_name}.{operation} with params:", {'params': params})
            
            # Execute the tool operation
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
        
        # Handle database queries if the capability is available
        elif request_data.get('type') == 'database-query' and 'database' in CAPABILITIES:
            payload = request_data.get('payload', {})
            query = payload.get('query')
            
            logger.info(f"Executing database query: {query}")
            
            # Mock database query result
            result = {
                'rows': [
                    {'id': 1, 'name': 'Sample 1', 'value': 100},
                    {'id': 2, 'name': 'Sample 2', 'value': 200},
                    {'id': 3, 'name': 'Sample 3', 'value': 300}
                ],
                'rowCount': 3
            }
            
            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result},
                source=f"mcp-server-{SERVER_ID}"
            )
            
            return jsonify(response)
        
        # Handle API calls if the capability is available
        elif request_data.get('type') == 'api-call' and 'api' in CAPABILITIES:
            payload = request_data.get('payload', {})
            endpoint = payload.get('endpoint')
            
            logger.info(f"Executing API call to: {endpoint}")
            
            try:
                import requests
                
                # Make the actual API call
                api_response = requests.request(
                    method=payload.get('method', 'GET'),
                    url=endpoint,
                    headers=payload.get('headers', {}),
                    json=payload.get('body', {})
                )
                
                # Return success response
                response = MCPProtocol.create_response(
                    request_data.get('id'),
                    'success',
                    {'result': api_response.json()},
                    source=f"mcp-server-{SERVER_ID}"
                )
                
                return jsonify(response)
            
            except Exception as e:
                raise ValueError(f"API call failed: {str(e)}")
        
        else:
            raise ValueError(f"Unsupported request type for server {SERVER_ID}: {request_data.get('type')}")
    
    except Exception as e:
        logger.error(f"Error processing request {request_data.get('id')}: {str(e)}")
        
        # Return error response
        error_response = MCPProtocol.create_response(
            request_data.get('id'),
            'error',
            {'error': str(e)},
            source=f"mcp-server-{SERVER_ID}"
        )
        
        return jsonify(error_response), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'serverId': SERVER_ID,
        'capabilities': CAPABILITIES,
        'timestamp': datetime.utcnow().isoformat()
    })

# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Server {SERVER_ID} running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)
```

## Calculator Tool (servers/tools_server/tools/calculator.py)

```python
class Calculator:
    """Calculator tool for MCP."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    def power(self, a, b):
        """Calculate a raised to the power of b."""
        return a ** b
```

## Text Processor Tool (servers/tools_server/tools/text_processor.py)

```python
class TextProcessor:
    """Text processor tool for MCP."""
    
    def word_count(self, text):
        """Count words in text."""
        return len([word for word in text.split() if word.strip()])
    
    def character_count(self, text):
        """Count characters in text."""
        return len(text)
    
    def sentence_count(self, text):
        """Count sentences in text."""
        return len([s for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()])
    
    def to_upper_case(self, text):
        """Convert text to uppercase."""
        return text.upper()
    
    def to_lower_case(self, text):
        """Convert text to lowercase."""
        return text.lower()
```

## Data Transformer Tool (servers/tools_server/tools/data_transformer.py)

```python
import json
import csv
from io import StringIO

class DataTransformer:
    """Data transformer tool for MCP."""
    
    def json_to_csv(self, json_data):
        """Convert JSON to CSV."""
        if not isinstance(json_data, list) or not json_data:
            return ""
        
        # Extract headers
        headers = list(json_data[0].keys())
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(json_data)
        
        return output.getvalue()
    
    def csv_to_json(self, csv_data):
        """Convert CSV to JSON."""
        # Parse CSV
        reader = csv.DictReader(StringIO(csv_data))
        
        # Convert to list of dictionaries
        result = []
        for row in reader:
            # Try to convert numeric values
            processed_row = {}
            for key, value in row.items():
                if value.strip() and value.strip().replace('.', '', 1).isdigit():
                    try:
                        processed_row[key] = float(value) if '.' in value else int(value)
                    except ValueError:
                        processed_row[key] = value
                else:
                    processed_row[key] = value
            
            result.append(processed_row)
        
        return result
```

## Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  # MCP Client
  mcp-client:
    build:
      context: .
      dockerfile: client/Dockerfile
    environment:
      - PORT=8080
      - SERVER_URL=http://session-manager:5000
      - CLIENT_ID=main-client
    ports:
      - "8080:8080"
    volumes:
      - ./client:/app
    depends_on:
      - session-manager

  # Session Manager
  session-manager:
    build:
      context: .
      dockerfile: session_manager/Dockerfile
    environment:
      - PORT=5000
      - SERVER_1_URL=http://resources-server:5001
      - SERVER_2_URL=http://sampling-server:5002
      - SERVER_3_URL=http://tools-server:5003
      - SERVER_4_URL=http://database-server:5004
      - SERVER_5_URL=http://internet-server:5005
      - SERVER_6_URL=http://roots-server:5006
      - SERVER_7_URL=http://prompts-server:5007
    ports:
      - "5000:5000"
    volumes:
      - ./session_manager:/app
    depends_on:
      - resources-server
      - sampling-server
      - tools-server
      - database-server
      - internet-server
      - roots-server
      - prompts-server

  # MCP Servers
  resources-server:
    build:
      context: .
      dockerfile: servers/resources_server/Dockerfile
    environment:
      - PORT=5001
      - SERVER_ID=1
      - CAPABILITIES=resources
    ports:
      - "5001:5001"
    volumes:
      - ./servers/resources_server:/app

  sampling-server:
    build:
      context: .
      dockerfile: servers/sampling_server/Dockerfile
    environment:
      - PORT=5002
      - SERVER_ID=2
      - CAPABILITIES=sampling
    ports:
      - "5002:5002"
    volumes:
      - ./servers/sampling_server:/app

  tools-server:
    build:
      context: .
      dockerfile: servers/tools_server/Dockerfile
    environment:
      - PORT=5003
      - SERVER_ID=3
      - CAPABILITIES=tools,database,api
    ports:
      - "5003:5003"
    volumes:
      - ./servers/tools_server:/app
    depends_on:
      - database

  database-server:
    build:
      context: .
      dockerfile: servers/database_server/Dockerfile
    environment:
      - PORT=5004
      - SERVER_ID=4
      - CAPABILITIES=database
      - DATABASE_URL=postgresql://postgres:postgres@database:5432/mcpdb
    ports:
      - "5004:5004"
    volumes:
      - ./servers/database_server:/app
    depends_on:
      - database

  internet-server:
    build:
      context: .
      dockerfile: servers/internet_server/Dockerfile
    environment:
      - PORT=5005
      - SERVER_ID=5
      - CAPABILITIES=internet
    ports:
      - "5005:5005"
    volumes:
      - ./servers/internet_server:/app

  roots-server:
    build:
      context: .
      dockerfile: servers/roots_server/Dockerfile
    environment:
      - PORT=5006
      - SERVER_ID=6
      - CAPABILITIES=roots
    ports:
      - "5006:5006"
    volumes:
      - ./servers/roots_server:/app

  prompts-server:
    build:
      context: .
      dockerfile: servers/prompts_server/Dockerfile
    environment:
      - PORT=5007
      - SERVER_ID=7
      - CAPABILITIES=prompts
    ports:
      - "5007:5007"
    volumes:
      - ./servers/prompts_server:/app

  # Database for MCP servers
  database:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=mcpdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Client Dockerfile (client/Dockerfile)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY client/ /app/

EXPOSE 8080

CMD ["python", "app.py"]
```

## Client Requirements (client/requirements.txt)

```
flask==2.0.1
requests==2.26.0
sseclient-py==1.7.2
```