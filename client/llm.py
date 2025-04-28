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

    def process(self, prompt):
        """Process a prompt through the LLM."""
        if not self.initialized:
            raise Exception('LLM not initialized')

        logger.info('Processing prompt through LLM', {'promptLength': len(prompt)})

        # If using external LLM
        if self.status == 'connected':
            try:
                headers = {
                    'Authorization': f"Bearer {self.api_key}",
                    'Content-Type': 'application/json'
                }

                payload = {
                    'prompt': prompt,
                    'max_tokens': 1000,
                    'temperature': 0.7
                }

                response = requests.post(self.api_url, json=payload, headers=headers)

                if response.status_code != 200:
                    raise Exception(f"LLM API error: {response.text}")

                result = response.json()
                logger.info('Received response from LLM API')

                return {'result': result['choices'][0]['text'].strip()}

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