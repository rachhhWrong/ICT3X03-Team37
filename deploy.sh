#!/bin/bash
docker kill 3x03/web redis > /dev/null 2>&1
docker rm 3x03/web redis > /dev/null 2>&1
docker-compose up -d