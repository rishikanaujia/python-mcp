#!/bin/bash
# Script to set up the Python MCP directory structure and files

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Creating Python MCP Project Directory Structure...${NC}"

# Create root directory
mkdir -p python-mcp
cd python-mcp

# Create main directories
echo -e "${YELLOW}Creating main directories...${NC}"
mkdir -p client/static client/templates
mkdir -p session_manager/src
mkdir -p common
mkdir -p servers/resources_server
mkdir -p servers/sampling_server
mkdir -p servers/tools_server/tools
mkdir -p servers/database_server
mkdir -p servers/internet_server
mkdir -p servers/roots_server
mkdir -p servers/prompts_server

# Create requirements.txt
echo -e "${YELLOW}Creating requirements.txt...${NC}"
cat > requirements.txt << 'EOF'
flask==2.0.1
requests==2.26.0
sseclient-py==1.7.2
python-dotenv==0.19.0
pydantic==1.8.2
asyncio==3.4.3
aiohttp==3.7.4.post0
websockets==9.1
psycopg2-binary==2.9.1
EOF

# Create common files
echo -e "${YELLOW}Creating common files...${NC}"

# common/__init__.py
touch common/__init__.py

# common/protocol.py
cat > common/protocol.py << 'EOF'
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
EOF

# common/logging_utils.py
cat > common/logging_utils.py << 'EOF'
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
EOF

# common/error_handling.py
cat > common/error_handling.py << 'EOF'
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
EOF

# Create client files
echo -e "${YELLOW}Creating client files...${NC}"

# client/requirements.txt
cat > client/requirements.txt << 'EOF'
flask==2.0.1
requests==2.26.0
sseclient-py==1.7.2
python-dotenv==0.19.0
EOF

# client/Dockerfile
cat > client/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY client/ /app/

EXPOSE 8080

CMD ["python", "app.py"]
EOF

# client/app.py
cat > client/app.py << 'EOF'
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
app = Flask(__name__, static_folder='static', template_folder='templates')

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
EOF

# client/llm.py
cat > client/llm.py << 'EOF'
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
EOF

# client/stdio_handler.py
cat > client/stdio_handler.py << 'EOF'
import sys
import datetime
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='stdio-handler')

class STDIOHandler:
    """Standard I/O Handler for MCP Client."""

    def __init__(self):
        self.input_buffer = []
        self.output_listeners = []

    def handle_input(self, input_text):
        """Handle input from stdin."""
        logger.debug('Handling input', {'inputLength': len(input_text)})

        # Store input in buffer
        self.input_buffer.append({
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'text': input_text
        })

        return input_text

    def send_output(self, output):
        """Send output to stdout."""
        logger.debug('Sending output', {'outputLength': len(output)})

        # Notify all output listeners
        for listener in self.output_listeners:
            try:
                listener(output)
            except Exception as e:
                logger.error(f'Error in output listener: {str(e)}')

        print(output)

    def add_output_listener(self, listener):
        """Add output listener."""
        if callable(listener):
            self.output_listeners.append(listener)

    def remove_output_listener(self, listener):
        """Remove output listener."""
        if listener in self.output_listeners:
            self.output_listeners.remove(listener)

    def get_input_history(self, limit=10):
        """Get input history."""
        return self.input_buffer[-limit:] if limit > 0 else self.input_buffer

    def clear_input_buffer(self):
        """Clear input buffer."""
        self.input_buffer = []
EOF

# client/sse_client.py
cat > client/sse_client.py << 'EOF'
import threading
import time
import json
import requests
import sys
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='sse-client')

class SSEClient:
    """SSE Client for notifications."""

    def __init__(self, url):
        self.url = url
        self.thread = None
        self.running = False
        self.connected = False
        self.event_listeners = {}

    def connect(self):
        """Connect to SSE endpoint."""
        logger.info('Connecting to SSE endpoint', {'url': self.url})

        if self.thread and self.thread.is_alive():
            self.disconnect()

        self.running = True
        self.thread = threading.Thread(target=self._listen)
        self.thread.daemon = True
        self.thread.start()

    def _listen(self):
        """Listen for SSE events."""
        try:
            headers = {'Accept': 'text/event-stream'}
            with requests.get(self.url, headers=headers, stream=True) as response:
                if response.status_code != 200:
                    logger.error(f'Failed to connect to SSE endpoint: {response.status_code}')
                    self._notify_listeners('error', {'error': f'HTTP error: {response.status_code}'})
                    return

                self.connected = True
                self._notify_listeners('connection', {'status': 'connected'})

                buffer = ""
                for line in response.iter_lines(decode_unicode=True):
                    if not self.running:
                        break

                    if line:
                        if line.startswith('data:'):
                            data = line[5:].strip()
                            try:
                                data_json = json.loads(data)
                                self._notify_listeners('message', data_json)

                                # Also notify type-specific listeners
                                if 'type' in data_json:
                                    self._notify_listeners(data_json['type'], data_json)
                            except json.JSONDecodeError:
                                logger.error('Error parsing SSE message', {'data': data})
                                self._notify_listeners('error', {'error': 'JSON parse error', 'data': data})
        except Exception as e:
            logger.error(f'SSE connection error: {str(e)}')
            self._notify_listeners('error', {'error': str(e)})
        finally:
            self.connected = False
            self._notify_listeners('connection', {'status': 'disconnected'})

            # Try to reconnect after a delay if still running
            if self.running:
                time.sleep(5)  # Wait 5 seconds before reconnecting
                if self.running:  # Check again after the delay
                    logger.info('Attempting to reconnect to SSE endpoint')
                    self._listen()

    def disconnect(self):
        """Disconnect from SSE endpoint."""
        if self.running:
            logger.info('Disconnecting from SSE endpoint')
            self.running = False
            if self.thread:
                self.thread.join(timeout=1)
            self.connected = False
            self._notify_listeners('connection', {'status': 'disconnected'})

    def add_event_listener(self, event, listener):
        """Add event listener."""
        if event not in self.event_listeners:
            self.event_listeners[event] = []

        self.event_listeners[event].append(listener)

    def remove_event_listener(self, event, listener):
        """Remove event listener."""
        if event in self.event_listeners and listener in self.event_listeners[event]:
            self.event_listeners[event].remove(listener)

    def _notify_listeners(self, event, data):
        """Notify all listeners for an event."""
        if event in self.event_listeners:
            for listener in self.event_listeners[event]:
                try:
                    listener(data)
                except Exception as e:
                    logger.error(f'Error in event listener: {str(e)}')

    def is_connected(self):
        """Get connection status."""
        return self.connected
EOF

# client/templates/index.html
mkdir -p client/templates
cat > client/templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Client Interface</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
</head>
<body>
    <div class="container">
        <h1>Model Context Protocol (MCP) Client</h1>

        <div class="status-bar">
            <div class="status">
                <span>Status: </span>
                <span id="status-text">Disconnected</span>
            </div>
            <div class="session">
                <span>Session ID: </span>
                <span id="session-id">None</span>
            </div>
        </div>

        <div class="control-panel">
            <button id="initialize-btn">Initialize</button>
            <button id="terminate-btn" disabled>Terminate</button>
        </div>

        <div class="main-panel">
            <div class="input-panel">
                <h2>Input</h2>
                <textarea id="prompt-input" placeholder="Enter your prompt here..." rows="5"></textarea>
                <button id="process-btn" disabled>Process</button>
            </div>

            <div class="output-panel">
                <h2>Output</h2>
                <div id="output-display" class="output-display"></div>
            </div>
        </div>

        <div class="tools-panel">
            <h2>Tools</h2>
            <div class="tool-form">
                <div class="form-group">
                    <label for="tool-select">Tool:</label>
                    <select id="tool-select">
                        <option value="calculator">Calculator</option>
                        <option value="textProcessor">Text Processor</option>
                        <option value="dataTransformer">Data Transformer</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="operation-select">Operation:</label>
                    <select id="operation-select"></select>
                </div>

                <div id="params-container" class="params-container"></div>

                <button id="execute-tool-btn" disabled>Execute Tool</button>
            </div>

            <div id="tool-result" class="tool-result"></div>
        </div>

        <div class="notifications-panel">
            <h2>Notifications</h2>
            <div id="notifications-display" class="notifications-display"></div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='client.js') }}"></script>
</body>
</html>
EOF

# client/static/styles.css
mkdir -p client/static
cat > client/static/styles.css << 'EOF'
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

body {
    background-color: #f5f5f5;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background-color: #ffffff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

h1 {
    color: #333;
    margin-bottom: 20px;
    text-align: center;
}

h2 {
    color: #555;
    margin-bottom: 10px;
    font-size: 18px;
}

.status-bar {
    display: flex;
    justify-content: space-between;
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
}

.control-panel {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

button {
    padding: 8px 16px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #3a80d2;
}

button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
}

.main-panel {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.input-panel, .output-panel {
    flex: 1;
}

textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    resize: vertical;
    margin-bottom: 10px;
}

.output-display {
    height: 300px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    overflow-y: auto;
    background-color: #f9f9f9;
}

.tools-panel {
    margin-bottom: 20px;
}

.tool-form {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 4px;
    margin-bottom: 10px;
}

.form-group {
    margin-bottom: 10px;
}

label {
    display: block;
    margin-bottom: 5px;
    color: #555;
}

select, input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.params-container {
    margin-bottom: 10px;
}

.tool-result {
    min-height: 100px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    background-color: #f9f9f9;
}

.notifications-panel {
    margin-bottom: 20px;
}

.notifications-display {
    height: 200px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    overflow-y: auto;
    background-color: #f9f9f9;
}

.notification {
    padding: 8px;
    margin-bottom: 5px;
    border-radius: 4px;
    background-color: #e8f4fd;
    border-left: 3px solid #4a90e2;
}

.notification-error {
    background-color: #fde8e8;
    border-left: 3px solid #e24a4a;
}

.notification-success {
    background-color: #e8fde8;
    border-left: 3px solid #4ae24a;
}

.notification-time {
    font-size: 12px;
    color: #888;
    margin-bottom: 3px;
}
EOF

# client/static/client.js
cat > client/static/client.js << 'EOF'
// MCP Client Interface

// Tool definitions
const tools = {
  calculator: {
    operations: ['add', 'subtract', 'multiply', 'divide', 'power'],
    params: {
      add: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      subtract: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      multiply: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B' }
      ],
      divide: [
        { name: 'a', type: 'number', label: 'Number A' },
        { name: 'b', type: 'number', label: 'Number B (non-zero)' }
      ],
      power: [
        { name: 'a', type: 'number', label: 'Base' },
        { name: 'b', type: 'number', label: 'Exponent' }
      ]
    }
  },
  textProcessor: {
    operations: ['word_count', 'character_count', 'sentence_count', 'to_upper_case', 'to_lower_case'],
    params: {
      word_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      character_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      sentence_count: [
        { name: 'text', type: 'text', label: 'Text to analyze' }
      ],
      to_upper_case: [
        { name: 'text', type: 'text', label: 'Text to convert' }
      ],
      to_lower_case: [
        { name: 'text', type: 'text', label: 'Text to convert' }
      ]
    }
  },
  dataTransformer: {
    operations: ['json_to_csv', 'csv_to_json'],
    params: {
      json_to_csv: [
        { name: 'json_data', type: 'textarea', label: 'JSON data' }
      ],
      csv_to_json: [
        { name: 'csv_data', type: 'textarea', label: 'CSV data' }
      ]
    }
  }
};

// DOM Elements
const statusText = document.getElementById('status-text');
const sessionId = document.getElementById('session-id');
const initializeBtn = document.getElementById('initialize-btn');
const terminateBtn = document.getElementById('terminate-btn');
const promptInput = document.getElementById('prompt-input');
const processBtn = document.getElementById('process-btn');
const outputDisplay = document.getElementById('output-display');
const toolSelect = document.getElementById('tool-select');
const operationSelect = document.getElementById('operation-select');
const paramsContainer = document.getElementById('params-container');
const executeToolBtn = document.getElementById('execute-tool-btn');
const toolResult = document.getElementById('tool-result');
const notificationsDisplay = document.getElementById('notifications-display');

// Initialize the client
async function initializeClient() {
  try {
    initializeBtn.disabled = true;

    // Update status
    statusText.textContent = 'Initializing...';

    // Call initialize endpoint
    const response = await fetch('/initialize', {
      method: 'POST'
    });

    const result = await response.json();

    if (result.success) {
      // Update UI
      statusText.textContent = 'Connected';
      sessionId.textContent = result.sessionId;

      // Enable/disable buttons
      initializeBtn.disabled = true;
      terminateBtn.disabled = false;
      processBtn.disabled = false;
      executeToolBtn.disabled = false;

      addNotification('Client initialized successfully.', 'success');
    } else {
      statusText.textContent = 'Error';
      addNotification(`Initialization failed: ${result.error}`, 'error');
      initializeBtn.disabled = false;
    }
  } catch (error) {
    statusText.textContent = 'Error';
    addNotification(`Initialization error: ${error.message}`, 'error');
    initializeBtn.disabled = false;
  }
}

// Terminate the client
async function terminateClient() {
  try {
    terminateBtn.disabled = true;

    // Update status
    statusText.textContent = 'Terminating...';

    // Call terminate endpoint
    const response = await fetch('/terminate', {
      method: 'POST'
    });

    const result = await response.json();

    if (result.success) {
      // Update UI
      statusText.textContent = 'Disconnected';
      sessionId.textContent = 'None';

      // Enable/disable buttons
      initializeBtn.disabled = false;
      terminateBtn.disabled = true;
      processBtn.disabled = true;
      executeToolBtn.disabled = true;

      addNotification('Client terminated successfully.', 'success');
    } else {
      statusText.textContent = 'Error';
      addNotification(`Termination failed: ${result.error}`, 'error');
      terminateBtn.disabled = false;
    }
  } catch (error) {
    statusText.textContent = 'Error';
    addNotification(`Termination error: ${error.message}`, 'error');
    terminateBtn.disabled = false;
  }
}

// Process an LLM prompt
async function processPrompt() {
  try {
    const prompt = promptInput.value.trim();

    if (!prompt) {
      addNotification('Please enter a prompt.', 'error');
      return;
    }

    // Disable process button
    processBtn.disabled = true;

    // Call process endpoint
    const response = await fetch('/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ prompt })
    });

    const result = await response.json();

    // Display result
    if (result.status === 'success') {
      outputDisplay.innerHTML += `<div class="prompt"><strong>Prompt:</strong> ${prompt}</div>`;
      outputDisplay.innerHTML += `<div class="response"><strong>Response:</strong> ${result.data.response}</div>`;

      // Clear prompt input
      promptInput.value = '';

      addNotification('Prompt processed successfully.', 'success');
    } else {
      addNotification(`Processing failed: ${result.error || 'Unknown error'}`, 'error');
    }

    // Enable process button
    processBtn.disabled = false;

    // Scroll to bottom of output
    outputDisplay.scrollTop = outputDisplay.scrollHeight;
  } catch (error) {
    addNotification(`Processing error: ${error.message}`, 'error');
    processBtn.disabled = false;
  }
}

// Execute a tool
async function executeTool() {
  try {
    const tool = toolSelect.value;
    const operation = operationSelect.value;

    // Collect parameters
    const params = {};
    const paramFields = document.querySelectorAll('.param-field');

    paramFields.forEach(field => {
      const paramName = field.getAttribute('data-param');
      let value = field.value;

      // Convert number inputs to actual numbers
      if (field.type === 'number') {
        value = Number(value);
      }

      // Try to parse JSON for textarea inputs (for json_to_csv)
      if (field.tagName === 'TEXTAREA' && operation === 'json_to_csv') {
        try {
          value = JSON.parse(value);
        } catch (e) {
          throw new Error('Invalid JSON data');
        }
      }

      params[paramName] = value;
    });

    // Disable execute button
    executeToolBtn.disabled = true;

    // Call tools endpoint
    const response = await fetch('/tools', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        tool,
        operation,
        params
      })
    });

    const result = await response.json();

    // Display result
    if (result.status === 'success') {
      const resultData = JSON.stringify(result.data.result, null, 2);
      toolResult.innerHTML = `<pre>${resultData}</pre>`;

      addNotification(`Tool ${tool}.${operation} executed successfully.`, 'success');
    } else {
      toolResult.innerHTML = `<div class="error">Error: ${result.error || 'Unknown error'}</div>`;
      addNotification(`Tool execution failed: ${result.error || 'Unknown error'}`, 'error');
    }

    // Enable execute button
    executeToolBtn.disabled = false;
  } catch (error) {
    toolResult.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    addNotification(`Tool execution error: ${error.message}`, 'error');
    executeToolBtn.disabled = false;
  }
}

// Add a notification
function addNotification(message, type = 'info') {
  const notificationElement = document.createElement('div');
  notificationElement.className = `notification notification-${type}`;

  const timeElement = document.createElement('div');
  timeElement.className = 'notification-time';
  timeElement.textContent = new Date().toLocaleTimeString();

  const messageElement = document.createElement('div');
  messageElement.textContent = message;

  notificationElement.appendChild(timeElement);
  notificationElement.appendChild(messageElement);

  notificationsDisplay.appendChild(notificationElement);

  // Scroll to bottom of notifications
  notificationsDisplay.scrollTop = notificationsDisplay.scrollHeight;
}

// Update operation select based on selected tool
function updateOperations() {
  const tool = toolSelect.value;
  const operations = tools[tool].operations;

  // Clear operations
  operationSelect.innerHTML = '';

  // Add operations
  operations.forEach(operation => {
    const option = document.createElement('option');
    option.value = operation;
    option.textContent = operation;
    operationSelect.appendChild(option);
  });

  // Update parameters
  updateParameters();
}

// Update parameters based on selected tool and operation
function updateParameters() {
  const tool = toolSelect.value;
  const operation = operationSelect.value;
  const params = tools[tool].params[operation];

  // Clear parameters
  paramsContainer.innerHTML = '';

  // Add parameter fields
  params.forEach(param => {
    const formGroup = document.createElement('div');
    formGroup.className = 'form-group';

    const label = document.createElement('label');
    label.textContent = param.label;

    let input;

    if (param.type === 'textarea') {
      input = document.createElement('textarea');
      input.rows = 5;
    } else {
      input = document.createElement('input');
      input.type = param.type;
    }

    input.className = 'param-field';
    input.setAttribute('data-param', param.name);

    formGroup.appendChild(label);
    formGroup.appendChild(input);

    paramsContainer.appendChild(formGroup);
  });
}

// Initialize tool operations
updateOperations();

// Event listeners
initializeBtn.addEventListener('click', initializeClient);
terminateBtn.addEventListener('click', terminateClient);
processBtn.addEventListener('click', processPrompt);
executeToolBtn.addEventListener('click', executeTool);
toolSelect.addEventListener('change', updateOperations);
operationSelect.addEventListener('change', updateParameters);

// Add notification on load
addNotification('MCP Client Interface loaded.');
EOF

# Create session_manager files
echo -e "${YELLOW}Creating session manager files...${NC}"

# session_manager/requirements.txt
cat > session_manager/requirements.txt << 'EOF'
flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
EOF

# session_manager/Dockerfile
cat > session_manager/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY session_manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY session_manager/ /app/

EXPOSE 5000

CMD ["python", "app.py"]
EOF

# session_manager/app.py
cat > session_manager/app.py << 'EOF'
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
def handle_request(session_id):
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
        response = dispatcher.dispatch(request_data)

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
EOF

# session_manager/dispatcher.py
cat > session_manager/dispatcher.py << 'EOF'
import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol

logger = MCPLogger(service_name='request-dispatcher')

# Request type to server mapping
REQUEST_TYPE_MAPPING = {
    'resource-request': '1',
    'sampling-task': '2',
    'tool-execution': '3',
    'database-query': '4',
    'internet-search': '5',
    'root-operation': '6',
    'prompt-management': '7',
    'llm-response': '1',  # Process LLM responses through resources server
    'default': '1'
}

class RequestDispatcher:
    """Request Dispatcher for MCP Session Manager."""

    def __init__(self, server_urls):
        self.server_urls = server_urls

    def dispatch(self, request):
        """Dispatch a request to the appropriate MCP server."""
        # Validate request
        if not MCPProtocol.validate_message(request, 'request'):
            raise ValueError('Invalid request format')

        # Determine which server to route to
        request_type = request.get('type', 'default')
        server_id = REQUEST_TYPE_MAPPING.get(request_type, REQUEST_TYPE_MAPPING['default'])
        server_url = self.server_urls.get(server_id)

        if not server_url:
            raise ValueError(f"No server URL configured for server {server_id}")

        logger.info(f"Dispatching {request_type} request to server {server_id}", {
            'requestId': request.get('id'),
            'serverUrl': server_url
        })

        try:
            # Forward the request to the appropriate MCP server
            response = requests.post(
                f"{server_url}/process",
                json=request,
                headers={'Content-Type': 'application/json'},
                timeout=30  # 30 seconds timeout
            )

            if response.status_code != 200:
                raise ValueError(f"Server {server_id} returned error: {response.text}")

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error dispatching to server {server_id}: {str(e)}")
            raise ValueError(f"Failed to dispatch request: {str(e)}")

    def check_health(self):
        """Check health of all servers."""
        results = {}

        for server_id, server_url in self.server_urls.items():
            try:
                response = requests.get(
                    f"{server_url}/health",
                    timeout=5
                )

                if response.status_code == 200:
                    results[server_id] = {
                        'status': 'healthy',
                        'details': response.json()
                    }
                else:
                    results[server_id] = {
                        'status': 'unhealthy',
                        'error': f"HTTP {response.status_code}: {response.text}"
                    }

            except Exception as e:
                results[server_id] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }

        return results
EOF

# Create tools_server files
echo -e "${YELLOW}Creating tools server files...${NC}"

# servers/tools_server/requirements.txt
cat > servers/tools_server/requirements.txt << 'EOF'
flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
EOF

# servers/tools_server/Dockerfile
cat > servers/tools_server/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY servers/tools_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY servers/tools_server/ /app/

EXPOSE 5003

CMD ["python", "app.py"]
EOF

# servers/tools_server/app.py
cat > servers/tools_server/app.py << 'EOF'
from flask import Flask, request, jsonify
import json
import os
import sys
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
                    {'result': api_response.json() if api_response.content else None},
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
EOF

# servers/tools_server/tools/__init__.py
mkdir -p servers/tools_server/tools
touch servers/tools_server/tools/__init__.py

# servers/tools_server/tools/calculator.py
cat > servers/tools_server/tools/calculator.py << 'EOF'
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
EOF

# servers/tools_server/tools/text_processor.py
cat > servers/tools_server/tools/text_processor.py << 'EOF'
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
EOF

# servers/tools_server/tools/data_transformer.py
cat > servers/tools_server/tools/data_transformer.py << 'EOF'
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
EOF

# Create resources_server files
echo -e "${YELLOW}Creating resources server files...${NC}"

# servers/resources_server/requirements.txt
cat > servers/resources_server/requirements.txt << 'EOF'
flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
EOF

# servers/resources_server/Dockerfile
cat > servers/resources_server/Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY servers/resources_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY servers/resources_server/ /app/

EXPOSE 5001

CMD ["python", "app.py"]
EOF

# servers/resources_server/app.py
cat > servers/resources_server/app.py << 'EOF'
from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol

# Initialize logger
logger = MCPLogger(service_name='resources-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5001))
SERVER_ID = os.environ.get('SERVER_ID', '1')
CAPABILITIES = os.environ.get('CAPABILITIES', 'resources').split(',')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

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
        if request_data.get('type') == 'resource-request':
            payload = request_data.get('payload', {})
            resource_type = payload.get('resourceType')
            resource_id = payload.get('resourceId')

            logger.info(f"Processing resource request for {resource_type}/{resource_id}")

            # Mock resource data
            resource_data = {
                'id': resource_id,
                'type': resource_type,
                'name': f"Sample {resource_type}",
                'timestamp': datetime.utcnow().isoformat()
            }

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'resource': resource_data},
                source=f"mcp-server-{SERVER_ID}"
            )

            return jsonify(response)

        # Handle LLM responses
        elif request_data.get('type') == 'llm-response':
            payload = request_data.get('payload', {})
            prompt = payload.get('prompt', '')
            response_text = payload.get('response', '')

            logger.info(f"Processing LLM response", {'promptLength': len(prompt)})

            # Process the LLM response (e.g., post-processing, formatting, etc.)
            processed_response = response_text.strip()

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {
                    'prompt': prompt,
                    'response': processed_response
                },
                source=f"mcp-server-{SERVER_ID}"
            )

            return jsonify(response)

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
EOF

# Create basic server template for all remaining server types
for server in sampling_server database_server internet_server roots_server prompts_server; do
  SERVER_ID=$(case $server in
    sampling_server) echo "2" ;;
    database_server) echo "4" ;;
    internet_server) echo "5" ;;
    roots_server) echo "6" ;;
    prompts_server) echo "7" ;;
  esac)

  PORT=$((5000 + SERVER_ID))
  CAPABILITIES=$(case $server in
    sampling_server) echo "sampling" ;;
    database_server) echo "database" ;;
    internet_server) echo "internet" ;;
    roots_server) echo "roots" ;;
    prompts_server) echo "prompts" ;;
  esac)

  echo -e "${YELLOW}Creating ${server} files...${NC}"

  # requirements.txt
  cat > servers/${server}/requirements.txt << EOF
flask==2.0.1
requests==2.26.0
python-dotenv==0.19.0
EOF

  # Dockerfile
  cat > servers/${server}/Dockerfile << EOF
FROM python:3.9-slim

WORKDIR /app

COPY servers/${server}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY common/ /app/common/
COPY servers/${server}/ /app/

EXPOSE ${PORT}

CMD ["python", "app.py"]
EOF

  # app.py (basic template)
  cat > servers/${server}/app.py << EOF
from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol

# Initialize logger
logger = MCPLogger(service_name='${server}')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', ${PORT}))
SERVER_ID = os.environ.get('SERVER_ID', '${SERVER_ID}')
CAPABILITIES = os.environ.get('CAPABILITIES', '${CAPABILITIES}').split(',')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

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
        if request_data.get('type') == '${CAPABILITIES}-task':
            logger.info(f"Processing ${CAPABILITIES} task")

            # Mock result data
            result_data = {
                'id': request_data.get('id'),
                'timestamp': datetime.utcnow().isoformat(),
                'result': f"${CAPABILITIES} task processed successfully"
            }

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result_data},
                source=f"mcp-server-{SERVER_ID}"
            )

            return jsonify(response)
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
EOF

done

# Create docker-compose.yml
echo -e "${YELLOW}Creating docker-compose.yml...${NC}"
cat > docker-compose.yml << 'EOF'
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
EOF

# Make the script executable
chmod +x setup.sh

echo -e "${GREEN}Python MCP project structure and files created successfully!${NC}"
echo -e "You can now run the following commands to start the MCP system:"
echo -e "${YELLOW}cd python-mcp${NC}"
echo -e "${YELLOW}docker-compose up --build${NC}"
echo -e "Or for development, you can run each component individually:"
echo -e "${YELLOW}cd python-mcp${NC}"
echo -e "${YELLOW}pip install -r requirements.txt${NC}"
echo -e "${YELLOW}python client/app.py${NC}"