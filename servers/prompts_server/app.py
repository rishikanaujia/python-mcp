from flask import Flask, request, jsonify
import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol
from prompts import PromptsManager

# Initialize logger
logger = MCPLogger(service_name='prompts-server')

# Create Flask app
app = Flask(__name__)

# Configuration
PORT = int(os.environ.get('PORT', 5007))
SERVER_ID = os.environ.get('SERVER_ID', '7')
CAPABILITIES = os.environ.get('CAPABILITIES', 'prompts').split(',')

logger.info(f"Initializing MCP Server {SERVER_ID} with capabilities: {', '.join(CAPABILITIES)}")

# Initialize prompts manager
prompts_manager = PromptsManager()


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
        if request_data.get('type') == 'prompt-management':
            payload = request_data.get('payload', {})
            action = payload.get('action')

            if not action:
                raise ValueError("Action is required for prompt management")

            # Handle different prompt management actions
            if action == 'create_prompt':
                prompt_data = payload.get('prompt_data', {})
                result = prompts_manager.create_prompt(prompt_data)
                logger.info(f"Created prompt {result.get('id')}")

            elif action == 'get_prompt':
                prompt_id = payload.get('prompt_id')
                result = prompts_manager.get_prompt(prompt_id)
                logger.info(f"Retrieved prompt {prompt_id}")

            elif action == 'update_prompt':
                prompt_id = payload.get('prompt_id')
                updates = payload.get('updates', {})
                result = prompts_manager.update_prompt(prompt_id, updates)
                logger.info(f"Updated prompt {prompt_id}")

            elif action == 'delete_prompt':
                prompt_id = payload.get('prompt_id')
                result = prompts_manager.delete_prompt(prompt_id)
                logger.info(f"Deleted prompt {prompt_id}")

            elif action == 'list_prompts':
                filters = payload.get('filters', {})
                limit = payload.get('limit', 100)
                offset = payload.get('offset', 0)
                result = prompts_manager.list_prompts(filters, limit, offset)
                logger.info(f"Listed prompts with filters: {filters}")

            elif action == 'get_categories':
                result = {'categories': prompts_manager.get_categories()}
                logger.info("Retrieved prompt categories")

            elif action == 'create_template':
                template_data = payload.get('template_data', {})
                result = prompts_manager.create_template(template_data)
                logger.info(f"Created template {result.get('id')}")

            elif action == 'get_template':
                template_id = payload.get('template_id')
                result = prompts_manager.get_template(template_id)
                logger.info(f"Retrieved template {template_id}")

            elif action == 'render_template':
                template_id = payload.get('template_id')
                variables = payload.get('variables', {})
                result = prompts_manager.render_template(template_id, variables)
                logger.info(f"Rendered template {template_id}")

            else:
                raise ValueError(f"Unsupported action: {action}")

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
    # Get counts of prompts and templates
    prompt_count = len(prompts_manager.prompts)
    template_count = len(prompts_manager.templates)
    categories = prompts_manager.get_categories()

    return jsonify({
        'status': 'healthy',
        'serverId': SERVER_ID,
        'capabilities': CAPABILITIES,
        'timestamp': datetime.utcnow().isoformat(),
        'prompts': {
            'promptCount': prompt_count,
            'templateCount': template_count,
            'categories': categories
        }
    })


# Start the server
if __name__ == '__main__':
    logger.info(f"MCP Server {SERVER_ID} running on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)