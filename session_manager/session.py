import uuid
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='session-manager')


class Session:
    """Session management for MCP."""

    def __init__(self, session_id, client_id):
        """Initialize a new session."""
        self.id = session_id
        self.client_id = client_id
        self.created = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.active_requests = {}
        self.metadata = {}

    @classmethod
    def create(cls, client_id):
        """Create a new session with a unique ID."""
        session_id = str(uuid.uuid4())
        logger.info(f"Creating new session {session_id} for client {client_id}")
        return cls(session_id, client_id)

    def add_request(self, request_id, request):
        """Add an active request to the session."""
        self.active_requests[request_id] = {
            'timestamp': datetime.utcnow(),
            'request': request
        }
        self.update_activity()
        logger.debug(f"Added request {request_id} to session {self.id}")

    def remove_request(self, request_id):
        """Remove a request from the session."""
        if request_id in self.active_requests:
            del self.active_requests[request_id]
            self.update_activity()
            logger.debug(f"Removed request {request_id} from session {self.id}")
            return True
        return False

    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()

    def is_inactive(self, timeout_seconds=1800):
        """Check if the session has been inactive for a period."""
        inactive_time = (datetime.utcnow() - self.last_activity).total_seconds()
        return inactive_time > timeout_seconds

    def get_info(self):
        """Get session information."""
        return {
            'id': self.id,
            'clientId': self.client_id,
            'created': self.created.isoformat(),
            'lastActivity': self.last_activity.isoformat(),
            'activeRequestCount': len(self.active_requests),
            'metadata': self.metadata
        }

    def set_metadata(self, key, value):
        """Set metadata value."""
        self.metadata[key] = value
        self.update_activity()

    def get_metadata(self, key, default=None):
        """Get metadata value."""
        return self.metadata.get(key, default)


class SessionManager:
    """Manager for multiple MCP sessions."""

    def __init__(self):
        """Initialize the session manager."""
        self.sessions = {}

    def create_session(self, client_id):
        """Create a new session."""
        session = Session.create(client_id)
        self.sessions[session.id] = session
        return session

    def get_session(self, session_id):
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def close_session(self, session_id):
        """Close and remove a session."""
        if session_id in self.sessions:
            logger.info(f"Closing session {session_id}")
            del self.sessions[session_id]
            return True
        return False

    def cleanup_inactive_sessions(self, timeout_seconds=1800):
        """Clean up inactive sessions."""
        inactive_sessions = []

        for session_id, session in self.sessions.items():
            if session.is_inactive(timeout_seconds):
                inactive_sessions.append(session_id)

        for session_id in inactive_sessions:
            client_id = self.sessions[session_id].client_id
            self.close_session(session_id)
            logger.info(f"Closed inactive session {session_id} for client {client_id}")

        return len(inactive_sessions)

    def get_client_sessions(self, client_id):
        """Get all sessions for a client."""
        return {
            session_id: session for session_id, session in self.sessions.items()
            if session.client_id == client_id
        }

    def get_session_count(self):
        """Get the total number of active sessions."""
        return len(self.sessions)