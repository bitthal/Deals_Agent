-- Create tables for the deals agent application

-- Drop existing tables if they exist
DROP TABLE IF EXISTS deal_suggestions CASCADE;
DROP TABLE IF EXISTS inventory CASCADE;
DROP TABLE IF EXISTS events CASCADE;

-- Events table to store information about real-time events
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    location_uuid UUID,
    event_trigger_point VARCHAR(32) NOT NULL CHECK (event_trigger_point IN ('weather', 'product_expiry', 'holiday_special', 'local_event', 'competitor_action', 'stock_level')),
    event_details_text JSONB,
    event_location_latitude DECIMAL(10,8),
    event_location_longitude DECIMAL(11,8),
    event_timestamp TIMESTAMP,
    activity_id VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_for_suggestion BOOLEAN DEFAULT FALSE
    -- Add foreign key constraints if referenced tables exist:
    -- ,FOREIGN KEY (vendor_id) REFERENCES main_vendorkyc(vendor_id)
    -- ,FOREIGN KEY (location_uuid) REFERENCES vendor_business_locations(uuid)
);

-- Table: inventory (Stores product inventory information)
CREATE TABLE inventory (
    sku VARCHAR(32) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    quantity_on_hand INTEGER NOT NULL CHECK (quantity_on_hand >= 0),
    category VARCHAR(100) NOT NULL,
    supplier VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: deal_suggestions (Stores AI-generated deal suggestions and vendor feedback)
CREATE TABLE deal_suggestions (
    id SERIAL PRIMARY KEY,
    vendor_id INTEGER,
    event_id INTEGER,
    suggested_product_sku VARCHAR(32) NOT NULL,
    deal_details_prompt TEXT,
    deal_details_suggestion_text TEXT,
    suggested_discount_type VARCHAR(20) CHECK (suggested_discount_type IN ('percentage', 'fixed_amount')),
    suggested_discount_value DECIMAL(10,2),
    original_price DECIMAL(10,2),
    suggested_price DECIMAL(10,2),
    ai_model_name VARCHAR(100),
    ai_response_payload JSON,
    vendor_feedback VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (vendor_feedback IN ('pending', 'accepted', 'rejected')),
    feedback_timestamp TIMESTAMP,
    status VARCHAR(32) NOT NULL DEFAULT 'generated' CHECK (status IN ('generated', 'notified_vendor', 'feedback_received', 'deal_posted', 'deal_post_failed', 'expired')),
    deals_api_request_payload JSON,
    deals_api_response_payload JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (suggested_product_sku) REFERENCES inventory(sku)
    -- Add foreign key constraints if referenced tables exist:
    -- ,FOREIGN KEY (vendor_id) REFERENCES main_vendorkyc(vendor_id)
    -- ,FOREIGN KEY (event_id) REFERENCES events(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_events_vendor_id ON events(vendor_id);
CREATE INDEX IF NOT EXISTS idx_events_location_uuid ON events(location_uuid);
CREATE INDEX IF NOT EXISTS idx_events_trigger_point ON events(event_trigger_point);
CREATE INDEX IF NOT EXISTS idx_events_processed_for_suggestion ON events(processed_for_suggestion);
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