class Scheduler:
    def __init__(self, api_client, db_manager, api_id):
        self.api_client = api_client
        self.db_manager = db_manager
        self.api_id = api_id

    def scheduled_task(self):
        json_response = self.api_client.fetch_data(self.api_id)
        if json_response:
            self.db_manager.insert_record(json_response, self.api_id)

    def start(self):
        schedule.every(1).minutes.do(self.scheduled_task)
        while True:
            schedule.run_pending()
            time.sleep(1)

# Replace with your actual details
db_name = 'your_dbname'
db_user = 'your_username'
db_password = 'your_password'
db_host = 'your_host'
api_endpoint = 'your_api_endpoint'
api_id = 'your_api_id'

db_manager = DatabaseManager(db_name, db_user, db_password, db_host)
api_client = APIClient(api_endpoint)
scheduler = Scheduler(api_client, db_manager, api_id)

scheduler.start()
