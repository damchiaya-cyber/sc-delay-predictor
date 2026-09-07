-- sql/02_seed_data.sql
-- Seed data reflecting German FMCG/Logistics hubs

INSERT INTO hubs (hub_id, hub_name, city, country, latitude, longitude) VALUES
('HUB_FRA', 'Frankfurt Logistics Center', 'Frankfurt', 'DE', 50.1109, 8.6821),
('HUB_HAM', 'Hamburg Port Hub', 'Hamburg', 'DE', 53.5511, 9.9937),
('HUB_MUC', 'Munich Distribution Hub', 'Munich', 'DE', 48.1351, 11.5820),
('HUB_LEI', 'Leipzig FMCG Gateway', 'Leipzig', 'DE', 51.3397, 12.3731),
('HUB_CGN', 'Cologne Freight Depot', 'Cologne', 'DE', 50.9375, 6.9603)
ON CONFLICT (hub_id) DO NOTHING;

INSERT INTO routes (route_id, origin_hub_id, destination_hub_id, distance_km, expected_duration_hours, sla_max_hours) VALUES
('R_FRA_HAM', 'HUB_FRA', 'HUB_HAM', 500.00, 6.00, 7.50),
('R_FRA_MUC', 'HUB_FRA', 'HUB_MUC', 390.00, 4.50, 6.00),
('R_HAM_LEI', 'HUB_HAM', 'HUB_LEI', 400.00, 5.00, 6.50),
('R_CGN_FRA', 'HUB_CGN', 'HUB_FRA', 190.00, 2.50, 3.50)
ON CONFLICT (route_id) DO NOTHING;
