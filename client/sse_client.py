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

    # Fix for client/sse_client.py
    # Replace the _listen method with this implementation

    def _listen(self):
        """Listen for SSE events."""
        try:
            headers = {'Accept': 'text/event-stream', 'Cache-Control': 'no-cache'}

            # Set up the connection with a timeout
            session = requests.Session()
            response = session.get(self.url, headers=headers, stream=True, timeout=60)

            if response.status_code != 200:
                logger.error(f'Failed to connect to SSE endpoint: {response.status_code}')
                self._notify_listeners('error', {'error': f'HTTP error: {response.status_code}'})
                return

            self.connected = True
            self._notify_listeners('connection', {'status': 'connected'})

            # Create a buffer for incomplete lines
            buffer = ""

            # Process the event stream
            for line in response.iter_lines(decode_unicode=True):
                if not self.running:
                    break

                if line:
                    if line.startswith('data:'):
                        data = line[5:].strip()
                        try:
                            data_json = json.loads(data)

                            # Log only non-ping messages to avoid cluttering logs
                            if data_json.get('type') != 'ping':
                                logger.debug(f"Received SSE event: {data_json.get('type')}")

                            self._notify_listeners('message', data_json)

                            # Also notify type-specific listeners
                            if 'type' in data_json:
                                self._notify_listeners(data_json['type'], data_json)
                        except json.JSONDecodeError:
                            logger.error('Error parsing SSE message', {'data': data})
                            self._notify_listeners('error', {'error': 'JSON parse error', 'data': data})
        except requests.exceptions.Timeout:
            logger.warning('SSE connection timed out, will reconnect')
            self.connected = False
            self._notify_listeners('connection', {'status': 'disconnected', 'reason': 'timeout'})
        except requests.exceptions.RequestException as e:
            logger.error(f'SSE connection error: {str(e)}')
            self._notify_listeners('error', {'error': str(e)})
            self.connected = False
            self._notify_listeners('connection', {'status': 'disconnected', 'reason': 'error'})
        except Exception as e:
            logger.error(f'Unexpected error in SSE connection: {str(e)}')
            self._notify_listeners('error', {'error': str(e)})
            self.connected = False
            self._notify_listeners('connection', {'status': 'disconnected', 'reason': 'unexpected'})
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
