import os
import sys
import logging
from flask import Flask, request, jsonify
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.config import load_config, copy_files_to_appdata
from util.commands import command_registry
from util.module_registry import module_registry
from util.database import initialize_pool, close_pool


def resource_path(relative_path):
    """Get the absolute path to a resource, works for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path)


class BotServer:
    """Server that handles bot command and module processing."""
    
    def __init__(self):
        """Initialize the bot server."""
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # File handler for logging to a file
        file_handler = logging.FileHandler("bot_server.log")
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        
        # Stream handler for logging to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        # Add both handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Load configuration
        self.config = load_config()
        self.prefix = self.config.get("command_prefix", "@")
        
        # Initialize database connection pool
        self.logger.info("Initializing database connection pool...")
        try:
            initialize_pool()
            self.logger.info("Database connection pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise
        
        # Initialize command and module registries
        self.commands = command_registry
        self.commands.set_logger(self.logger)
        self.modules = module_registry
        self.modules.set_logger(self.logger)
        
        # Response queue for collecting responses during command execution
        self._response_queue = []
        
        # Load commands and modules
        if hasattr(sys, '_MEIPASS'):
            copy_files_to_appdata()
            
        self.load_commands()
        self.load_modules()
        
    def load_commands(self):
        """Load commands from the 'cmds' directory."""
        commands_dir = resource_path("cmds")
        self.commands.load_commands(commands_dir)
        self.logger.info(f"Loaded {len(self.commands)} commands from {commands_dir}")
        
    def load_modules(self):
        """Load modules from the 'modules' directory."""
        modules_dir = resource_path("modules")
        if not os.path.exists(modules_dir):
            return
        self.modules.load_modules(modules_dir)
        self.logger.info(f"Loaded {len(self.modules)} modules from {modules_dir}")
        
    def process_message(self, is_team: bool, playername: str, chattext: str) -> List[Dict]:
        """Process a message and return list of responses."""
        import time
        start_time = time.time()
        
        # Clear response queue for this message
        self._response_queue = []
        
        # Pass to modules that are reading input
        module_start = time.time()
        for module_name, module_instance in self.modules.modules.items():
            if hasattr(module_instance, "process") and getattr(module_instance, "reading_input", True):
                try:
                    response = module_instance.process(playername, is_team, chattext)
                    if response:
                        self._response_queue.append({
                            "is_team": is_team,
                            "text": f"{playername}: {response}"
                        })
                except Exception as e:
                    self.logger.error(f"Error in module '{module_name}' while processing: {e}")
        module_time = time.time() - module_start
                    
        # Process commands if the line contains the command prefix
        if chattext.startswith(self.prefix):
            try:
                command_start = time.time()
                command_name = chattext[len(self.prefix):].split(" ")[0]
                command_args = chattext[len(self.prefix) + len(command_name):].strip()
                
                self.logger.info(f"Executing command: {command_name} with args: {command_args}")
                res = self.commands.execute(command_name, self, is_team, playername, command_args)
                
                if isinstance(res, str):
                    self._response_queue.append({
                        "is_team": is_team,
                        "text": res
                    })
                command_time = time.time() - command_start
                self.logger.info(f"Command execution took {command_time:.4f}s")
            except Exception as e:
                import traceback
                self.logger.error(f"Error executing command: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return collected responses
        responses = self._response_queue
        self._response_queue = []
        
        total_time = time.time() - start_time
        self.logger.info(f"Total processing time: {total_time:.4f}s (modules: {module_time:.4f}s)")
        
        return responses
        
    def add_to_chat_queue(self, is_team: bool, chattext: str) -> None:
        """Compatibility method for commands that expect this method."""
        # Commands call this to queue responses - we collect them in _response_queue
        self._response_queue.append({
            "is_team": is_team,
            "text": chattext
        })


# Create Flask app
app = Flask(__name__)
bot_server = None


@app.route('/process_message', methods=['POST'])
def process_message():
    """Handle incoming messages from the client."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        is_team = data.get('is_team', False)
        playername = data.get('playername', '')
        chattext = data.get('chattext', '')
        
        if not playername or not chattext:
            return jsonify({"error": "Missing required fields"}), 400
            
        # Process the message
        responses = bot_server.process_message(is_team, playername, chattext)
        
        return jsonify({"responses": responses}), 200
        
    except Exception as e:
        app.logger.error(f"Error processing message: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


def run_server(host='127.0.0.1', port=8080):
    """Run the Flask server."""
    global bot_server
    bot_server = BotServer()
    app.logger.info(f"Starting bot server on {host}:{port}")
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    run_server()
