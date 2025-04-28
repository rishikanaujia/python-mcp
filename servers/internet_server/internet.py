import requests
import json
import urllib.parse
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.logging_utils import MCPLogger

logger = MCPLogger(service_name='internet-server')


class InternetConnector:
    """Internet connector for MCP Internet Server."""

    def __init__(self):
        """Initialize the internet connector."""
        self.rate_limits = {
            'requests_per_minute': int(os.environ.get('RATE_LIMIT_RPM', '60')),
            'data_per_minute_mb': float(os.environ.get('RATE_LIMIT_DPM', '10'))
        }

        self.request_history = []
        self.allowed_domains = self._parse_allowed_domains()
        self.blocked_domains = self._parse_blocked_domains()

    def _parse_allowed_domains(self):
        """Parse allowed domains from environment."""
        domains_str = os.environ.get('ALLOWED_DOMAINS', '')
        if domains_str:
            return [domain.strip() for domain in domains_str.split(',')]
        return []  # Empty list means all domains are allowed (subject to blocked domains)

    def _parse_blocked_domains(self):
        """Parse blocked domains from environment."""
        domains_str = os.environ.get('BLOCKED_DOMAINS', '')
        if domains_str:
            return [domain.strip() for domain in domains_str.split(',')]
        return []

    def _check_domain_access(self, url):
        """Check if access to domain is allowed."""
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc

        # Check blocked domains first
        for blocked in self.blocked_domains:
            if blocked in domain:
                logger.warn(f"Access to domain {domain} is blocked")
                return False

        # If allowed domains is empty, all non-blocked domains are allowed
        if not self.allowed_domains:
            return True

        # Check allowed domains
        for allowed in self.allowed_domains:
            if allowed in domain:
                return True

        logger.warn(f"Access to domain {domain} is not allowed")
        return False

    def _check_rate_limits(self):
        """Check if rate limits are exceeded."""
        # Clean up old requests
        current_time = datetime.utcnow()
        one_minute_ago = current_time.timestamp() - 60

        # Remove requests older than 1 minute
        self.request_history = [
            r for r in self.request_history if r['timestamp'] > one_minute_ago
        ]

        # Check request count
        if len(self.request_history) >= self.rate_limits['requests_per_minute']:
            logger.warn("Rate limit exceeded: too many requests per minute")
            return False

        # Check data transfer
        total_data_mb = sum(r['size_bytes'] for r in self.request_history) / (1024 * 1024)
        if total_data_mb >= self.rate_limits['data_per_minute_mb']:
            logger.warn("Rate limit exceeded: too much data per minute")
            return False

        return True

    def _record_request(self, url, size_bytes):
        """Record a request for rate limiting."""
        self.request_history.append({
            'timestamp': datetime.utcnow().timestamp(),
            'url': url,
            'size_bytes': size_bytes
        })

    def make_request(self, request_params):
        """Make an HTTP request to the internet."""
        url = request_params.get('url')
        method = request_params.get('method', 'GET').upper()
        headers = request_params.get('headers', {})
        data = request_params.get('data')
        timeout = request_params.get('timeout', 30)

        if not url:
            raise ValueError("URL is required")

        # Check domain access
        if not self._check_domain_access(url):
            raise ValueError(f"Access to URL {url} is not allowed")

        # Check rate limits
        if not self._check_rate_limits():
            raise ValueError("Rate limit exceeded")

        logger.info(f"Making {method} request to {url}")

        try:
            start_time = datetime.utcnow()

            # Make the request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=json.dumps(data) if data and method != 'GET' else None,
                params=data if data and method == 'GET' else None,
                timeout=timeout
            )

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            # Record request for rate limiting
            content_length = len(response.content)
            self._record_request(url, content_length)

            # Parse response
            try:
                response_data = response.json()
                content_type = 'application/json'
            except:
                try:
                    response_data = response.text
                    content_type = response.headers.get('Content-Type', 'text/plain')
                except:
                    response_data = None
                    content_type = 'application/octet-stream'

            # Log response
            logger.info(f"Received response from {url}", {
                'status': response.status_code,
                'size': content_length,
                'duration_ms': duration_ms
            })

            # Return response info
            return {
                'status': response.status_code,
                'headers': dict(response.headers),
                'data': response_data,
                'content_type': content_type,
                'content_length': content_length,
                'duration_ms': duration_ms,
                'url': response.url,
                'timestamp': datetime.utcnow().isoformat()
            }

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            raise ValueError(f"Request failed: {str(e)}")

    def search(self, query, search_params=None):
        """Perform a search query."""
        if not query:
            raise ValueError("Search query is required")

        # Default search parameters
        params = {
            'num_results': 10,
            'search_type': 'web',
            'safe_search': True
        }

        # Update with provided parameters
        if search_params:
            params.update(search_params)

        # For development: return mock search results
        logger.info(f"Performing search for query: {query}")

        # Mock search results
        results = []
        for i in range(params['num_results']):
            results.append({
                'title': f"Sample result {i + 1} for '{query}'",
                'url': f"https://example.com/result/{i + 1}",
                'snippet': f"This is a sample search result for the query '{query}'. "
                           f"Result number {i + 1} contains relevant information.",
                'position': i + 1
            })

        return {
            'query': query,
            'results': results,
            'total_results': params['num_results'],
            'search_type': params['search_type'],
            'timestamp': datetime.utcnow().isoformat()
        }
