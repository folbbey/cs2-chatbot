# Client-Server Communication Flow

## Message Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CS2 Game                                    │
│  - console.log file                                                  │
│  - Chat input (keyboard simulation)                                  │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 │ 1. Read console.log
                 │    Parse chat messages
                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     CS2 Client Adapter                               │
│  Location: ./client/adapters/cs2/cs2_client.py                      │
│                                                                       │
│  Responsibilities:                                                   │
│  - Monitor console.log file                                          │
│  - Parse chat lines (extract player name, team, message)            │
│  - Send keyboard inputs to CS2                                       │
│  - Queue and send chat messages                                      │
│  - Handle hotkeys (pause/resume)                                     │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 │ 2. HTTP POST to /process_message
                 │    { "is_team": bool, "playername": str, "chattext": str }
                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      Flask Web Server                                │
│  Location: ./server/server.py                                        │
│  Endpoint: POST /process_message                                     │
│                                                                       │
│  Responsibilities:                                                   │
│  - Receive messages via HTTP                                         │
│  - Route to command/module processors                                │
│  - Collect responses                                                 │
│  - Return JSON response                                              │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 │ 3. Process through modules & commands
                 │
                 ├──────────────┐
                 │              │
                 ↓              ↓
        ┌─────────────┐  ┌─────────────┐
        │  Modules    │  │  Commands   │
        │             │  │             │
        │ - Fishing   │  │ - @fish     │
        │ - Casino    │  │ - @flip     │
        │ - Scramble  │  │ - @help     │
        │ - etc.      │  │ - @shop     │
        └─────────────┘  └─────────────┘
                 │              │
                 │              │
                 └──────┬───────┘
                        │
                        │ 4. Collect responses
                        ↓
        ┌────────────────────────────────┐
        │  Response Queue                │
        │  [                             │
        │    {                           │
        │      "is_team": true,          │
        │      "text": "Player caught..."│
        │    }                           │
        │  ]                             │
        └────────────────┬───────────────┘
                         │
                         │ 5. Return HTTP Response
                         │    { "responses": [...] }
                         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                     CS2 Client Adapter                               │
│  - Receives response array                                           │
│  - Adds each response to chat queue                                  │
└────────────────┬────────────────────────────────────────────────────┘
                 │
                 │ 6. Process chat queue
                 │    - Write to chat.cfg
                 │    - Simulate key presses
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                          CS2 Game                                    │
│  - Message appears in chat                                           │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Benefits

1. **Separation of Concerns**: Game-specific logic is isolated in the client adapter
2. **Testability**: Server can be tested independently without CS2 running
3. **Flexibility**: Multiple clients could connect to one server
4. **Maintainability**: Business logic changes don't require client changes
5. **Debugging**: Server and client can be debugged separately

## Files Structure

```
cs2-chatbot/
├── client/
│   └── adapters/
│       └── cs2/
│           ├── __init__.py
│           └── cs2_client.py        # CS2-specific adapter
├── server/
│   ├── __init__.py
│   └── server.py                    # Flask web server
├── cmds/                             # Command implementations
├── modules/                          # Module implementations
├── util/                             # Shared utilities
├── cs2chatbot.py                     # Main entry (runs both)
├── launcher.py                       # Flexible launcher
└── test_communication.py             # Test script
```
