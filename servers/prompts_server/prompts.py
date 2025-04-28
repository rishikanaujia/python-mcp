import os
import sys
import json
import uuid
import re
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger
from common.error_handling import ResourceError

logger = MCPLogger(service_name='prompts-server')


class PromptsManager:
    """Prompts manager for MCP Prompts Server."""

    def __init__(self):
        """Initialize the prompts manager."""
        self.prompts = {}
        self.templates = {}
        self.categories = set()

    def create_prompt(self, prompt_data):
        """Create a new prompt."""
        # Required fields
        prompt_text = prompt_data.get('text')
        title = prompt_data.get('title')

        if not prompt_text or not title:
            raise ValueError("Prompt text and title are required")

        # Generate prompt ID
        prompt_id = str(uuid.uuid4())

        # Optional fields
        description = prompt_data.get('description', '')
        category = prompt_data.get('category', 'general')
        tags = prompt_data.get('tags', [])
        metadata = prompt_data.get('metadata', {})

        # Create prompt object
        prompt = {
            'id': prompt_id,
            'title': title,
            'text': prompt_text,
            'description': description,
            'category': category,
            'tags': tags,
            'metadata': metadata,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat()
        }

        # Store the prompt
        self.prompts[prompt_id] = prompt

        # Track category
        self.categories.add(category)

        logger.info(f"Created prompt {prompt_id}")
        return prompt

    def get_prompt(self, prompt_id):
        """Get a prompt by ID."""
        if prompt_id not in self.prompts:
            raise ResourceError(f"Prompt not found: {prompt_id}")

        logger.info(f"Retrieved prompt {prompt_id}")
        return self.prompts[prompt_id]

    def update_prompt(self, prompt_id, updates):
        """Update a prompt."""
        if prompt_id not in self.prompts:
            raise ResourceError(f"Prompt not found: {prompt_id}")

        prompt = self.prompts[prompt_id]

        # Apply updates
        updatable_fields = ['title', 'text', 'description', 'category', 'tags', 'metadata']
        for field in updatable_fields:
            if field in updates:
                prompt[field] = updates[field]

        # Update timestamp
        prompt['updated'] = datetime.utcnow().isoformat()

        # Update category tracking if changed
        if 'category' in updates:
            self.categories.add(updates['category'])

        logger.info(f"Updated prompt {prompt_id}")
        return prompt

    def delete_prompt(self, prompt_id):
        """Delete a prompt."""
        if prompt_id not in self.prompts:
            raise ResourceError(f"Prompt not found: {prompt_id}")

        # Remove the prompt
        del self.prompts[prompt_id]

        logger.info(f"Deleted prompt {prompt_id}")
        return {'id': prompt_id, 'deleted': True}

    def list_prompts(self, filters=None, limit=100, offset=0):
        """List prompts with optional filtering."""
        filtered_prompts = []

        # Apply filters
        for prompt in self.prompts.values():
            if filters:
                # Filter by category
                if 'category' in filters and prompt['category'] != filters['category']:
                    continue

                # Filter by tags (any match)
                if 'tags' in filters:
                    filter_tags = set(filters['tags'])
                    prompt_tags = set(prompt['tags'])
                    if not filter_tags.intersection(prompt_tags):
                        continue

                # Filter by search term
                if 'search' in filters:
                    search_term = filters['search'].lower()
                    if (search_term not in prompt['title'].lower() and
                            search_term not in prompt['description'].lower() and
                            search_term not in prompt['text'].lower()):
                        continue

            # Prompt passed all filters
            filtered_prompts.append(prompt)

        # Sort by updated timestamp (newest first)
        sorted_prompts = sorted(
            filtered_prompts,
            key=lambda p: p['updated'],
            reverse=True
        )

        # Apply pagination
        paginated_prompts = sorted_prompts[offset:offset + limit]

        return {
            'prompts': paginated_prompts,
            'total': len(filtered_prompts),
            'limit': limit,
            'offset': offset
        }

    def get_categories(self):
        """Get all prompt categories."""
        return list(self.categories)

    # Template Management

    def create_template(self, template_data):
        """Create a prompt template."""
        # Required fields
        template_text = template_data.get('text')
        name = template_data.get('name')

        if not template_text or not name:
            raise ValueError("Template text and name are required")

        # Generate template ID
        template_id = str(uuid.uuid4())

        # Parse variables in template
        variables = self._extract_template_variables(template_text)

        # Optional fields
        description = template_data.get('description', '')
        category = template_data.get('category', 'general')
        tags = template_data.get('tags', [])
        metadata = template_data.get('metadata', {})

        # Create template object
        template = {
            'id': template_id,
            'name': name,
            'text': template_text,
            'variables': variables,
            'description': description,
            'category': category,
            'tags': tags,
            'metadata': metadata,
            'created': datetime.utcnow().isoformat(),
            'updated': datetime.utcnow().isoformat()
        }

        # Store the template
        self.templates[template_id] = template

        # Track category
        self.categories.add(category)

        logger.info(f"Created template {template_id}")
        return template

    def get_template(self, template_id):
        """Get a template by ID."""
        if template_id not in self.templates:
            raise ResourceError(f"Template not found: {template_id}")

        logger.info(f"Retrieved template {template_id}")
        return self.templates[template_id]

    def render_template(self, template_id, variables):
        """Render a template with provided variables."""
        if template_id not in self.templates:
            raise ResourceError(f"Template not found: {template_id}")

        template = self.templates[template_id]
        template_text = template['text']

        # Check for required variables
        required_vars = template['variables']
        missing_vars = [var for var in required_vars if var not in variables]

        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

        # Replace variables in template
        rendered_text = template_text
        for var_name, var_value in variables.items():
            rendered_text = rendered_text.replace(f"{{{{{var_name}}}}}", str(var_value))

        logger.info(f"Rendered template {template_id}")

        return {
            'template_id': template_id,
            'template_name': template['name'],
            'variables': variables,
            'rendered_text': rendered_text
        }

    def _extract_template_variables(self, template_text):
        """Extract variable names from a template."""
        variable_pattern = r'\{\{([a-zA-Z0-9_]+)\}\}'
        matches = re.findall(variable_pattern, template_text)
        return list(set(matches))  # Return unique variable names