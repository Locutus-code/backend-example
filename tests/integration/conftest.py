"""Test preconditions used by all integration tests.

Fixtures that are scoped at session level should be here.
"""
from typing import List
from dataclasses import dataclass
from uuid import uuid4
from random import randint
import pytest
from faker import Faker

from chalicelib.models.database import ChannelModel, ArticleModel
from chalicelib.models.generic import ArticleStatusEnum
from chalicelib.helpers.utils import now


@dataclass
class Channel:
    channel: ChannelModel
    articles: List[ArticleModel]


@dataclass
class MockTestData:
    FOX: Channel
    CNN: Channel
    THE_GUARDIAN: Channel


@pytest.fixture(scope="session")
def test_data() -> MockTestData:
    """Generate testdata for use by integration tests."""
    faker = Faker()
    channels = ("FOX", "CNN", "THE_GUARDIAN")
    output = {}
    for channel in channels:
        output[channel] = {}
        channel_model = ChannelModel(
            channel=channel,
            id="Channel",
            channel_url=faker.url(),
            description=faker.catch_phrase(),
            date=now(),
        )
        channel_model.save()
        output[channel]["channel"] = channel_model
        output[channel]["articles"] = []
        for n in range(0, 5):
            article_text = faker.text(randint(25, 10000))
            word_count = len(article_text.split())
            article = ArticleModel(
                channel=channel,
                id=uuid4(),
                title=faker.catch_phrase(),
                article_text=article_text,
                wordcount=word_count,
                date=now(),
                origin_url=faker.url(),
                status=ArticleStatusEnum.AVAILABLE,
            )
            output[channel]["articles"].append(article)
            article.save()

    test_data = MockTestData(
        FOX=Channel(**output["FOX"]),
        CNN=Channel(**output["CNN"]),
        THE_GUARDIAN=Channel(**output["THE_GUARDIAN"]),
    )
    yield test_data

    def __cleanup(dataset: Channel):
        dataset.channel.delete()
        for article in dataset.articles:
            article.delete()

    __cleanup(test_data.CNN)
    __cleanup(test_data.FOX)
    __cleanup(test_data.THE_GUARDIAN)
