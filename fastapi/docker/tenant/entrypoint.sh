#!/bin/bash
# @Author: Daniel Gomes
# @Date:   2022-10-13 11:14:38
# @Last Modified by:   Daniel Gomes
# @Last Modified time: 2022-10-19 11:09:47
echo "Waiting for RabbitMQ to Start..."

until timeout 1 bash -c "cat < /dev/null > /dev/tcp/rabbitmq/5672"; do
        >&2 echo "Waiting for RabbitMQ at \"rabbitmq:5672\"..."
        sleep 1
done

#while ! nc -z $RABBITMQ_SERVICE_NAME 5672; do
  #sleep 0.1
#done

echo "RabbitMQ started"

echo "Waiting for Postgres to Start..."

while ! nc -z db 5432; do
  sleep 0.1
done
echo "Postgres started"
# save ip in an environment variable
export HOST=$IMAGE_NAME-$(hostname) 
# Run metric collector - telegraf
eval "telegraf --config telegraf.conf &"
#run poetry and fastapi server
#poetry run alembic upgrade head
uvicorn main:app --host 0.0.0.0 --port 80