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
