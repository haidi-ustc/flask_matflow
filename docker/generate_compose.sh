#!/bin/bash

USER_UID=`id -u`
USER_GID=`id -g`

# Change the owner of the workspace and data directories
if [ ! -d ../workspace ];then
    mkdir ../workspace
fi
if [ ! -d ../data ];then
    mkdir ../data
fi

cat <<EOF > docker-compose.yml
version: '3'

services:
  flask_matflow:
    build:
      context: ../
      dockerfile: docker/Dockerfile
    user: "$USER_UID:$USER_GID"
    command: python manage.py
    ports:
      - "5000:5000"
    volumes:
      - ..:/flask_matflow
      - ../workspace:/flask_matflow/workspace:z
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:5.0
    user: "$USER_UID:$USER_GID"
    environment:
      MONGO_INITDB_ROOT_USERNAME: "admin"
      MONGO_INITDB_ROOT_PASSWORD: "admin"
    ports:
      - "27017:27017"
    volumes:
      - ../data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js

  redis:
    image: "redis:latest"
    user: "$USER_UID:$USER_GID"
    ports:
      - "6379:6379"

  celery:
    build:
      context: ../
      dockerfile: docker/Dockerfile
    user: "$USER_UID:$USER_GID"
    command: celery -A task.tasks worker --loglevel=info
    volumes:
      - ..:/flask_matflow
      - ../workspace:/flask_matflow/workspace:z
    depends_on:
      - redis

volumes:
  mongo-data:
EOF

