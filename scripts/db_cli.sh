#!/bin/bash

CONTAINER_NAME="erp_postgres"
DB_USER="erp_user"
DB_NAME="erp_db"

docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME
