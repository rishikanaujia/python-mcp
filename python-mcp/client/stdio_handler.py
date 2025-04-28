import sys
import datetime
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='stdio-handler')

class STDIOHandler:
    """Standard I/O Handler for MCP Client."""

    def __init__(self):
        self.input_buffer = []
        self.output_listeners = []

    def handle_input(self, input_text):
        """Handle input from stdin."""
        logger.debug('Handling input', {'inputLength': len(input_text)})

        # Store input in buffer
        self.input_buffer.append({
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'text': input_text
        })

        return input_text

    def send_output(self, output):
        """Send output to stdout."""
        logger.debug('Sending output', {'outputLength': len(output)})

        # Notify all output listeners
        for listener in self.output_listeners:
            try:
                listener(output)
            except Exception as e:
                logger.error(f'Error in output listener: {str(e)}')

        print(output)

    def add_output_listener(self, listener):
        """Add output listener."""
        if callable(listener):
            self.output_listeners.append(listener)

    def remove_output_listener(self, listener):
        """Remove output listener."""
        if listener in self.output_listeners:
            self.output_listeners.remove(listener)

    def get_input_history(self, limit=10):
        """Get input history."""
        return self.input_buffer[-limit:] if limit > 0 else self.input_buffer

    def clear_input_buffer(self):
        """Clear input buffer."""
        self.input_buffer = []
