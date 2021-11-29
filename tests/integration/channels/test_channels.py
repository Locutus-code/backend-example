from random import randint
from logging import getLogger

import pytest
import requests
import allure

from tests.integration.conftest import test_data, MockTestData
from tests.integration.steps import (
    new_channel_payload,
    channel_for_test,
    log_response,
    get_all_channels,
    post_channel,
    update_channel,
    delete_channel,
    get_channel,
    verify_channel_unique_in_response,
)


@allure.story("Able to manage Channels")
class TestChannelsApi:
    logger = getLogger()

    @allure.title("Able to manage channels: Enumerate")
    def test_get_all_channels_succeeds(self, base_url: str, test_data):
        test_data: MockTestData
        response = get_all_channels(base_url)
        response.status_code = 200
        verify_channel_unique_in_response(response, test_data.FOX.channel.channel)
        verify_channel_unique_in_response(response, test_data.CNN.channel.channel)
        verify_channel_unique_in_response(
            response, test_data.THE_GUARDIAN.channel.channel
        )

    @allure.title("Able to manage channels: Read")
    def test_get_single_channel_succeeds(self, base_url: str, test_data):
        test_data: MockTestData
        response = get_channel(base_url, test_data.CNN.channel.channel)
        assert response.status_code == 200
        assert response.json().get("description") == test_data.CNN.channel.description

    @allure.title("Able to manage channels: Create")
    def test_create_new_channel_succeeds(
        self, base_url: str, test_data, new_channel_payload: dict
    ):
        test_data: MockTestData

        expected_normalized_name = (
            new_channel_payload["channel"].upper().replace(" ", "_")
        )

        response = post_channel(base_url, new_channel_payload)
        assert response.status_code == 201
        assert response.json().get("channel") == expected_normalized_name

        channels = get_all_channels(base_url)
        verify_channel_unique_in_response(channels, expected_normalized_name)

    @allure.title("Able to manage channels: Update")
    def test_update_channel_succeeds(
        self,
        base_url: str,
        test_data,
        new_channel_payload: dict,
        channel_for_test: dict,
    ):
        channel = channel_for_test.get("channel")
        payload = {
            "description": f"Updated for integration testing {randint(0, 10000)}"
        }
        response = update_channel(base_url, payload, channel)
        response.status_code == 200
        response.json().get("description") == payload["description"]

    @allure.title("Able to manage channels: Delete")
    def test_delete_channel_succeeds(
        self,
        base_url: str,
        new_channel_payload: dict,
        channel_for_test: dict,
    ):
        channel = channel_for_test.get("channel")
        response = delete_channel(base_url, channel)
        assert response.status_code == 200
        assert get_channel(base_url, channel).status_code == 404
