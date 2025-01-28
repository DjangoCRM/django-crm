#!/bin/bash

# Docker config
# clean up docker containers and images
docker compose down --volumes --remove-orphans --rmi all
docker system prune -a -f

# build and run docker containers
docker compose up -d

sleep 10
# run init.sql to grant privileges to the user for testing
docker exec -i mysql_dev mysql -u root -pcrmpass < init.sql

cd ..

# downlaod the dependencies
pip install -r requirements.txt

# populate the database
python manage.py setupdata

# run test
python manage.py test tests/ --noinput

# run the server
python manage.py runserver