create user adsb_user with password 'adsb_password';
CREATE DATABASE adsb_data;
GRANT ALL PRIVILEGES ON DATABASE adsb_data TO adsb_user;
\c adsb_data;
create schema adsb_data;
create table adsb_data.adsb_data(id varchar(32), timestamp timestamp, icao_type_code varchar(50), manufacturer varchar(100), mode_s varchar(50), operator_flag_code VARCHAR(50), registered_owners VARCHAR(255), registration VARCHAR(50), type VARCHAR(100), PRIMARY KEY (id, timestamp));
create index adsb_data_id_index ON adsb_data.adsb_data (id);