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
