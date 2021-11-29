"""SQS Triggered worker for scraping articles."""

import os
import json

import bs4
import requests
import boto3

from mypy_boto3_sqs import Client as SqsClient
from aws_lambda_powertools.utilities.parser import parse
from aws_lambda_powertools import Logger

from chalicelib.helpers.utils import now
from chalicelib.models.database import ArticleModel
from chalicelib.models.generic import (
    ScraperWorkerMessage,
    ArticleStatusEnum,
)


QUEUE_URL: str = os.environ.get("SCRAPER_QUEUE_URL")


def scraper_worker(body, receipt_handle):
    """Invoke by SQS Events."""
    message = parse(
        json.loads(body), ScraperWorkerMessage
    )  # FIXME: Use a extraction envelope
    ArticleScraper(message).scrape_article()
    sqs: SqsClient = boto3.client("sqs")
    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)


class ArticleScraper:
    """Class containing methods for scraping articles and updating their database entries"""

    def __init__(self, message: ScraperWorkerMessage):
        self.logger = Logger()
        self.scrapers = {
            "CNN": self._scrape_cnn,
            "FOX_NEWS": self._scrape_fox_news,
            "THE_GUARDIAN": self._scrape_the_guardian,
            "NU": self._scrape_nu,
        }
        self.article = ArticleModel.get(message.channel, message.id)
        self.logger.debug(self.article.attribute_values)

    def scrape_article(self):
        """Main scraper process."""
        try:
            self.logger.debug(f"origin url: {self.article.origin_url}")
            response = requests.get(self.article.origin_url)
            response.raise_for_status()
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.debug(f"text : {response.text[:50]}")
            soup = bs4.BeautifulSoup(response.text)
            scraper = self.scrapers.get(self.article.channel, self._scrape_best_effort)
            self.logger.debug(f"selected scraper: {scraper.__name__}")
            scraper(soup)
            self.article.status = ArticleStatusEnum.AVAILABLE
        except (
            bs4.ParserRejectedMarkup,
            requests.ConnectionError,
            requests.HTTPError,
        ) as exc:
            self.logger.debug(f"Scraping failure occured: {exc}")
            self.article.status = ArticleStatusEnum.FAILED
        finally:
            self.logger.debug(f"article_title: {self.article.title}")
            self.logger.debug(f"article_text: {self.article.article_text[:50]}")
            self.article.date = now()
            self.article.wordcount = len(self.article.article_text.split())
            self.article.save()

    def _scrape_cnn(self, soup: bs4.BeautifulSoup):
        self.article.title = soup.title.text
        self.article.article_text = "\n".join(
            [
                p.get_text()
                for p in soup.find_all("div", {"class": "zn-body__paragraph"})
            ]
        )

    def _scrape_fox_news(self, soup: bs4.BeautifulSoup):
        self.article.title = soup.title.text
        self.article.article_text = "\n".join(
            [
                p.get_text()
                for p in soup.find("div", {"class": "article-body"}).find_all("p")
            ]
        )

    def _scrape_the_guardian(self, soup: bs4.BeautifulSoup):
        self.article.title = soup.title.text
        self.article.article_text = soup.find("div", {"id": "maincontent"}).get_text()

    def _scrape_nu(self, soup: bs4.BeautifulSoup):
        self.article.title = soup.title.text
        self.article.article_text = soup.find(
            "div", {"class": "block article-body"}
        ).get_text()

    def _scrape_best_effort(self, soup: bs4.BeautifulSoup):
        self.article.title = soup.title.text
        self.article.article_text = soup.get_text()
