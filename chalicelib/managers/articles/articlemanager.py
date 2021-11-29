"""Manager for operating on Articles."""

import os
from uuid import uuid4

import boto3

from chalice.app import BadRequestError, NotFoundError
from mypy_boto3_sqs import Client as SqsClient

from chalicelib.models.database import (
    ChannelModel,
    ArticleModel,
)
from chalicelib.models.payloads.articles import (
    GetArticlesModel,
    GetSingleArticleModel,
    GetFullArticleModel,
    PostArticleModel,
    CreateArticleResponse,
)
from chalicelib.models.generic import ArticleStatusEnum, ScraperWorkerMessage

QUEUE_URL: str = os.environ.get("SCRAPER_QUEUE_URL")


class ArticleManager:
    """Manager class containing methods for operating on Articles."""

    def get_articles_by_channel(
        self, channel, min_words=0, max_words=100000
    ) -> GetArticlesModel:
        """
        Return all articles belonging to a channel.

        Optionally filter by word count
        """
        articles = ArticleModel.query(
            channel,
            filter_condition=ArticleModel.wordcount.between(min_words, max_words),
        )
        return GetArticlesModel.parse_obj(
            [GetSingleArticleModel.from_orm(n) for n in articles]
        )

    def get_single_article_by_id(
        self, channel: str, article_id: str
    ) -> GetFullArticleModel:
        """Get a full article including its body text."""
        try:
            article = ArticleModel.get(channel, article_id)
            return GetFullArticleModel.from_orm(article)
        except ArticleModel.DoesNotExist:
            raise NotFoundError(f"Article {article_id} does not exist")

    def create_article_work_item(
        self, channel: str, payload: PostArticleModel
    ) -> CreateArticleResponse:
        """Initiate the process to create and scrape a new article."""
        try:
            ChannelModel.get(channel, "Channel")
        except ChannelModel.DoesNotExist:
            raise BadRequestError(f"Channel {channel} does not exist")

        article = ArticleModel(channel, uuid4())
        article.channel = channel
        article.origin_url = payload.url
        article.status = ArticleStatusEnum.IN_PROGRESS
        article.save()

        msg = ScraperWorkerMessage(id=article.id, url=payload.url, channel=channel)
        sqs: SqsClient = boto3.client("sqs")
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=msg.json())
        return CreateArticleResponse(
            id=article.id, status=ArticleStatusEnum.IN_PROGRESS.value
        )
