import json
import threading
import queue
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_utils import MCPLogger
from common.protocol import MCPProtocol

logger = MCPLogger(service_name='notifications-handler')


class NotificationsHandler:
    """SSE Notifications handler for MCP."""

    def __init__(self):
        """Initialize the notifications handler."""
        self.clients = {}
        self.notification_queues = {}
        self.lock = threading.Lock()

    def register_client(self, client_id, response):
        """Register a client for notifications."""
        with self.lock:
            # Create notification queue for this client
            self.notification_queues[client_id] = queue.Queue()

            # Store the client connection
            self.clients[client_id] = response

            logger.info(f"Client {client_id} registered for notifications")

            # Send initial connection message
            initial_notification = MCPProtocol.create_notification(
                'connected',
                {
                    'clientId': client_id,
                    'timestamp': datetime.utcnow().isoformat()
                },
                source='session-manager'
            )

            self._send_event(response, initial_notification)

    def unregister_client(self, client_id):
        """Unregister a client."""
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]

                if client_id in self.notification_queues:
                    del self.notification_queues[client_id]

                logger.info(f"Client {client_id} unregistered from notifications")
                return True
            return False

    def send_notification(self, client_id, notification_data):
        """Send a notification to a client."""
        with self.lock:
            if client_id not in self.clients:
                logger.debug(f"Cannot send notification: client {client_id} not registered")
                return False

            # Get the client's response object
            response = self.clients[client_id]

            # Create notification using protocol
            notification = MCPProtocol.create_notification(
                notification_data.get('type', 'event'),
                notification_data,
                source='session-manager'
            )

            try:
                # Add to the client's notification queue
                if client_id in self.notification_queues:
                    self.notification_queues[client_id].put(notification)

                # Send directly to client
                self._send_event(response, notification)

                logger.debug(f"Notification sent to client {client_id}",
                             {'type': notification_data.get('type')})
                return True
            except Exception as e:
                logger.error(f"Error sending notification to client {client_id}: {str(e)}")
                # Client connection might be broken, unregister
                self.unregister_client(client_id)
                return False

    def broadcast_notification(self, notification_data):
        """Broadcast a notification to all clients."""
        # Create notification using protocol
        notification = MCPProtocol.create_notification(
            notification_data.get('type', 'broadcast'),
            notification_data,
            source='session-manager'
        )

        sent_count = 0

        with self.lock:
            for client_id, response in list(self.clients.items()):
                try:
                    # Add to client's notification queue
                    if client_id in self.notification_queues:
                        self.notification_queues[client_id].put(notification)

                    # Send to client
                    self._send_event(response, notification)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to client {client_id}: {str(e)}")
                    # Client connection might be broken, unregister
                    self.unregister_client(client_id)

        logger.info(f"Broadcast notification sent to {sent_count} clients",
                    {'type': notification_data.get('type')})

        return sent_count

    def get_client_notifications(self, client_id, max_count=None):
        """Get pending notifications for a client."""
        if client_id not in self.notification_queues:
            return []

        notifications = []
        q = self.notification_queues[client_id]

        # Get notifications up to max_count (or all if max_count is None)
        count = 0
        while not q.empty() and (max_count is None or count < max_count):
            notifications.append(q.get())
            count += 1

        return notifications

    def _send_event(self, response, data):
        """Send an SSE event to the client."""
        try:
            event_data = f"data: {json.dumps(data)}\n\n"
            response.write(event_data)
            response.flush()
        except Exception as e:
            logger.error(f"Error sending SSE event: {str(e)}")
            raise

    def get_client_count(self):
        """Get the number of connected clients."""
        return len(self.clients)

    def is_client_connected(self, client_id):
        """Check if a client is connected."""
        return client_id in self.clients