#!/usr/bin/env python3
"""
Test script for the database server integration.
This script tests the SQLite database functionality of the MCP architecture.
"""

import requests
import json
import sys
import os
import time
from datetime import datetime


def initialize_client():
    """Initialize the MCP client and create a session."""
    print("\n=== Initializing MCP Client ===")
    response = requests.post('http://localhost:8080/initialize')

    if response.status_code == 200:
        result = response.json()
        print(f"Client initialized with session ID: {result.get('sessionId')}")
        return True
    else:
        print(f"Failed to initialize client: {response.text}")
        return False


def test_basic_query():
    """Test a basic database query."""
    print("\n=== Testing Basic Database Query ===")

    # Example: Simple query to show current date
    response = requests.post('http://localhost:8080/tools', json={
        'tool': 'database',
        'operation': 'query',
        'params': {
            'query': "SELECT date('now') as current_date"
        }
    })

    if response.status_code == 200:
        result = response.json()
        print(f"Query result: {json.dumps(result, indent=2)}")
        return True
    else:
        print(f"Query failed: {response.text}")
        return False


def test_create_table():
    """Test creating a table in the database."""
    print("\n=== Testing Table Creation ===")

    # Create a test table
    response = requests.post('http://localhost:8080/tools', json={
        'tool': 'database',
        'operation': 'query',
        'params': {
            'query': """
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'fetch': False
        }
    })

    if response.status_code == 200:
        print("Table created successfully")
        return True
    else:
        print(f"Table creation failed: {response.text}")
        return False


def test_insert_data():
    """Test inserting data into the database."""
    print("\n=== Testing Data Insertion ===")

    # Insert test data
    test_data = [
        ("Test Item 1", 10.5),
        ("Test Item 2", 20.75),
        ("Test Item 3", 30.0)
    ]

    success = True

    for name, value in test_data:
        response = requests.post('http://localhost:8080/tools', json={
            'tool': 'database',
            'operation': 'query',
            'params': {
                'query': "INSERT INTO test_table (name, value) VALUES (?, ?)",
                'params': [name, value],
                'fetch': False
            }
        })

        if response.status_code != 200:
            print(f"Data insertion failed: {response.text}")
            success = False
            break

    if success:
        print(f"Inserted {len(test_data)} records successfully")

    return success


def test_query_data():
    """Test querying data from the database."""
    print("\n=== Testing Data Query ===")

    # Query the inserted data
    response = requests.post('http://localhost:8080/tools', json={
        'tool': 'database',
        'operation': 'query',
        'params': {
            'query': "SELECT * FROM test_table ORDER BY id"
        }
    })

    if response.status_code == 200:
        result = response.json()
        data = result.get('data', {}).get('result', {}).get('results', [])
        print(f"Retrieved {len(data)} records:")
        for row in data:
            print(f"  ID: {row.get('id')}, Name: {row.get('name')}, Value: {row.get('value')}")
        return True
    else:
        print(f"Data query failed: {response.text}")
        return False


def test_request_history():
    """Test retrieving request history from the database."""
    print("\n=== Testing Request History ===")

    # Query the request history
    response = requests.post('http://localhost:8080/tools', json={
        'tool': 'database',
        'operation': 'history',
        'params': {
            'limit': 10,
            'offset': 0
        }
    })

    if response.status_code == 200:
        result = response.json()
        history = result.get('data', {}).get('history', {})
        requests_list = history.get('requests', [])
        total = history.get('total', 0)

        print(f"Retrieved {len(requests_list)} requests out of {total} total:")
        for req in requests_list:
            print(f"  ID: {req.get('id')}, Type: {req.get('type')}, Client: {req.get('clientId')}")

        return True
    else:
        print(f"History query failed: {response.text}")
        return False


def main():
    """Main test function."""
    print("=== MCP Database Server Test ===")

    # First initialize the client
    if not initialize_client():
        print("Initialization failed, aborting tests.")
        return

    # Wait a moment for initialization to complete
    time.sleep(1)

    # Run the tests
    tests = [
        ("Basic Query", test_basic_query),
        ("Create Table", test_create_table),
        ("Insert Data", test_insert_data),
        ("Query Data", test_query_data),
        ("Request History", test_request_history)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nRunning test: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"Test threw an exception: {str(e)}")
            results.append((test_name, False))

    # Print test summary
    print("\n=== Test Summary ===")
    all_passed = True
    for test_name, success in results:
        status = "PASSED" if success else "FAILED"
        if not success:
            all_passed = False
        print(f"{test_name}: {status}")

    if all_passed:
        print("\nAll tests passed successfully!")
    else:
        print("\nSome tests failed.")


if __name__ == "__main__":
    main()