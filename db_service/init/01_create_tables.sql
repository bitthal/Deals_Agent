-- Create tables for the deals agent application

-- Drop existing tables if they exist
DROP TABLE IF EXISTS deal_suggestions CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- Events table to store information about real-time events
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(255) NOT NULL,
    location_uuid VARCHAR(255) NOT NULL,
    event_trigger_point VARCHAR(255) NOT NULL,
    event_details_text JSONB NOT NULL,
    event_location_latitude DECIMAL(10, 8) NOT NULL,
    event_location_longitude DECIMAL(11, 8) NOT NULL,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    activity_id VARCHAR(255) NOT NULL,
    processed_for_suggestion BOOLEAN DEFAULT FALSE
);

-- Table: inventory (Stores product inventory information)
CREATE TABLE IF NOT EXISTS inventory (
    sku VARCHAR(255) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    quantity_on_hand INTEGER NOT NULL,
    category VARCHAR(255),
    supplier VARCHAR(255),
    vendor_id VARCHAR(255) NOT NULL
);

-- Table: deal_suggestions (Stores AI-generated deal suggestions and vendor feedback)
CREATE TABLE IF NOT EXISTS deal_suggestions (
    id SERIAL PRIMARY KEY,
    vendor_id VARCHAR(255) NOT NULL,
    event_id INTEGER NOT NULL,
    suggested_product_sku VARCHAR(255) NOT NULL,
    deal_details_prompt TEXT NOT NULL,
    deal_details_suggestion_text TEXT NOT NULL,
    suggested_discount_type VARCHAR(50) NOT NULL,
    suggested_discount_value DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2) NOT NULL,
    suggested_price DECIMAL(10, 2) NOT NULL,
    ai_model_name VARCHAR(255) NOT NULL,
    ai_response_payload JSONB NOT NULL,
    vendor_feedback VARCHAR(50) DEFAULT 'pending',
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(id),
    FOREIGN KEY (suggested_product_sku) REFERENCES inventory(sku)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_events_vendor_id ON events(vendor_id);
CREATE INDEX IF NOT EXISTS idx_events_location_uuid ON events(location_uuid);
CREATE INDEX IF NOT EXISTS idx_events_trigger_point ON events(event_trigger_point);
CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category);
CREATE INDEX IF NOT EXISTS idx_inventory_supplier ON inventory(supplier);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_deal_suggestions_vendor_id ON deal_suggestions(vendor_id);
CREATE INDEX IF NOT EXISTS idx_deal_suggestions_event_id ON deal_suggestions(event_id);
CREATE INDEX IF NOT EXISTS idx_deal_suggestions_product_sku ON deal_suggestions(suggested_product_sku);
CREATE INDEX IF NOT EXISTS idx_deal_suggestions_status ON deal_suggestions(status);
CREATE INDEX IF NOT EXISTS idx_deal_suggestions_vendor_feedback ON deal_suggestions(vendor_feedback);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_inventory_updated_at
    BEFORE UPDATE ON inventory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_deal_suggestions_updated_at
    BEFORE UPDATE ON deal_suggestions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 