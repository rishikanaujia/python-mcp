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