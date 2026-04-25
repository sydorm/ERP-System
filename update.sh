#!/bin/bash
echo " Updating ERP System..."
cd /var/www/ERP-System
git pull origin main
docker-compose restart
docker-compose exec -T backend alembic upgrade head
echo " Done!"

