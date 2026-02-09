-- Initialize PostgreSQL database schema for fishing bot

-- User balances table
CREATE TABLE IF NOT EXISTS user_balances (
    user_id TEXT PRIMARY KEY,
    balance NUMERIC(10, 2) NOT NULL DEFAULT 0
);

-- Caught fish table
CREATE TABLE IF NOT EXISTS caught_fish (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    weight NUMERIC(10, 2) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    bait INTEGER DEFAULT 0
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS idx_caught_fish_user_id ON caught_fish(user_id);

-- User inventory table
CREATE TABLE IF NOT EXISTS user_inventory (
    user_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_data TEXT DEFAULT '{}',
    quantity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, item_name)
);

-- Status effects table
CREATE TABLE IF NOT EXISTS status_effects (
    user_id TEXT NOT NULL,
    effect_name TEXT NOT NULL,
    expiration_time BIGINT NOT NULL,
    PRIMARY KEY (user_id, effect_name)
);

-- Create index on expiration_time for cleanup queries
CREATE INDEX IF NOT EXISTS idx_status_effects_expiration ON status_effects(expiration_time);

-- Grant permissions (if needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bot_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bot_user;
