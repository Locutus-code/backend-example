"""Models of payloads and responses for Channel API."""


from typing import List, Optional
from datetime import datetime
from aws_lambda_powertools.utilities.parser import BaseModel


class PostSingleChannelModel(BaseModel):
    """Creation payload for a channel."""

    channel: str
    description: str
    channel_url: Optional[str]


class GetSingleChannelModel(BaseModel):
    """API representation of a single Channel."""

    class Config:
        """This Response can directly ingress PynamoDB Models."""

        orm_mode = True

    channel: str
    description: str
    channel_url: str
    date: datetime


class GetChannelsModel(BaseModel):
    """List of Channels."""

    __root__: List[Optional[GetSingleChannelModel]]


class UpdateSingleChannelModel(BaseModel):
    """Update payload for a channel.

    Only descriptions can be changed after creation.
    """

    description: Optional[str]
