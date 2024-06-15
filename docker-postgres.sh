docker run --name postgres \
--add-host=host.docker.internal:host-gateway \
-e POSTGRES_PASSWORD=mysecretpassword -d \
-v ./.postgres_data:/var/lib/postgresql/data \
-p 192.168.1.204:5432:5432 postgres
