-- Migration script to add missing item_data column to user_inventory table

-- Add item_data column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user_inventory' 
        AND column_name = 'item_data'
    ) THEN
        ALTER TABLE user_inventory ADD COLUMN item_data TEXT DEFAULT '{}';
    END IF;
END $$;
