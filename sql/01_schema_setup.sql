-- sql/01_schema_setup.sql
-- Enterprise Supply Chain & Logistics Schema

CREATE TABLE IF NOT EXISTS hubs (
    hub_id VARCHAR(50) PRIMARY KEY,
    hub_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(10) NOT NULL DEFAULT 'DE',
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
    route_id VARCHAR(50) PRIMARY KEY,
    origin_hub_id VARCHAR(50) NOT NULL,
    destination_hub_id VARCHAR(50) NOT NULL,
    distance_km DECIMAL(8, 2) NOT NULL,
    expected_duration_hours DECIMAL(5, 2) NOT NULL,
    sla_max_hours DECIMAL(5, 2) NOT NULL,
    FOREIGN KEY (origin_hub_id) REFERENCES hubs(hub_id),
    FOREIGN KEY (destination_hub_id) REFERENCES hubs(hub_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(50) PRIMARY KEY,
    route_id VARCHAR(50) NOT NULL,
    carrier_name VARCHAR(100) NOT NULL,
    planned_dispatch TIMESTAMP NOT NULL,
    actual_dispatch TIMESTAMP,
    planned_delivery TIMESTAMP NOT NULL,
    actual_delivery TIMESTAMP,
    status VARCHAR(20) DEFAULT 'PLANNED', -- PLANNED, IN_TRANSIT, DELIVERED, DELAYED
    delay_minutes INT DEFAULT 0,
    is_sla_violated INT DEFAULT 0, -- 1 = Yes, 0 = No
    FOREIGN KEY (route_id) REFERENCES routes(route_id)
);

CREATE TABLE IF NOT EXISTS weather_observations (
    observation_id VARCHAR(100) PRIMARY KEY,
    hub_id VARCHAR(50) NOT NULL,
    observation_time TIMESTAMP NOT NULL,
    temperature_c DECIMAL(4, 1),
    precipitation_mm DECIMAL(5, 2),
    snowfall_cm DECIMAL(5, 2),
    wind_speed_kmh DECIMAL(5, 2),
    weather_code INT,
    FOREIGN KEY (hub_id) REFERENCES hubs(hub_id)
);

-- Indexing strategy for query optimization on large joins
CREATE INDEX IF NOT EXISTS idx_shipments_route ON shipments(route_id);
CREATE INDEX IF NOT EXISTS idx_shipments_dispatch ON shipments(planned_dispatch);
CREATE INDEX IF NOT EXISTS idx_weather_hub_time ON weather_observations(hub_id, observation_time);
