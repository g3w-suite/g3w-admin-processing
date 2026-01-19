#!/bin/bash
# Run Celery worker for Qprocessing module

set -x

# run rabbimq/redis
# docker run -d --hostname my-rabbit -p 5672:5672 --name some-rabbit rabbitmq
# docker run --name some-redis -p 6379:6379 -d redis

# run celery
celery -A base worker -l info #-n wrk1@%h
