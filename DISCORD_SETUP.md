# Discord Bot Setup

## Prerequisites

1. Python 3.10 or higher
2. A Discord bot token from the Discord Developer Portal

## Getting a Discord Bot Token

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give your bot a name and click "Create"
4. Navigate to the "Bot" tab on the left
5. Click "Add Bot"
6. Under "Token", click "Reset Token" and copy the token
7. **Important**: Keep this token secret!

## Bot Permissions

In the Discord Developer Portal, under "Bot" tab:
1. Enable "Message Content Intent" (required to read message content)
2. Under "OAuth2" > "URL Generator":
   - Select scopes: `bot`
   - Select bot permissions:
     - Read Messages/View Channels
     - Send Messages
     - Read Message History

## Configuration

Add your Discord bot token to `config.toml`:

```toml
discord_bot_token = "your_bot_token_here"
discord_command_prefix = "@"
```

Or set it as an environment variable:

```bash
# Windows PowerShell
$env:DISCORD_BOT_TOKEN="your_bot_token_here"

# Linux/Mac
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

## Installation

Install the Discord library:

```bash
pip install discord.py
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Running the Bot

Start the Discord bot:

```bash
python discord_bot.py
```

This will:
1. Start the backend server on port 8080
2. Connect to Discord using your bot token
3. Listen for commands starting with `@` (configurable)

## Usage

In Discord, send messages to channels where the bot has access:

```
@fish
@sack
@balance
@shop
@help
```

The bot will respond in the same channel.

## Architecture

The Discord adapter follows the same client-server architecture as the CS2 client:

```
Discord → DiscordClient → HTTP POST → BotServer → Commands/Modules
                                                          ↓
Discord ← DiscordClient ← HTTP Response ← BotServer ← Response
```

- **DiscordClient** (`client/adapters/discord/discord_client.py`): Handles Discord events and sends messages to the server
- **BotServer** (`server/server.py`): Processes commands and returns responses
- Commands and modules remain unchanged

## Inviting the Bot to Your Server

1. Go to Discord Developer Portal
2. Select your application
3. Navigate to "OAuth2" > "URL Generator"
4. Select scopes: `bot`
5. Select bot permissions (at minimum: Send Messages, Read Messages)
6. Copy the generated URL
7. Open the URL in your browser
8. Select the server you want to add the bot to
9. Click "Authorize"

## Troubleshooting

### Bot doesn't respond
- Check that the bot is online in your server
- Verify the command prefix matches (default is `@`)
- Ensure "Message Content Intent" is enabled in Discord Developer Portal
- Check `discord_client.log` for errors

### "Intents are not enabled"
- Go to Discord Developer Portal
- Navigate to your application > Bot
- Enable "Message Content Intent" under "Privileged Gateway Intents"
- Restart the bot

### Server connection errors
- Ensure the backend server is running on port 8080
- Check firewall settings
- Verify `server_url` in the Discord client initialization

## Multiple Platform Support

You can run both CS2 and Discord adapters simultaneously:

1. Start the server once: `python launcher.py server`
2. In separate terminals:
   - CS2: `python launcher.py client`
   - Discord: `python discord_bot.py`

Both clients will connect to the same backend server and share the same database.
