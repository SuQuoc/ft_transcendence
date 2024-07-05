#!/bin/bash

echo "CREATE USER $POSTGRES_ACCESS_USER WITH PASSWORD $POSTGRES_ACCESS_PASSWORD;" >> /docker-entrypoint-initdb.d/create_user.sql
echo "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_ACCESS_USER;" >> /docker-entrypoint-initdb.d/create_user.sql
chmod 777 /docker-entrypoint-initdb.d/create_user.sql
