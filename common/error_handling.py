class MCPError(Exception):
    """Base class for MCP errors."""

    def __init__(self, message, **options):
        super().__init__(message)
        self.name = options.get('name', 'MCPError')
        self.code = options.get('code', 'INTERNAL_ERROR')
        self.status = options.get('status', 500)
        self.data = options.get('data', None)

    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'code': self.code,
            'message': str(self),
            'status': self.status,
            'data': self.data
        }


class RequestError(MCPError):
    """Error for invalid requests."""

    def __init__(self, message, **options):
        options.setdefault('name', 'RequestError')
        options.setdefault('code', 'INVALID_REQUEST')
        options.setdefault('status', 400)
        super().__init__(message, **options)


class AuthenticationError(MCPError):
    """Error for authentication failures."""

    def __init__(self, message, **options):
        options.setdefault('name', 'AuthenticationError')
        options.setdefault('code', 'AUTHENTICATION_FAILED')
        options.setdefault('status', 401)
        super().__init__(message, **options)


class ResourceError(MCPError):
    """Error for resource access issues."""

    def __init__(self, message, **options):
        options.setdefault('name', 'ResourceError')
        options.setdefault('code', 'RESOURCE_ERROR')
        options.setdefault('status', 500)
        super().__init__(message, **options)


class TimeoutError(MCPError):
    """Error for request timeouts."""

    def __init__(self, message, **options):
        options.setdefault('name', 'TimeoutError')
        options.setdefault('code', 'REQUEST_TIMEOUT')
        options.setdefault('status', 504)
        super().__init__(message, **options)
