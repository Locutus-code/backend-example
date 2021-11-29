"""Various helper functions used in API endpoints."""

from datetime import datetime, timezone
from urllib.parse import urlparse

from aws_lambda_powertools.utilities.parser import BaseModel, parse
from chalice import app


def now() -> datetime:
    """Return the current time in UTC."""
    return datetime.now(tz=timezone.utc)


def get_base_url(current_request: app.Request):
    """
    Generate URL's for internal links in swagger documentation.

    Note to reviewer, this is inherited code
    """
    headers = current_request.headers
    base_url = "%s://%s" % (headers.get("x-forwarded-proto", "http"), headers["host"])
    if "stage" in current_request.context:
        base_url = "%s/%s" % (base_url, current_request.context.get("stage"))
    return base_url


def sanitize_url(url) -> str:
    """
    Place holder sanitization of URL's.

    Only here to illustrate that something should be done.
    """
    url = urlparse(url)
    if url.scheme not in ("http", "https"):
        raise app.BadRequestError("Invalid URL")
    return url.geturl()


def get_query_params(app: app, model: BaseModel):
    """
    Fetch query params and parse them using an applied model.

    If the model has default values defined, these will be returned.
    """
    if app.current_request.query_params:
        return parse(app.current_request.query_params, model)
    return model()
