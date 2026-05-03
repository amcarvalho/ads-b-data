import psycopg2
import configparser
from datetime import datetime, timedelta
from typing import Dict, Optional

class DatabaseManager:
    def __init__(self, password):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.db_params = {
            'dbname': config.get('Database', 'dbname'),
            'user': config.get('Database', 'user'),
            'password': password,
            'host': config.get('Database', 'host'),
        }
        self.hours_since_last_record = int(config.get('General', 'hours_since_last_record'))


    def is_there_a_recent_record(self, hex_code):
        with psycopg2.connect(**self.db_params) as conn:
            x_hours_ago = datetime.now() - timedelta(self.hours_since_last_record)
            query = """
                SELECT EXISTS (
                    SELECT 1 FROM adsb_data.adsb_data
                    WHERE id = %s AND timestamp > %s
                );
            """
            cursor = conn.cursor()
            cursor.execute(query, (hex_code, x_hours_ago))
            result = cursor.fetchone()[0]
            return result


    def insert_record(self, data: dict, hex_code: str, route_data: Optional[Dict[str, Optional[str]]] = None):
        route_data = route_data or {}
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO adsb_data.adsb_data (
                        icao_type_code,
                        manufacturer,
                        mode_s,
                        operator_flag_code,
                        registered_owners,
                        registration,
                        type,
                        departure_airport_code,
                        departure_airport_city,
                        departure_airport_country,
                        arrival_airport_code,
                        arrival_airport_city,
                        arrival_airport_country,
                        id,
                        timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        data['icao_type'],
                        data['manufacturer'],
                        data['mode_s'],
                        data['registered_owner_operator_flag_code'],
                        data['registered_owner'],
                        data['registration'],
                        data['type'],
                        route_data.get('departure_airport_code'),
                        route_data.get('departure_airport_city'),
                        route_data.get('departure_airport_country'),
                        route_data.get('arrival_airport_code'),
                        route_data.get('arrival_airport_city'),
                        route_data.get('arrival_airport_country'),
                        hex_code,
                        datetime.now(),
                    )
                )
                conn.commit()
                print('Record inserted successfully.')

