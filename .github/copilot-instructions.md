# CS2 Chatbot - AI Agent Instructions

## Architecture Overview

This is a **client-server chatbot** for Counter-Strike 2 with multi-platform support:
- **Server** (`server/server.py`): Flask-based, handles commands & business logic
- **Clients** (`client/adapters/`): CS2 adapter (Windows-only) and Discord bot
- **Database**: PostgreSQL with connection pooling (`util/database.py`)

Communication: Clients POST messages to `http://127.0.0.1:8080/process_message` → server returns JSON response array.

## Critical Workflows

### Running the Bot
```powershell
# Production: server in Docker, client on Windows
docker-compose up --build -d  # Start/rebuild server + PostgreSQL
python launcher.py client     # Run CS2 client locally

# Development: Run server locally (no Docker)
python launcher.py server  # Terminal 1
python launcher.py client  # Terminal 2

# Discord bot (requires DISCORD_TOKEN in .env)
python launcher.py discord

# Local development with both CS2 + server
python launcher.py both
```

**Important**: After making server changes, rebuild with `docker-compose up --build -d`

### Database Setup
- **Docker** (recommended): `docker-compose up --build -d` auto-initializes PostgreSQL with `db/init.sql`
- **Local dev**: Configure `config.toml` [database] section for direct PostgreSQL connection
- **Migration**: Use `migrate_to_postgres.py` to convert SQLite databases

## Command & Module Pattern

**Commands** (`cmds/`) are user-invoked with `@` prefix:
```python
from util.commands import command_registry
from modules.fishing import Fishing as FishingModule

@command_registry.register("fish", aliases=["cast", "gofish"])
def fish_command(bot, is_team: bool, playername: str, chattext: str) -> None:
    fishing = bot.modules.get_module("fishing")
    result = fishing.fish(playername)
    bot.add_to_chat_queue(is_team, f"{playername} caught a {result['name']}!")
```

**Modules** (`modules/`) provide business logic:
```python
class Fishing:
    load_after = ["inventory", "economy"]  # Dependency order
    
    def __init__(self):
        self.inventory = module_registry.get_module("inventory")
```

**Key distinction**: Commands are thin controllers that call module methods. Modules contain all game logic.

## Database Patterns

Always use the `DatabaseConnection` context manager:
```python
from util.database import DatabaseConnection

with DatabaseConnection() as cursor:
    cursor.execute("SELECT * FROM caught_fish WHERE user_id = %s", (user_id,))
    fish = cursor.fetchall()
# Auto-commits on success, rolls back on exception
```

Never manually manage connections—the pool handles it. Use parameterized queries (`%s`) to prevent SQL injection.

## Response Queue Pattern

The server collects multiple responses per message via `bot.add_to_chat_queue()`:
```python
# In commands/modules:
bot.add_to_chat_queue(is_team, "First message")
bot.add_to_chat_queue(is_team, "Second message")
# Server returns: [{"is_team": true, "text": "First message"}, {...}]
```

CS2 client sends them sequentially with delays to avoid rate limits. Discord sends as separate messages.

## Module Loading Dependencies

Modules with `load_after = ["module_name"]` load in dependency order. Common dependencies:
- `economy`: Currency operations
- `inventory`: Item management
- `status_effects`: Temporary buffs/debuffs

Circular dependencies cause startup failures. The `ModuleRegistry` auto-detects and errors explicitly.

## Config Management

- `config.toml`: Main settings (CS2 paths, database, key bindings)
- `.env`: Secrets (Discord token, etc.)
- PyInstaller mode: Config copied to `%APPDATA%/cs2chatbot/` automatically

## CS2-Specific Quirks

The CS2 client simulates keyboard input to send chat:
1. Writes message to `chat.cfg`
2. Presses `load_chat_key` to exec the config
3. Presses `send_chat_key` to send

**Critical**: In CS2, bind these keys:
```
bind "kp_1" "exec chat"
bind "kp_2" "messagemode"  // or messagemode2 for team
```

And add launch options: `-condebug -conclearlog`

## Common Pitfalls

1. **Don't call `get_connection()` directly**: Use `DatabaseConnection` context manager
2. **Module dependencies**: Check `load_after` when cross-referencing modules
3. **Response format**: Commands must call `bot.add_to_chat_queue()`, not return strings directly (unless returning error messages)
4. **Windows-only**: CS2 client requires `pywin32` and `keyboard` packages (Windows-specific)
5. **Testing**: Use `test_communication.py` to test server without CS2 running

## File Organization

- `cmds/`: Command handlers (user-facing @commands)
- `modules/`: Business logic classes
- `modules/data/`: JSON configs (fish.json, shop.json, quests.json, etc.)
- `util/`: Shared utilities (database, config, registries)
- `db/`: SQL schemas and migrations

## Key Files

- `server/server.py`: Main Flask app, request routing
- `util/module_registry.py`: Auto-loads modules with dependency resolution
- `util/commands.py`: Decorator-based command registration with fuzzy matching
- `util/database.py`: PostgreSQL connection pooling
- `launcher.py`: Multi-mode entry point (server/client/both/all/discord)
