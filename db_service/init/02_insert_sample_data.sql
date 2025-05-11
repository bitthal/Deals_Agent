-- Insert sample data into events table
INSERT INTO events (id, vendor_id, location_uuid, event_trigger_point, event_details_text, event_location_latitude, event_location_longitude, event_timestamp, updated_at)
VALUES
  (1, 1, '11111111-1111-1111-1111-111111111111', 'weather', '{"description": "Heavy rain expected"}', 28.6139, 77.2090, '2024-06-01T09:00:00Z', CURRENT_TIMESTAMP),
  (2, 2, '22222222-2222-2222-2222-222222222222', 'product_expiry', '{"product": "Energy Gel", "expiry": "2024-06-10"}', 19.0760, 72.8777, '2024-06-02T10:00:00Z', CURRENT_TIMESTAMP),
  (3, 3, '33333333-3333-3333-3333-333333333333', 'holiday_special', '{"holiday": "Independence Day"}', 12.9716, 77.5946, '2024-08-15T08:00:00Z', CURRENT_TIMESTAMP),
  (4, 4, '44444444-4444-4444-4444-444444444444', 'local_event', '{"event": "Marathon"}', 13.0827, 80.2707, '2024-07-20T06:00:00Z', CURRENT_TIMESTAMP),
  (5, 5, '55555555-5555-5555-5555-555555555555', 'stock_level', '{"sku": "UMB-LG-BLK-001", "stock": 10}', 22.5726, 88.3639, '2024-06-15T12:00:00Z', CURRENT_TIMESTAMP);

-- Insert sample data into inventory table
INSERT INTO inventory (sku, product_name, description, price, quantity_on_hand, category, supplier)
VALUES
  ('UMB-LG-BLK-001', 'Large Black Umbrella', 'A sturdy black umbrella, windproof.', 400, 150, 'Accessories', 'Reliable Umbrellas Inc.'),
  ('WB-BRD-STL-002', 'Water Bottle - Branded', 'Stainless steel, 750ml, event branded.', 250, 2000, 'Merchandise', 'PromoGoods Ltd.'),
  ('EG-STR-PK-003', 'Energy Gel - Strawberry', 'Quick energy boost, strawberry flavor, pack of 3.', 150, 500, 'Consumables', 'Sports Nutrition Co.'),
  ('CAP-RUN-BLU-004', 'Running Cap - Blue', 'Lightweight, breathable, adjustable blue cap.', 180, 300, 'Apparel', 'ActiveWear Supplies'),
  ('TSH-EVT-M-005', 'T-Shirt - Event Branded - M', 'Cotton event t-shirt, medium size.', 350, 1500, 'Merchandise', 'PromoGoods Ltd.'),
  ('TSH-EVT-L-006', 'T-Shirt - Event Branded - L', 'Cotton event t-shirt, large size.', 350, 1500, 'Merchandise', 'PromoGoods Ltd.'),
  ('FAK-SML-RD-007', 'First Aid Kit - Small', 'Compact first aid kit for minor injuries.', 220, 100, 'Safety', 'HealthFirst Products'),
  ('SUN-SPF50-100ML-008', 'Sunscreen SPF 50', '100ml tube, SPF 50, water-resistant.', 120, 400, 'Consumables', 'SafeSkin Solutions'),
  ('TWL-COOL-GRN-009', 'Cooling Towel', 'Instant cooling relief towel, green.', 90, 600, 'Accessories', 'ActiveWear Supplies'),
  ('BAG-DRAW-RD-010', 'Drawstring Bag - Red', 'Nylon drawstring bag, red color, event logo option.', 75, 1000, 'Merchandise', 'PromoGoods Ltd.');

-- Insert sample data into deal_suggestions table
INSERT INTO deal_suggestions (vendor_id, event_id, suggested_product_sku, deal_details_prompt, deal_details_suggestion_text, suggested_discount_type, suggested_discount_value, original_price, suggested_price, ai_model_name, ai_response_payload, vendor_feedback, status)
VALUES
  (1, 1, 'UMB-LG-BLK-001', 'Suggest a rainy day deal.', 'Buy a Large Black Umbrella at 20% off!', 'percentage', 20, 400, 320, 'gemini-1.5-flash', '{"model": "gemini-1.5-flash", "score": 0.98}', 'pending', 'generated'),
  (2, 2, 'WB-BRD-STL-002', 'Suggest a hydration deal.', 'Get a Branded Water Bottle for just ₹200!', 'fixed_amount', 50, 250, 200, 'gemini-1.5-flash', '{"model": "gemini-1.5-flash", "score": 0.95}', 'pending', 'generated'),
  (3, 3, 'EG-STR-PK-003', 'Suggest an energy deal.', 'Energy Gel pack of 3 at 10% off!', 'percentage', 10, 150, 135, 'gemini-1.5-flash', '{"model": "gemini-1.5-flash", "score": 0.92}', 'pending', 'generated'),
  (4, 4, 'CAP-RUN-BLU-004', 'Suggest a sun protection deal.', 'Running Cap - Blue at ₹150 only!', 'fixed_amount', 30, 180, 150, 'gemini-1.5-flash', '{"model": "gemini-1.5-flash", "score": 0.90}', 'pending', 'generated'),
  (5, 5, 'TSH-EVT-M-005', 'Suggest a t-shirt deal.', 'Event Branded T-Shirt (M) at 15% off!', 'percentage', 15, 350, 297.5, 'gemini-1.5-flash', '{"model": "gemini-1.5-flash", "score": 0.93}', 'pending', 'generated'); 