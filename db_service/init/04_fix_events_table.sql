-- Drop existing triggers and functions
DROP TRIGGER IF EXISTS update_events_updated_at ON events;
DROP TRIGGER IF EXISTS update_inventory_updated_at ON inventory;
DROP TRIGGER IF EXISTS update_deal_suggestions_updated_at ON deal_suggestions;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop and recreate the events table
DROP TABLE IF EXISTS events CASCADE;

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    location_uuid UUID,
    event_trigger_point VARCHAR(32) NOT NULL CHECK (event_trigger_point IN ('weather', 'product_expiry', 'holiday_special', 'local_event', 'competitor_action', 'stock_level')),
    event_details_text JSONB,
    event_location_latitude DECIMAL(10,8),
    event_location_longitude DECIMAL(11,8),
    event_timestamp TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_for_suggestion BOOLEAN DEFAULT FALSE
);

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_events_vendor_id ON events(vendor_id);
CREATE INDEX IF NOT EXISTS idx_events_location_uuid ON events(location_uuid);
CREATE INDEX IF NOT EXISTS idx_events_trigger_point ON events(event_trigger_point);
CREATE INDEX IF NOT EXISTS idx_events_processed_for_suggestion ON events(processed_for_suggestion); 