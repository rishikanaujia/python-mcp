from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from internet import InternetConnector

# Initialize logger
logger = MCPLogger(service_name='internet-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5005))
SERVER_ID = os.environ.get('SERVER_ID', '5')
CAPABILITIES = os.environ.get('CAPABILITIES', 'internet').split(',')
ENABLE_RATE_LIMITING = os.environ.get('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
ENABLE_DOMAIN_RESTRICTIONS = os.environ.get('ENABLE_DOMAIN_RESTRICTIONS', 'true').lower() == 'true'

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

# Initialize internet connector
internet_connector = InternetConnector()


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
        if request_data.get('type') == 'internet-request':
            payload = request_data.get('payload', {})
            request_params = payload.get('request', {})

            if not request_params or not request_params.get('url'):
                raise ValueError("URL is required for internet request")

            logger.info(f"Making internet request to {request_params.get('url')}")

            # Make the request
            result = internet_connector.make_request(request_params)

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result},
                source=f"mcp-server-{SERVER_ID}"
            )

            return jsonify(response)

        elif request_data.get('type') == 'internet-search':
            payload = request_data.get('payload', {})
            query = payload.get('query')
            search_params = payload.get('params', {})

            if not query:
                raise ValueError("Search query is required")

            logger.info(f"Performing internet search for '{query}'")

            # Perform search
            result = internet_connector.search(query, search_params)

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
    # Get rate limit info
    rate_limits = internet_connector.rate_limits
    request_count = len(internet_connector.request_history)
    total_data_mb = sum(r['size_bytes'] for r in internet_connector.request_history) / (1024 * 1024)

    return jsonify({
        'status': 'healthy',
        'serverId': SERVER_ID,
        'capabilities': CAPABILITIES,
        'timestamp': datetime.utcnow().isoformat(),
        'internet': {
            'rateLimit': {
                'enabled': ENABLE_RATE_LIMITING,
                'requestsPerMinute': rate_limits['requests_per_minute'],
                'dataPerMinuteMB': rate_limits['data_per_minute_mb'],
                'currentRequests': request_count,
                'currentDataMB': total_data_mb
            },
            'domainRestrictions': {
                'enabled': ENABLE_DOMAIN_RESTRICTIONS,
                'allowedDomains': internet_connector.allowed_domains,
                'blockedDomains': internet_connector.blocked_domains
            }
        }
    })


# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Server {SERVER_ID} running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)