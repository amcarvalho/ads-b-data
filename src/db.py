import psycopg2
import configparser
from datetime import datetime, timedelta

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


    def insert_record(self, data: dict, hex_code: str):
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM adsb_data.adsb_data WHERE id = %s AND timestamp > %s",
                    (hex_code, datetime.now() - timedelta(hours=2))
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO adsb_data.adsb_data (icao_type_code, manufacturer, mode_s, operator_flag_code, registered_owners, registration, type, id, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (data['ICAOTypeCode'], data['Manufacturer'], data['ModeS'], data['OperatorFlagCode'], data['RegisteredOwners'], data['Registration'], data['Type'], hex_code, datetime.now())
                    )
                    conn.commit()
                    print('Record inserted successfully.')
                else:
                    print('Record already exists for this ID within the last 2 hours.')

