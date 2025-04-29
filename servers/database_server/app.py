# servers/database_server/app.py

from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime
import sqlite3

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from database import DatabaseConnector

# Initialize logger
logger = MCPLogger(service_name='database-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5004))
SERVER_ID = os.environ.get('SERVER_ID', '4')
CAPABILITIES = os.environ.get('CAPABILITIES', 'database').split(',')
ENABLE_LOGGING = os.environ.get('ENABLE_DATABASE_LOGGING', 'true').lower() == 'true'
DB_PATH = os.environ.get('SQLITE_DB_PATH', 'mcp.db')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

# Initialize database connector
db_connector = DatabaseConnector(db_type='sqlite', db_path=DB_PATH)


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
        if request_data.get('type') == 'database-query':
            payload = request_data.get('payload', {})
            query = payload.get('query')
            params = payload.get('params', [])
            fetch = payload.get('fetch', True)

            if not query:
                raise ValueError("SQL query is required")

            logger.info(f"Executing database query: {query}")

            # Execute the query
            result = db_connector.execute_query(query, params, fetch)

            # Log request in database if enabled
            if ENABLE_LOGGING:
                try:
                    db_connector.record_request(request_data)
                except Exception as log_error:
                    logger.error(f"Failed to log request: {str(log_error)}")

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'result': result},
                source=f"mcp-server-{SERVER_ID}"
            )

            # Log response in database if enabled
            if ENABLE_LOGGING:
                try:
                    db_connector.record_response(response)
                except Exception as log_error:
                    logger.error(f"Failed to log response: {str(log_error)}")

            return jsonify(response)

        elif request_data.get('type') == 'database-history':
            payload = request_data.get('payload', {})
            filters = payload.get('filters', {})
            limit = payload.get('limit', 100)
            offset = payload.get('offset', 0)

            logger.info(f"Retrieving request history with filters: {filters}")

            # Get request history
            history = db_connector.get_request_history(filters, limit, offset)

            # Return success response
            response = MCPProtocol.create_response(
                request_data.get('id'),
                'success',
                {'history': history},
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
    # Check database connection
    db_status = "connected" if db_connector.connected else "disconnected"

    try:
        if not db_connector.connected:
            db_connector.connect()
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        'status': 'healthy',
        'serverId': SERVER_ID,
        'capabilities': CAPABILITIES,
        'timestamp': datetime.utcnow().isoformat(),
        'database': {
            'type': db_connector.db_type,
            'path': db_connector.db_path,
            'status': db_status
        }
    })


# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Server {SERVER_ID} running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)