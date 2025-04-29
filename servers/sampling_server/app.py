from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from sampling import SamplingEngine

# Initialize logger
logger = MCPLogger(service_name='sampling-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5002))
SERVER_ID = os.environ.get('SERVER_ID', '2')
CAPABILITIES = os.environ.get('CAPABILITIES', 'sampling').split(',')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

# Initialize sampling engine
sampling_engine = SamplingEngine()


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
        if request_data.get('type') == 'sampling-task':
            payload = request_data.get('payload', {})
            method = payload.get('method')
            params = payload.get('params', {})

            if not method:
                raise ValueError("Sampling method is required")

            logger.info(f"Performing {method} sampling with params:", {'params': params})

            # Execute sampling
            result = sampling_engine.sample(method, params)

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result},
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
        'timestamp': datetime.utcnow().isoformat(),
        'samplingMethods': list(sampling_engine.sampling_methods.keys())
    })


# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Server {SERVER_ID} running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)