-- Migration: add autosell_fish table for fish autosell preferences

CREATE TABLE IF NOT EXISTS autosell_fish (
    user_id TEXT NOT NULL,
    fish_name TEXT NOT NULL,
    PRIMARY KEY (user_id, fish_name)
);

CREATE INDEX IF NOT EXISTS idx_autosell_fish_user_id ON autosell_fish(user_id);
