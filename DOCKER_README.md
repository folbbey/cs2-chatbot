# Docker Setup for CS2 Chatbot Server

This setup containerizes the bot server with PostgreSQL database.

## Prerequisites

- Docker Desktop installed
- Docker Compose installed

## Quick Start

### 1. Build and Start Services

```powershell
# Build and start both PostgreSQL and the server
docker-compose up --build
```

### 2. Run Client Locally (Windows)

The client must run on your Windows machine (not in Docker) since it needs to interact with CS2:

```powershell
python launcher.py client
```

Or run both (server in Docker, client locally):

```powershell
# Terminal 1: Start Docker services
docker-compose up

# Terminal 2: Run client
python launcher.py client
```

## Architecture

- **PostgreSQL**: Runs in Docker container `fishing-bot-db` on port 5432
- **Server**: Runs in Docker container `fishing-bot-server` on port 8080
- **Client**: Runs on Windows host, connects to server at `http://127.0.0.1:8080`

## Database Migration

If you have existing SQLite databases, migrate them to PostgreSQL:

```powershell
# Set environment variables for PostgreSQL connection
$env:POSTGRES_HOST="localhost"
$env:POSTGRES_PORT="5432"
$env:POSTGRES_DB="fishing_bot"
$env:POSTGRES_USER="bot_user"
$env:POSTGRES_PASSWORD="bot_password"

# Run migration script
python migrate_to_postgres.py
```

## Docker Commands

```powershell
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f server
docker-compose logs -f postgres

# Stop services
docker-compose down

# Stop and remove volumes (deletes all database data!)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build

# Access PostgreSQL directly
docker-compose exec postgres psql -U bot_user -d fishing_bot
```

## Environment Variables

Configure in `docker-compose.yml` or `.env` file:

- `POSTGRES_HOST`: Database host (default: `postgres`)
- `POSTGRES_PORT`: Database port (default: `5432`)
- `POSTGRES_DB`: Database name (default: `fishing_bot`)
- `POSTGRES_USER`: Database user (default: `bot_user`)
- `POSTGRES_PASSWORD`: Database password (default: `bot_password`)

## Database Schema

Schema is automatically initialized from `db/init.sql` on first run. Includes tables:

- `user_balances`: User economy balances
- `caught_fish`: Fishing records
- `user_inventory`: Player inventories
- `status_effects`: Active status effects

## Troubleshooting

### Container won't start

```powershell
# Check logs
docker-compose logs server

# Restart from scratch
docker-compose down -v
docker-compose up --build
```

### Client can't connect to server

- Ensure server is running: `docker-compose ps`
- Check server is on port 8080: `http://localhost:8080/health`
- Verify client is using `http://127.0.0.1:8080`

### Database connection errors

```powershell
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready -U bot_user

# View database logs
docker-compose logs postgres
```

## Development Workflow

1. Make code changes
2. Rebuild and restart: `docker-compose up --build`
3. Test with client: `python launcher.py client`

## Production Deployment

For production, update `docker-compose.yml`:

- Change default passwords
- Add volume mounts for logs
- Configure backup strategy for `postgres_data` volume
- Consider using Docker secrets for sensitive data
