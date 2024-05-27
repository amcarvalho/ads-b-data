create user adsb_user with password 'adsb_password';
create database adsb_data;
grant connect on database adsb_data to adsb_user;
\c adsb_data;
create schema adsb_data;
GRANT ALL ON SCHEMA adsb_data TO adsb_user;