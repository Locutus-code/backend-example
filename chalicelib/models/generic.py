"""Module for shared types."""

from uuid import UUID
from enum import Enum
from aws_lambda_powertools.utilities.parser import BaseModel


class StatusOkMsg(BaseModel):
    status: str
    message: str


class StatusFailMsg(BaseModel):
    status: str
    message: str


class ArticleStatusEnum(Enum):
    """Possible worker states for articles."""

    AVAILABLE = "available"
    IN_PROGRESS = "in progress"
    FAILED = "failed"


class ScraperWorkerMessage(BaseModel):
    """SQS Message payload for REST API to trigger async worker."""

    id: UUID
    channel: str
    url = str
