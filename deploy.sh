docker-compose stop
docker-compose rm -f
docker-compose pull
docker rmi $(docker images -f "dangling=true" -q)
docker-compose up -d