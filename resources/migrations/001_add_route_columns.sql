ALTER TABLE adsb_data.adsb_data
ADD COLUMN IF NOT EXISTS departure_airport_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS departure_airport_city VARCHAR(100),
ADD COLUMN IF NOT EXISTS departure_airport_country VARCHAR(100),
ADD COLUMN IF NOT EXISTS arrival_airport_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS arrival_airport_city VARCHAR(100),
ADD COLUMN IF NOT EXISTS arrival_airport_country VARCHAR(100);
