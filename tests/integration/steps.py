"""Allure tagged steps used in integration tests."""

from uuid import uuid4
from random import randint
from logging import getLogger

import requests
import pytest
import allure

from faker import Faker

from tests.integration.conftest import test_data, MockTestData

logger = getLogger()


@pytest.fixture(scope="function")
def new_channel_payload():
    yield {
        "channel": f"integration {uuid4()}",
        "description": "integration test created",
        "channel_url": "http://locutus.fi",
        "name": "aws s3 homepage",
    }


@pytest.fixture(scope="function")
def channel_for_test(base_url, new_channel_payload) -> dict:
    response = post_channel(base_url, new_channel_payload)
    log_response(response)
    response.raise_for_status()
    yield response.json()
    delete_channel(base_url, new_channel_payload.get("channel"))


@allure.step("Log Response")
def log_response(response: requests.Response):
    allure.attach(
        f"""API Response received:
        origin url: {response.request.url}
        http status: {response.status_code}
        body: {response.text}
        """
    )


@allure.step("Get all Channels from API")
def get_all_channels(base_url: str) -> requests.Response:
    response = requests.get(f"{base_url}/channels")
    log_response(response)
    return response


@allure.step("Create new Channel from API")
def post_channel(base_url: str, payload: dict) -> requests.Response:
    response = requests.post(f"{base_url}/channels", json=payload)
    log_response(response)
    return response


@allure.step("Update existing Channel from API")
def update_channel(base_url: str, payload: dict, channel: str) -> requests.Response:
    response = requests.put(f"{base_url}/channels/{channel}", json=payload)
    log_response(response)
    return response


@allure.step("Delete existing Channel from API")
def delete_channel(base_url: str, channel: str) -> requests.Response:
    response = requests.delete(f"{base_url}/channels/{channel}")
    log_response(response)
    return response


@allure.step("Get existing Channel from API")
def get_channel(base_url: str, channel: str) -> requests.Response:
    response = requests.get(f"{base_url}/channels/{channel}")
    log_response(response)
    return response


@allure.step("Verify Channel is Unique in Response")
def verify_channel_unique_in_response(response, channel):
    assert (
        len(
            list(
                (
                    filter(
                        lambda response: response.get("channel") == channel,
                        response.json(),
                    )
                )
            )
        )
        == 1
    )
    logger.debug(f"Channel {channel} is unique in response")


@allure.step("Get articles from channel")
def get_articles_by_channel(base_url: str, channel: str) -> requests.Response:
    response = requests.get(f"{base_url}/articles/{channel}")
    log_response(response)
    return response


@allure.step("Get specific article from channel")
def get_single_article(base_url: str, channel: str, article: str) -> requests.Response:
    response = requests.get(f"{base_url}/articles/{channel}/{article}")
    log_response(response)
    return response


@allure.step("Request article to be scraped")
def post_article_scrape_request(
    base_url: str, channel: str, payload: dict
) -> requests.Response:
    response = requests.post(f"{base_url}/articles/{channel}", json=payload)
    log_response(response)
    return response
