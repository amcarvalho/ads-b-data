import psycopg2
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, dbname, user, password, host):
        self.db_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host
        }

    def insert_record(self, data, api_id):
        with psycopg2.connect(**self.db_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM adsb_data.adsb_data WHERE id = %s AND timestamp > %s",
                    (api_id, datetime.now() - timedelta(hours=2))
                )
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO adsb_data.adsb_data (icao_type_code, manufacturer, mode_s, operator_flag_code, registered_owners, registration, type, id, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (data['ICAOTypeCode'], data['Manufacturer'], data['ModeS'], data['OperatorFlagCode'], data['RegisteredOwners'], data['Registration'], data['Type'], api_id, datetime.now())
                    )
                    conn.commit()
                    print('Record inserted successfully.')
                else:
                    print('Record already exists for this ID within the last 2 hours.')

