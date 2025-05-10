-- Drop the trigger that updates updated_at column
DROP TRIGGER IF EXISTS update_events_updated_at ON events;
DROP TRIGGER IF EXISTS update_inventory_updated_at ON inventory;
DROP TRIGGER IF EXISTS update_deal_suggestions_updated_at ON deal_suggestions;

-- Drop the function that updates updated_at column
DROP FUNCTION IF EXISTS update_updated_at_column(); 