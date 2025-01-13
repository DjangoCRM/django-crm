# clean up docker containers and images
docker compose down --volumes --remove-orphans --rmi all
docker system prune -a -f

# build and run docker containers
docker compose up -d

sleep 10
# run init.sql to grant privileges to the user for testing
docker exec -i mysql_dev mysql -u root -pcrmpass < init.sql