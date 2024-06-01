docker build -t nervokid/adsbdatadb:latest -f Dockerfile.db .
docker build -t nervokid/adsbdatabackend:latest -f Dockerfile.backend .
#docker-compose up --detach
#docker cp db.json djangowebsite_web_1:/db.json
#docker exec djangowebsite_web_1 python manage.py loaddata /db.json
