import requests
import os
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='llm-interface')

class LLMInterface:
    """LLM Interface for MCP Client."""

    def __init__(self):
        self.api_key = os.environ.get('LLM_API_KEY')
        self.api_url = os.environ.get('LLM_API_URL')
        logger.error(f'{self.api_key}, {self.api_url}')
        self.initialized = False
        self.status = 'disconnected'

    def initialize(self):
        """Initialize the LLM."""
        logger.info('Initializing LLM Interface')

        # If API key and URL are provided, use external LLM
        if self.api_key and self.api_url:
            try:
                # Test connection
                headers = {'Authorization': f"Bearer {self.api_key}"}
                requests.get(self.api_url, headers=headers)

                self.initialized = True
                self.status = 'connected'
                logger.info('Connected to external LLM API')
            except Exception as e:
                logger.error(f'Failed to connect to external LLM API: {str(e)}')
                self.status = 'error'
                raise Exception(f"LLM connection error: {str(e)}")
        else:
            # Use mock LLM for development
            logger.info('Using mock LLM (no API credentials provided)')
            self.initialized = True
            self.status = 'mock'

        return {'status': self.status}

    # Update the process method in client/llm.py

    def process(self, prompt):
        """Process a prompt through the LLM."""
        if not self.initialized:
            raise Exception('LLM not initialized')

        logger.info('Processing prompt through LLM', {'promptLength': len(prompt)})

        # If using external LLM
        if self.status == 'connected':
            try:
                # Detect if it's an Anthropic API by checking the URL
                is_anthropic = 'anthropic.com' in self.api_url.lower()

                if is_anthropic:
                    # Anthropic Claude API format
                    headers = {
                        'x-api-key': self.api_key,  # Anthropic uses x-api-key not Authorization
                        'Content-Type': 'application/json',
                        'anthropic-version': '2023-06-01'  # Include API version
                    }

                    payload = {
                        'model': 'claude-3-opus-20240229',  # Use an appropriate Claude model
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ],
                        'max_tokens': 1000
                    }
                else:
                    # OpenAI or other API format (default)
                    headers = {
                        'Authorization': f"Bearer {self.api_key}",
                        'Content-Type': 'application/json'
                    }

                    payload = {
                        'model': 'gpt-4',  # Default to GPT-4 for OpenAI
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ],
                        'max_tokens': 1000,
                        'temperature': 0.7
                    }

                # Make the API request
                response = requests.post(self.api_url, json=payload, headers=headers)

                if response.status_code != 200:
                    error_msg = f"LLM API error: {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                result = response.json()
                logger.info('Received response from LLM API')

                # Extract the response text based on API type
                if is_anthropic:
                    response_text = result['content'][0]['text']
                else:
                    response_text = result['choices'][0]['message']['content']

                return {'result': response_text}

            except Exception as e:
                logger.error(f'LLM API error: {str(e)}')
                raise Exception(f"LLM processing error: {str(e)}")

        # If using mock LLM
        elif self.status == 'mock':
            # Simulate processing delay
            time.sleep(0.5)

            # Generate mock response
            mock_response = f"This is a mock LLM response to: \"{prompt[:50]}...\""

            logger.info('Generated mock LLM response')
            return {'result': mock_response}

        else:
            raise Exception(f"LLM in invalid state: {self.status}")

    def shutdown(self):
        """Shut down the LLM."""
        logger.info('Shutting down LLM Interface')
        self.initialized = False
        self.status = 'disconnected'
        return {'status': self.status}

    def get_status(self):
        """Get LLM status."""
        return {
            'initialized': self.initialized,
            'status': self.status
        }
