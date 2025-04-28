import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger
from common.error_handling import ResourceError

logger = MCPLogger(service_name='resources-server')


class ResourceManager:
    """Resource management for MCP Resources Server."""

    def __init__(self):
        """Initialize the resource manager."""
        self.resources = {}
        self.resource_types = set()

    def get_resource(self, resource_type, resource_id):
        """Retrieve a resource."""
        resource_key = f"{resource_type}/{resource_id}"

        if resource_key not in self.resources:
            # For development, create mock resources on demand
            return self._create_mock_resource(resource_type, resource_id)

        return self.resources[resource_key]

    def create_resource(self, resource_type, resource_data):
        """Create a new resource."""
        resource_id = str(uuid.uuid4())

        # Create the resource object
        resource = {
            'id': resource_id,
            'type': resource_type,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat(),
            **resource_data
        }

        # Store the resource
        resource_key = f"{resource_type}/{resource_id}"
        self.resources[resource_key] = resource
        self.resource_types.add(resource_type)

        logger.info(f"Created resource {resource_key}")
        return resource

    def update_resource(self, resource_type, resource_id, resource_data):
        """Update an existing resource."""
        resource_key = f"{resource_type}/{resource_id}"

        if resource_key not in self.resources:
            raise ResourceError(f"Resource {resource_key} not found")

        # Update the resource
        self.resources[resource_key].update(resource_data)
        self.resources[resource_key]['updated'] = datetime.utcnow().isoformat()

        logger.info(f"Updated resource {resource_key}")
        return self.resources[resource_key]

    def delete_resource(self, resource_type, resource_id):
        """Delete a resource."""
        resource_key = f"{resource_type}/{resource_id}"

        if resource_key not in self.resources:
            raise ResourceError(f"Resource {resource_key} not found")

        # Remove the resource
        del self.resources[resource_key]

        logger.info(f"Deleted resource {resource_key}")
        return True

    def list_resources(self, resource_type=None, limit=100, offset=0):
        """List resources, optionally filtered by type."""
        if resource_type:
            # Filter by resource type
            filtered_resources = [
                resource for key, resource in self.resources.items()
                if key.startswith(f"{resource_type}/")
            ]
        else:
            # All resources
            filtered_resources = list(self.resources.values())

        # Apply pagination
        paginated_resources = filtered_resources[offset:offset + limit]

        return {
            'resources': paginated_resources,
            'total': len(filtered_resources),
            'limit': limit,
            'offset': offset
        }

    def get_resource_types(self):
        """Get all registered resource types."""
        return list(self.resource_types)

    def _create_mock_resource(self, resource_type, resource_id):
        """Create a mock resource for development."""
        resource = {
            'id': resource_id,
            'type': resource_type,
            'name': f"Sample {resource_type}",
            'description': f"Auto-generated {resource_type} resource",
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat(),
            'properties': {
                'sample': True,
                'generated': 'on-demand'
            }
        }

        # Store the resource
        resource_key = f"{resource_type}/{resource_id}"
        self.resources[resource_key] = resource
        self.resource_types.add(resource_type)

        logger.info(f"Created mock resource {resource_key}")
        return resource

    def process_llm_response(self, prompt, response):
        """Process an LLM response."""
        # Create a record of the LLM interaction
        interaction_id = str(uuid.uuid4())

        # Process the response (could implement post-processing logic here)
        processed_response = response.strip()

        # Store as a resource
        interaction = {
            'id': interaction_id,
            'type': 'llm-interaction',
            'prompt': prompt,
            'original_response': response,
            'processed_response': processed_response,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': {
                'length': len(processed_response),
                'word_count': len(processed_response.split())
            }
        }

        # Store the interaction
        resource_key = f"llm-interaction/{interaction_id}"
        self.resources[resource_key] = interaction
        self.resource_types.add('llm-interaction')

        logger.info(f"Processed LLM response, created resource {resource_key}")

        return {
            'prompt': prompt,
            'response': processed_response,
            'interactionId': interaction_id
        }