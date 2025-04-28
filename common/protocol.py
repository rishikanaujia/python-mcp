import uuid
import json
from datetime import datetime

class MCPProtocol:
    """MCP Protocol implementation for creating and validating messages."""

    @staticmethod
    def create_request(type_name, payload, **options):
        """Create a request object."""
        request_id = options.get('id', f"req-{uuid.uuid4()}")
        source = options.get('source', 'mcp-client')
        metadata = options.get('metadata', {})

        return {
            'id': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type_name,
            'payload': payload,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }

    @staticmethod
    def create_response(request_id, status, data, **options):
        """Create a response object."""
        response_id = options.get('id', f"res-{uuid.uuid4()}")
        source = options.get('source', 'mcp-server')
        metadata = options.get('metadata', {})

        return {
            'id': response_id,
            'requestId': request_id,
            'timestamp': datetime.utcnow().isoformat(),
            'status': status,
            'data': data,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }

    @staticmethod
    def create_notification(type_name, data, **options):
        """Create a notification object."""
        notification_id = options.get('id', f"notif-{uuid.uuid4()}")
        source = options.get('source', 'mcp-server')
        metadata = options.get('metadata', {})

        return {
            'id': notification_id,
            'timestamp': datetime.utcnow().isoformat(),
            'type': type_name,
            'data': data,
            'metadata': {
                'version': '1.0',
                'source': source,
                **metadata
            }
        }

    @staticmethod
    def validate_message(message, message_type):
        """Validate a message against the MCP protocol."""
        if not isinstance(message, dict):
            return False

        # Common required fields
        if 'id' not in message or 'timestamp' not in message:
            return False

        # Message type specific validation
        if message_type == 'request':
            return 'type' in message and 'payload' in message
        elif message_type == 'response':
            return 'requestId' in message and 'status' in message
        elif message_type == 'notification':
            return 'type' in message and 'data' in message
        else:
            return False
