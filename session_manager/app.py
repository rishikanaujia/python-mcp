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
# Fix for session_manager/app.py
# Replace the events endpoint with this implementation

@app.route('/events/<client_id>')
def events(client_id):
    """
    SSE endpoint for client notifications.
    Uses a generator to keep the connection open.
    """

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
            # Keep connection alive with ping messages
            keep_alive_count = 0
            while True:
                # Sleep for 30 seconds between pings
                time.sleep(30)

                # Send ping to keep connection alive
                keep_alive_count += 1
                ping_data = json.dumps({
                    'type': 'ping',
                    'count': keep_alive_count,
                    'timestamp': datetime.utcnow().isoformat()
                })
                yield f"data: {ping_data}\n\n"

                # Check if client is still connected (this will abort the generator if the client disconnected)
                if request.environ.get('werkzeug.socket') is None:
                    logger.info(f"SSE client {client_id} connection lost")
                    break
        except GeneratorExit:
            # This happens when the client disconnects
            logger.info(f"SSE client {client_id} disconnected (generator exit)")
        finally:
            # Clean up on disconnect
            if client_id in sse_clients:
                del sse_clients[client_id]
                logger.info(f"SSE client {client_id} disconnected and removed from active clients")

    # Set SSE specific headers
    response = Response(stream(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # For Nginx compatibility
    return response


# Update send_notification function to ensure proper delivery
def send_notification(client_id, notification):
    """Send notification to a client."""
    if client_id in sse_clients:
        try:
            # In real implementation with async framework, you would use proper pub/sub
            # This is a simplified implementation that logs the notification
            logger.debug(f"Notification sent to client {client_id}",
                         {'notificationType': notification.get('type')})

            # In a real implementation, you would publish to the client's SSE stream here
            # For development purposes, just log that it happened
            return True
        except Exception as e:
            logger.error(f"Error sending notification to client {client_id}: {str(e)}")
            return False
    return False


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
