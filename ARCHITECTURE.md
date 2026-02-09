# CS2 Chat Bot - Client/Server Architecture

This bot now uses a client-server architecture:

- **Client** (`./client/adapters/cs2/`): Handles CS2-specific interactions (reading console log, sending chat messages, keyboard hooks)
- **Server** (`./server/`): Handles command processing, module execution, and business logic

## Architecture

```
┌─────────────────┐                    ┌─────────────────┐
│   CS2 Client    │◄──────HTTP────────►│   Bot Server    │
│                 │   POST /process    │                 │
│  - Read logs    │   JSON messages    │  - Commands     │
│  - Send chat    │                    │  - Modules      │
│  - Key hooks    │                    │  - Logic        │
└─────────────────┘                    └─────────────────┘
```

## Running the Bot

### Option 1: Run everything together (default)
```bash
python launcher.py both
# or
python cs2chatbot.py
```

### Option 2: Run server and client separately

**Terminal 1 - Start the server:**
```bash
python launcher.py server
```

**Terminal 2 - Start the client:**
```bash
python launcher.py client
```

This separation allows you to:
- Run the server on a different machine
- Restart the client without restarting the server
- Connect multiple clients to one server (future enhancement)
- Debug client and server independently

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Configuration remains in `config.toml` and works the same way as before.

## Communication Protocol

Messages are sent from client to server via POST requests to `/process_message`:

**Request:**
```json
{
  "is_team": true,
  "playername": "Player1",
  "chattext": "@fish"
}
```

**Response:**
```json
{
  "responses": [
    {
      "is_team": true,
      "text": "Player1 caught a Bass weighing 5.2 lbs worth $10!"
    }
  ]
}
```
