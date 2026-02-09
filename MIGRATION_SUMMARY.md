# Migration Summary: Client-Server Architecture

## Overview
The CS2 chatbot has been restructured from a monolithic architecture to a client-server architecture. This document summarizes all changes made.

## New Files Created

### 1. Client Adapter
- `client/__init__.py` - Client package initialization
- `client/adapters/cs2/__init__.py` - CS2 adapter package initialization
- `client/adapters/cs2/cs2_client.py` - Main CS2 client adapter class

**Purpose**: Handles all CS2-specific operations (console log reading, chat sending, window interaction)

### 2. Server
- `server/__init__.py` - Server package initialization
- `server/server.py` - Flask web server with command/module processing

**Purpose**: Handles business logic, command execution, and module processing

### 3. Documentation
- `ARCHITECTURE.md` - High-level architecture overview
- `COMMUNICATION_FLOW.md` - Detailed message flow and structure
- `launcher.py` - Flexible launcher script for different modes
- `test_communication.py` - Test script for client-server communication

## Modified Files

### 1. `cs2chatbot.py`
**Before**: Imported and ran the monolithic Bot class
**After**: Starts both server and client in separate threads

### 2. `requirements.txt`
**Added dependencies**:
- `flask` - Web server framework
- `requests` - HTTP client library

### 3. `cs2chatbot.spec`
**Updated** to include new directories:
- `('client', 'client')`
- `('server', 'server')`

**Updated hidden imports**:
- `flask`
- `requests`
- `client.adapters.cs2`
- `server`

### 4. `README.md`
**Added**:
- Architecture overview
- Multiple running modes
- Links to additional documentation

## Architecture Changes

### Before (Monolithic)
```
Bot Class
├── CS2 Window Connection
├── Console Log Reading
├── Chat Queue Management
├── Key Simulation
├── Command Processing
└── Module Processing
```

### After (Client-Server)
```
CS2 Client                          Server
├── CS2 Window Connection     ◄──►  ├── Command Processing
├── Console Log Reading             ├── Module Processing
├── Chat Queue Management           └── Response Collection
├── Key Simulation
└── HTTP Client
```

## Key Changes in Logic

### 1. Message Processing Flow
**Before**: All processing happened in one place (Bot.run())
**After**: 
1. Client reads console log
2. Client sends HTTP POST to server
3. Server processes through modules/commands
4. Server returns responses
5. Client queues responses for CS2

### 2. Command Execution
**Before**: Commands called `bot.add_to_chat_queue()` directly
**After**: Commands still call `bot.add_to_chat_queue()`, but in server context this adds to `_response_queue` which is returned via HTTP

### 3. Bot Class Split
- **util/bot.py**: Original Bot class (can be deprecated but kept for reference)
- **client/adapters/cs2/cs2_client.py**: CS2-specific functionality
- **server/server.py**: BotServer class with business logic

## Running Modes

### Mode 1: Combined (Default)
```bash
python cs2chatbot.py
```
Runs both server and client in the same process

### Mode 2: Separate Processes
```bash
# Terminal 1
python launcher.py server

# Terminal 2
python launcher.py client
```
Runs server and client independently

### Mode 3: Testing
```bash
# Terminal 1
python launcher.py server

# Terminal 2
python test_communication.py
```
Test server without CS2 running

## Benefits of New Architecture

1. **Modularity**: Game-specific code is isolated
2. **Testability**: Server can be tested without game running
3. **Scalability**: Multiple clients could connect to one server
4. **Maintainability**: Changes to business logic don't affect client
5. **Debugging**: Components can be debugged separately
6. **Future-proofing**: Easy to add adapters for other games

## Migration Path for Other Games

To support a different game (e.g., TF2, CSGO):

1. Create new adapter: `client/adapters/tf2/tf2_client.py`
2. Implement the same interface as CS2Client
3. Server code remains unchanged
4. Commands and modules remain unchanged

## Backwards Compatibility

The original `util/bot.py` file is preserved for reference but is no longer used by the main application. All functionality has been migrated to the new architecture.

## What Remains the Same

- Command implementations (`cmds/`)
- Module implementations (`modules/`)
- Utility functions (`util/`)
- Configuration (`config.toml`)
- Database structure (`db/`)

## Testing Checklist

- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Run server: `python launcher.py server`
- [ ] Run client: `python launcher.py client`
- [ ] Test commands in CS2 chat
- [ ] Verify responses appear in game
- [ ] Test pause/resume hotkeys
- [ ] Run communication tests: `python test_communication.py`

## Troubleshooting

### Server won't start
- Check if port 5000 is available
- Check if Flask is installed: `pip install flask`

### Client can't connect to server
- Verify server is running: `http://localhost:5000/health`
- Check firewall settings
- Ensure server_url in client is correct

### Commands not responding
- Check server logs in `bot_server.log`
- Check client logs in `cs2_client.log`
- Verify command prefix in `config.toml`
