docker run --name postgres \
-e POSTGRES_PASSWORD=mysecretpassword -d \
-v ./.postgres_data:/var/lib/postgresql/data \
-p 5432:5432 postgres