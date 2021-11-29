#!/bin/sh

aws sqs create-queue --queue-name 'scraper-queue-test'
aws sqs set-queue-attributes \
    --queue-url https://eu-west-1.queue.amazonaws.com/020193958197/scraper-queue-test \
    --attributes VisibilityTimeout=60

poetry run ./create_tables.py
poetry export -f requirements.txt > requirements.txt --without-hashes

chalice deploy --profile locutus --stage test
