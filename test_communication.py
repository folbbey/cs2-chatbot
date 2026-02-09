"""
Test script to verify client-server communication

This script tests the communication between the client and server
by simulating a message being sent from the client to the server.
"""

import requests
import json
import time
import threading
import sys


def test_server_health():
    """Test if the server is running and responding."""
    try:
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running and healthy")
            return True
        else:
            print(f"✗ Server returned unexpected status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to server: {e}")
        return False


def test_message_processing():
    """Test processing a message through the server."""
    test_messages = [
        {
            "is_team": False,
            "playername": "TestPlayer",
            "chattext": "@help"
        },
        {
            "is_team": True,
            "playername": "TestPlayer",
            "chattext": "Hello world"
        },
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\nTest {i}: Sending message: {msg['chattext']}")
        try:
            response = requests.post(
                "http://localhost:8080/process_message",
                json=msg,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                responses = data.get("responses", [])
                print(f"✓ Message processed successfully")
                print(f"  Received {len(responses)} response(s):")
                for resp in responses:
                    print(f"    - {'[TEAM]' if resp['is_team'] else '[ALL]'} {resp['text']}")
            else:
                print(f"✗ Server returned error: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")


def start_test_server():
    """Start the server for testing."""
    from server import run_server
    print("Starting test server...")
    run_server(host='127.0.0.1', port=8080)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    
    if mode == "start-server":
        # Just start the server and keep it running
        start_test_server()
    else:
        # Run tests (assumes server is already running)
        print("=" * 60)
        print("CS2 Chat Bot - Client/Server Communication Test")
        print("=" * 60)
        print("\nNote: Make sure the server is running before running tests.")
        print("Run 'python test_communication.py start-server' in another terminal.\n")
        
        time.sleep(1)
        
        # Test server health
        print("\n1. Testing server health endpoint...")
        if not test_server_health():
            print("\n✗ Server is not running. Start it with:")
            print("  python launcher.py server")
            sys.exit(1)
        
        # Test message processing
        print("\n2. Testing message processing...")
        test_message_processing()
        
        print("\n" + "=" * 60)
        print("Tests completed!")
        print("=" * 60)
