from typing import List
from uuid import UUID
from logging import getLogger
from time import sleep
from datetime import datetime, timedelta


import allure

from tests.integration.conftest import test_data, MockTestData
from tests.integration.steps import (
    channel_for_test,
    log_response,
    get_articles_by_channel,
    get_single_article,
    post_article_scrape_request,
)


@allure.story("Able to manage Articles")
class TestArticlesApi:
    logger = getLogger()

    @allure.title("Able to manage articles: Enumerate")
    def test_get_all_articles_by_channel_succeeds(
        self, base_url: str, test_data: MockTestData
    ):
        test_data: MockTestData
        response = get_articles_by_channel(base_url, test_data.CNN.channel.channel)
        assert response.status_code == 200
        articles: List = response.json()
        assert len(articles) >= 1

    @allure.title("Able to manage articles: Get single")
    def test_get_single_article_succeeds(self, base_url: str, test_data: MockTestData):
        test_data: MockTestData

        expected_article = test_data.CNN.articles[0]

        response = get_single_article(
            base_url, test_data.CNN.channel.channel, expected_article.id
        )
        assert response.status_code == 200
        article = response.json()
        assert article.get("title") == expected_article.title
        assert article.get("article_text") == expected_article.article_text

    @allure.title("Able to manage articles: Create article")
    def test_create_article_succeeds(self, base_url: str, test_data: MockTestData):
        test_data: MockTestData

        channel = test_data.CNN.channel.channel
        payload = {
            "url": "https://edition.cnn.com/2021/11/25/china/who-is-zhang-gaoli-intl-hnk-dst/index.html"
        }
        response = post_article_scrape_request(base_url, channel, payload)
        assert response.status_code == 202
        article_id = response.json().get("id")
        assert UUID(article_id)

        time = datetime.now()
        timeout = time + timedelta(seconds=70)
        while time <= timeout:
            response = get_single_article(base_url, channel, article_id).json()
            article_status = response.get("status")
            if article_status == "in progress":
                sleep(1)
                time = datetime.now()
            if article_status == "failure":
                raise AssertionError("Article failed parsing")
            if article_status == "available":
                break
        assert response["article_text"]
        assert response["title"]
