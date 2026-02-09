import os
import threading
import sys
from client.adapters.cs2 import CS2Client
from server import run_server

def start_server():
    """Start the backend server in a separate thread."""
    run_server(host='127.0.0.1', port=8080)

def start_client(client):
    """Start the CS2 client logic."""
    client.run()

if __name__ == "__main__":
    # Start the backend server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give the server a moment to start
    import time
    time.sleep(2)
    
    # Initialize and run the CS2 client on the main thread
    client = CS2Client(server_url="http://127.0.0.1:8080")
    
    # Start client in a separate thread
    client_thread = threading.Thread(target=start_client, args=(client,))
    client_thread.daemon = True
    client_thread.start()
    
    # Keep the main thread alive
    try:
        import keyboard
        keyboard.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
        client.stop()




