#!/bin/bash

sh -c "truncate -s 0 /var/lib/docker/containers/**/*-json.log"

docker-compose down -v
docker-compose up --build -d
docker-compose logs cinbot
