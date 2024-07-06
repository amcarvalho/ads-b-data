docker compose down
sudo mv .postgres_data ..
docker build -t nervokid/adsbdatadb:latest -f Dockerfile.db .
docker build -t nervokid/adsbdatabackend:latest -f Dockerfile.backend .
sudo mv ../.postgres_data .
docker compose up -d
#docker-compose up --detach
#docker cp db.json djangowebsite_web_1:/db.json
#docker exec djangowebsite_web_1 python manage.py loaddata /db.json
