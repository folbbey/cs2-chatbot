"""
Discord Bot Launcher

Starts the Discord client adapter with the backend server.
"""
import os
import threading
import time
from client.adapters.discord import DiscordClient
from server import run_server


def start_server():
    """Start the backend server in a separate thread."""
    print("Starting backend server...")
    run_server()


def start_discord_client():
    """Start the Discord client."""
    # Initialize and run the Discord client
    client = DiscordClient(server_url="http://127.0.0.1:8080")
    client.run_bot()


if __name__ == "__main__":
    # Start the backend server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(2)
    
    # Start Discord client on the main thread
    print("Starting Discord client...")
    start_discord_client()
