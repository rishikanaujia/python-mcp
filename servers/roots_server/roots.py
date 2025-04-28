import os
import sys
import json
import uuid
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger
from common.error_handling import ResourceError, AuthenticationError

logger = MCPLogger(service_name='roots-server')


class RootsManager:
    """Roots manager for MCP Roots Server."""

    def __init__(self):
        """Initialize the roots manager."""
        self.roots = {}
        self.operations = {
            'create': self.create_root,
            'get': self.get_root,
            'update': self.update_root,
            'delete': self.delete_root,
            'list': self.list_roots
        }

    def execute_operation(self, operation, params):
        """Execute a root operation."""
        if operation not in self.operations:
            raise ValueError(f"Unsupported operation: {operation}")

        logger.info(f"Executing root operation: {operation}")
        return self.operations[operation](params)

    def create_root(self, params):
        """Create a new root."""
        # Required parameters
        name = params.get('name')
        root_type = params.get('type')

        if not name or not root_type:
            raise ValueError("Name and type are required for root creation")

        # Generate a unique root ID
        root_id = str(uuid.uuid4())

        # Create the root object
        root = {
            'id': root_id,
            'name': name,
            'type': root_type,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat(),
            'params': params.get('params', {}),
            'metadata': params.get('metadata', {})
        }

        # Store the root
        self.roots[root_id] = root

        logger.info(f"Created root {root_id} of type {root_type}")
        return root

    def get_root(self, params):
        """Get a root by ID."""
        root_id = params.get('id')

        if not root_id:
            raise ValueError("Root ID is required")

        if root_id not in self.roots:
            raise ResourceError(f"Root not found: {root_id}")

        logger.info(f"Retrieved root {root_id}")
        return self.roots[root_id]

    def update_root(self, params):
        """Update a root."""
        root_id = params.get('id')
        updates = params.get('updates', {})

        if not root_id or not updates:
            raise ValueError("Root ID and updates are required")

        if root_id not in self.roots:
            raise ResourceError(f"Root not found: {root_id}")

        # Update the root
        root = self.roots[root_id]

        # Apply updates
        for key, value in updates.items():
            if key in ['name', 'type', 'params', 'metadata']:
                root[key] = value

        # Update timestamp
        root['updated'] = datetime.utcnow().isoformat()

        logger.info(f"Updated root {root_id}")
        return root

    def delete_root(self, params):
        """Delete a root."""
        root_id = params.get('id')

        if not root_id:
            raise ValueError("Root ID is required")

        if root_id not in self.roots:
            raise ResourceError(f"Root not found: {root_id}")

        # Remove the root
        del self.roots[root_id]

        logger.info(f"Deleted root {root_id}")
        return {'id': root_id, 'deleted': True}

    def list_roots(self, params):
        """List all roots, optionally filtered."""
        root_type = params.get('type')
        limit = params.get('limit', 100)
        offset = params.get('offset', 0)

        # Filter by type if specified
        if root_type:
            filtered_roots = [
                root for root in self.roots.values()
                if root['type'] == root_type
            ]
        else:
            filtered_roots = list(self.roots.values())

        # Sort by creation time (newest first)
        sorted_roots = sorted(
            filtered_roots,
            key=lambda r: r['created'],
            reverse=True
        )

        # Apply pagination
        paginated_roots = sorted_roots[offset:offset + limit]

        logger.info(f"Listed {len(paginated_roots)} roots")
        return {
            'roots': paginated_roots,
            'total': len(filtered_roots),
            'limit': limit,
            'offset': offset
        }