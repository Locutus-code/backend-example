"""Models of payloads and responses for Articles API."""

from uuid import UUID
from typing import List, Optional
from datetime import datetime
from aws_lambda_powertools.utilities.parser import BaseModel

from chalicelib.models.generic import ArticleStatusEnum


class PostArticleModel(BaseModel):
    """Create article payload."""

    url: str


class CreateArticleResponse(BaseModel):
    """Create article response.

    Caller will be issued a UUID id to poll for completion
    status is at this point always 'in progress' at create time
    """

    status: ArticleStatusEnum
    id: UUID


class GetSingleArticleModel(BaseModel):
    """API Representation of a single article descriptions used in enumerations.

    This model can directly ingress PynamoDB models.
    """

    class Config:
        orm_mode = True

    id: UUID
    title: str
    date: datetime
    wordcount: int


class GetArticlesModel(BaseModel):
    """Lists of article descriptions."""

    __root__: List[GetSingleArticleModel]


class GetFullArticleModel(BaseModel):
    """Article ful text.

    This model can directly ingress PynamoDB models.
    """

    class Config:
        orm_mode = True

    title: Optional[str]
    article_text: Optional[str]
    status: ArticleStatusEnum
