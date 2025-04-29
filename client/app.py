from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import os
import sys
import json
import asyncio
import time
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from tool_router import ToolRouter
from llm import LLMInterface
from stdio_handler import STDIOHandler
from sse_client import SSEClient

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = MCPLogger(service_name='mcp-client')

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configuration
PORT = int(os.environ.get('CLIENT_PORT', 8080))
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


# Async process_request function
async def process_request_async(request_type, payload):
    """Process a request through the MCP asynchronously."""
    global connection_state, session_id

    if connection_state != 'connected':
        raise Exception(f"Client not connected (state: {connection_state})")

    if not session_id:
        raise Exception('No active session')

    # Create MCP request
    request_data = MCPProtocol.create_request(request_type, payload, source=CLIENT_ID)

    logger.info(f"Sending {request_type} request", {'requestId': request_data['id']})

    # Create an event loop to run the async code
    loop = asyncio.get_event_loop()

    # Define the async task
    async def make_request():
        # Use requests for now, could be replaced with aiohttp for true async
        response = requests.post(
            f"{SERVER_URL}/sessions/{session_id}/requests",
            json=request_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code not in (200, 201):
            raise Exception(f"Error from server: {response.text}")

        return response.json()

    # Run the async task
    return await loop.run_in_executor(None, lambda: requests.post(
        f"{SERVER_URL}/sessions/{session_id}/requests",
        json=request_data,
        headers={'Content-Type': 'application/json'}
    ).json())


# Synchronous version for backwards compatibility
def process_request(request_type, payload):
    """Process a request through the MCP (synchronous version)."""
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


# Async process_prompt implementation
async def process_prompt_async():
    """Process a prompt through LLM with tool routing (async version)."""
    try:
        data = request.json
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        # Initialize tool router
        tool_router = ToolRouter()

        # Step 1: Analyze prompt for tool needs
        tools_to_use = tool_router.analyze_prompt(prompt)

        # Step 2: Execute tools if needed
        tool_results = []
        if tools_to_use:
            logger.info(f"Detected {len(tools_to_use)} tools to use for prompt")

            for tool_request in tools_to_use:
                try:
                    tool_name = tool_request['tool']
                    operation = tool_request['operation']
                    params = tool_request['params']

                    logger.info(f"Executing {tool_name}.{operation}", {'params': params})

                    # Execute the tool
                    tool_response = await process_request_async('tool-execution', {
                        'tool': tool_name,
                        'operation': operation,
                        'params': params
                    })

                    # Check if the tool execution was successful
                    if tool_response.get('status') == 'success':
                        tool_result = tool_response.get('data', {}).get('result')
                        logger.info(f"Tool {tool_name}.{operation} executed successfully")

                        # Add to tool results
                        tool_results.append({
                            'tool': tool_name,
                            'operation': operation,
                            'params': params,
                            'result': tool_result
                        })
                    else:
                        error = tool_response.get('data', {}).get('error', 'Unknown error')
                        logger.error(f"Tool execution error: {error}")
                except Exception as e:
                    logger.error(f"Error executing tool: {str(e)}")

        # Step 3: Process through LLM
        if tool_results:
            # If tools were used, include their results in the prompt
            formatted_results = tool_router.format_results_for_llm(tool_results)
            enriched_prompt = f"{prompt}\n\nTool Results:\n{formatted_results}\n\nProvide a response using these tool results."

            logger.info('Processing enriched prompt with tool results', {'promptLength': len(enriched_prompt)})
            llm_result = llm.process(enriched_prompt)
        else:
            # No tools were used, process the original prompt
            logger.info('Processing original prompt', {'promptLength': len(prompt)})
            llm_result = llm.process(prompt)

        # Step 4: Send result through MCP for any additional processing
        result = await process_request_async('llm-response', {
            'prompt': prompt,
            'response': llm_result['result'],
            'metadata': {
                'tools_used': [f"{t['tool']}.{t['operation']}" for t in tool_results]
            }
        })

        return jsonify(result)
    except Exception as e:
        logger.error(f'Processing error: {str(e)}')
        return jsonify({'error': str(e)}), 500


# Endpoint for processing prompts
@app.route('/process', methods=['POST'])
def process_prompt_endpoint():
    """Endpoint for processing prompts with tool routing."""
    # Get or create an event loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(process_prompt_async())
    except Exception as e:
        logger.error(f'Error in process_prompt_endpoint: {str(e)}')
        return jsonify({'error': str(e)}), 500


# Original process endpoint (without tool routing) for backwards compatibility
@app.route('/process_simple', methods=['POST'])
def process_prompt():
    """Process an LLM prompt without tool routing."""
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
        'sessionId': session_id or None,
        'llmStatus': llm.get_status()
    })


# Serve the main page
@app.route('/')
def index():
    return render_template('index.html')


# Start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)