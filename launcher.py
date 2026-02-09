"""
Launcher script for CS2 Chat Bot

This script allows you to run the client and server separately or together.

Usage:
    python launcher.py both      # Run both client and server (default)
    python launcher.py client    # Run only the client
    python launcher.py server    # Run only the server
"""

import sys
import threading
import time


def start_server():
    """Start the backend server."""
    from server import run_server
    print("Starting backend server...")
    run_server(host='127.0.0.1', port=8080)


def start_client():
    """Start the CS2 client."""
    from client.adapters.cs2 import CS2Client
    print("Starting CS2 client...")
    client = CS2Client(server_url="http://127.0.0.1:8080")
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("Shutting down client...")
        client.stop()


def run_both():
    """Run both server and client."""
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Run client on main thread
    start_client()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    
    if mode == "server":
        start_server()
    elif mode == "client":
        start_client()
    elif mode == "both":
        run_both()
    else:
        print(f"Unknown mode: {mode}")
        print(__doc__)
        sys.exit(1)
