"""Chalice template example app.."""

import os
import sys

from chalice import (
    Chalice,
    Response,
)
from chalice.app import ConvertToMiddleware, SQSEvent

from aws_lambda_powertools import Logger, Tracer

from chalicelib.blueprints.channels import channels
from chalicelib.blueprints.articles import articles
from chalicelib.blueprints.api_docs import api_docs
from chalicelib.workers.articlescraper import scraper_worker

QUEUE_URL: str = os.environ.get("SCRAPER_QUEUE_URL")
app = Chalice(app_name="chalice-example-backend")
if "local" in sys.argv:
    app.debug = True
app.api.cors = True

logger = Logger()
tracer = Tracer()

app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))
app.register_middleware(ConvertToMiddleware(tracer.capture_lambda_handler))

app.register_blueprint(channels)
app.register_blueprint(articles)
app.register_blueprint(api_docs)


@app.on_sqs_message(queue=QUEUE_URL, batch_size=1)
def sqs_scraper_worker(event: SQSEvent):
    """Worker that fires of the scraper process from SQS events."""
    for record in event:
        logger.info(f"Received work item: {record.body}")
        scraper_worker(record.body, record.receipt_handle)
