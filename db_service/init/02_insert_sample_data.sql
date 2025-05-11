-- Insert sample events
INSERT INTO events (
    vendor_id,
    location_uuid,
    event_trigger_point,
    event_details_text,
    event_location_latitude,
    event_location_longitude,
    event_timestamp,
    activity_id
) VALUES
    ('vendor1', 'loc123', 'entry', '{"activity_type": "entry", "duration": 30}', 12.9716, 77.5946, CURRENT_TIMESTAMP, 'act123'),
    ('vendor2', 'loc456', 'exit', '{"activity_type": "exit", "duration": 45}', 12.9784, 77.6408, CURRENT_TIMESTAMP, 'act456'),
    ('vendor3', 'loc789', 'entry', '{"activity_type": "entry", "duration": 60}', 12.9716, 77.5946, CURRENT_TIMESTAMP, 'act789');

-- Insert sample inventory
INSERT INTO inventory (sku, product_name, description, price, quantity_on_hand, category, supplier) VALUES
    ('SKU001', 'Premium Coffee', 'High-quality arabica coffee beans', 19.99, 100, 'Beverages', 'Coffee Supplier Inc'),
    ('SKU002', 'Organic Tea', 'Organic green tea leaves', 14.99, 150, 'Beverages', 'Tea Distributors'),
    ('SKU003', 'Artisan Pastry', 'Freshly baked croissant', 4.99, 50, 'Bakery', 'Local Bakery Co');

-- Insert sample deal suggestions
INSERT INTO deal_suggestions (
    vendor_id,
    event_id,
    suggested_product_sku,
    deal_details_prompt,
    deal_details_suggestion_text,
    suggested_discount_type,
    suggested_discount_value,
    original_price,
    suggested_price,
    ai_model_name,
    ai_response_payload,
    status
) VALUES
    ('vendor1', 1, 'SKU001', 'Coffee promotion for morning rush', '20% off on premium coffee', 'percentage', 20.00, 19.99, 15.99, 'gpt-4', '{"confidence": 0.85}', 'pending'),
    ('vendor2', 2, 'SKU002', 'Tea promotion for afternoon', 'Buy one get one free on tea', 'bogo', 0.00, 14.99, 14.99, 'gpt-4', '{"confidence": 0.90}', 'pending'),
    ('vendor3', 3, 'SKU003', 'Pastry promotion for evening', '15% off on all pastries', 'percentage', 15.00, 4.99, 4.24, 'gpt-4', '{"confidence": 0.75}', 'pending'); 