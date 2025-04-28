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