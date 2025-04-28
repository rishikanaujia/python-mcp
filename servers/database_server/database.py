import sqlite3
import psycopg2
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger
from common.error_handling import ResourceError

logger = MCPLogger(service_name='database-server')


class DatabaseConnector:
    """Database connector for MCP Database Server."""

    def __init__(self):
        """Initialize the database connector."""
        self.db_type = os.environ.get('DB_TYPE', 'sqlite')
        self.connection = None
        self.connected = False

        # Database configuration
        self.config = {
            'sqlite': {
                'db_path': os.environ.get('SQLITE_DB_PATH', 'mcp.db')
            },
            'postgres': {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': os.environ.get('DB_PORT', '5432'),
                'database': os.environ.get('DB_NAME', 'mcpdb'),
                'user': os.environ.get('DB_USER', 'postgres'),
                'password': os.environ.get('DB_PASSWORD', 'postgres')
            }
        }

    def connect(self):
        """Connect to the database."""
        if self.connected:
            return True

        try:
            if self.db_type == 'sqlite':
                self.connection = sqlite3.connect(self.config['sqlite']['db_path'])
                self.connection.row_factory = sqlite3.Row
            elif self.db_type == 'postgres':
                config = self.config['postgres']
                self.connection = psycopg2.connect(
                    host=config['host'],
                    port=config['port'],
                    database=config['database'],
                    user=config['user'],
                    password=config['password']
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")

            self.connected = True
            logger.info(f"Connected to {self.db_type} database")

            # Initialize database schema if needed
            self._initialize_schema()

            return True
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def disconnect(self):
        """Disconnect from the database."""
        if self.connected and self.connection:
            self.connection.close()
            self.connected = False
            self.connection = None
            logger.info("Disconnected from database")

    def execute_query(self, query, params=None, fetch=True):
        """Execute a SQL query."""
        if not self.connected:
            self.connect()

        try:
            cursor = self.connection.cursor()

            start_time = datetime.utcnow()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch:
                if self.db_type == 'sqlite':
                    # For SQLite with row_factory
                    results = [dict(row) for row in cursor.fetchall()]
                else:
                    # For PostgreSQL
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            else:
                results = None

            # Commit for write operations
            if not query.strip().lower().startswith('select'):
                self.connection.commit()

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Log query execution
            logger.info(f"Executed query in {duration_ms:.2f}ms", {
                'query': query[:100] + ('...' if len(query) > 100 else ''),
                'rowcount': cursor.rowcount
            })

            cursor.close()

            return {
                'results': results,
                'rowcount': cursor.rowcount,
                'duration_ms': duration_ms
            }
        except Exception as e:
            # Rollback on error
            self.connection.rollback()
            logger.error(f"Query execution error: {str(e)}", {'query': query})
            raise

    def _initialize_schema(self):
        """Initialize database schema if needed."""
        # Check if the tables exist
        if self.db_type == 'sqlite':
            tables_query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='mcp_requests'
            """
        else:  # postgres
            tables_query = """
                SELECT tablename FROM pg_catalog.pg_tables
                WHERE schemaname='public' AND tablename='mcp_requests'
            """

        result = self.execute_query(tables_query)

        if not result['results']:
            logger.info("Initializing database schema")

            # Create tables
            self.execute_query("""
                CREATE TABLE mcp_requests (
                    id VARCHAR(100) PRIMARY KEY,
                    request_type VARCHAR(50) NOT NULL,
                    payload TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    client_id VARCHAR(100),
                    session_id VARCHAR(100)
                )
            """, fetch=False)

            self.execute_query("""
                CREATE TABLE mcp_responses (
                    id VARCHAR(100) PRIMARY KEY,
                    request_id VARCHAR(100) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    server_id VARCHAR(20),
                    FOREIGN KEY (request_id) REFERENCES mcp_requests(id)
                )
            """, fetch=False)

            logger.info("Database schema initialized")

    def record_request(self, request_data):
        """Record a request in the database."""
        if not self.connected:
            self.connect()

        request_id = request_data.get('id')
        request_type = request_data.get('type')
        client_id = request_data.get('metadata', {}).get('source')
        session_id = request_data.get('metadata', {}).get('sessionId')

        # Convert payload to JSON string
        payload_json = json.dumps(request_data.get('payload', {}))

        query = """
            INSERT INTO mcp_requests (id, request_type, payload, client_id, session_id)
            VALUES (?, ?, ?, ?, ?)
        """

        if self.db_type == 'postgres':
            query = query.replace('?', '%s')

        self.execute_query(
            query,
            (request_id, request_type, payload_json, client_id, session_id),
            fetch=False
        )

        return {'requestId': request_id}

    def record_response(self, response_data):
        """Record a response in the database."""
        if not self.connected:
            self.connect()

        response_id = response_data.get('id')
        request_id = response_data.get('requestId')
        status = response_data.get('status')
        server_id = response_data.get('metadata', {}).get('source', '').split('-')[-1] if response_data.get('metadata',
                                                                                                            {}).get(
            'source') else None

        # Convert data to JSON string
        data_json = json.dumps(response_data.get('data', {}))

        query = """
            INSERT INTO mcp_responses (id, request_id, status, data, server_id)
            VALUES (?, ?, ?, ?, ?)
        """

        if self.db_type == 'postgres':
            query = query.replace('?', '%s')

        self.execute_query(
            query,
            (response_id, request_id, status, data_json, server_id),
            fetch=False
        )

        return {'responseId': response_id}

    def get_request_history(self, filters=None, limit=100, offset=0):
        """Get request history with optional filters."""
        if not self.connected:
            self.connect()

        query_conditions = []
        query_params = []

        # Build the query based on filters
        if filters:
            if 'client_id' in filters:
                query_conditions.append("client_id = ?")
                query_params.append(filters['client_id'])

            if 'session_id' in filters:
                query_conditions.append("session_id = ?")
                query_params.append(filters['session_id'])

            if 'request_type' in filters:
                query_conditions.append("request_type = ?")
                query_params.append(filters['request_type'])

            if 'start_date' in filters:
                query_conditions.append("created_at >= ?")
                query_params.append(filters['start_date'])

            if 'end_date' in filters:
                query_conditions.append("created_at <= ?")
                query_params.append(filters['end_date'])

        # Build the WHERE clause
        where_clause = " WHERE " + " AND ".join(query_conditions) if query_conditions else ""

        # Query for total count
        count_query = f"SELECT COUNT(*) as count FROM mcp_requests{where_clause}"

        if self.db_type == 'postgres':
            count_query = count_query.replace('?', '%s')

        count_result = self.execute_query(count_query, query_params)
        total_count = count_result['results'][0]['count']

        # Query for requests with pagination
        query = f"""
            SELECT r.id, r.request_type, r.payload, r.created_at, r.client_id, r.session_id,
                   resp.id as response_id, resp.status, resp.data, resp.created_at as response_time, resp.server_id
            FROM mcp_requests r
            LEFT JOIN mcp_responses resp ON r.id = resp.request_id
            {where_clause}
            ORDER BY r.created_at DESC
            LIMIT {limit} OFFSET {offset}
        """

        if self.db_type == 'postgres':
            query = query.replace('?', '%s')

        result = self.execute_query(query, query_params)

        # Process results
        requests = []
        for row in result['results']:
            # Parse JSON strings
            payload = json.loads(row['payload']) if row['payload'] else {}
            response_data = json.loads(row['data']) if row.get('data') else None

            request_info = {
                'id': row['id'],
                'type': row['request_type'],
                'payload': payload,
                'timestamp': row['created_at'],
                'clientId': row['client_id'],
                'sessionId': row['session_id'],
                'response': {
                    'id': row.get('response_id'),
                    'status': row.get('status'),
                    'data': response_data,
                    'timestamp': row.get('response_time'),
                    'serverId': row.get('server_id')
                } if row.get('response_id') else None
            }

            requests.append(request_info)

        return {
            'requests': requests,
            'total': total_count,
            'limit': limit,
            'offset': offset
        }