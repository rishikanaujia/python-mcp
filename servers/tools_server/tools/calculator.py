class Calculator:
    """Calculator tool for MCP."""

    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract b from a."""
        return a - b

    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b

    def divide(self, a, b):
        """Divide a by b."""
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    def power(self, a, b):
        """Calculate a raised to the power of b."""
        return a ** b