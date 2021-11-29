"""Models backed by DynamoDB tables."""

from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, IncludeProjection
from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    DiscriminatorAttribute,
)
from pynamodb_attributes import UUIDAttribute, TimestampAttribute, UnicodeEnumAttribute
from chalicelib.models.generic import ArticleStatusEnum


class ChannelIndex(GlobalSecondaryIndex):
    """Additional index for faster lookups."""

    class Meta:
        """Include projection only mirrors items required."""

        index_name = "channel-index"
        projection = IncludeProjection(["channel", "title", "id", "wordcount", "cls"])

    channel = NumberAttribute(hash_key=True)


class SingleTable(Model):
    """Container table for both Channel and Article models.

    Differentiating between object types is done using the `cls` discriminator attribute.

    Items are further segmented then using channe/id attributes.
    For channels, this simply becomes 'channel' (no duplicates allowed).
    For Articles, this is a str encoded UUID.

    This results then in a table design that looks like thus repeated for every channel:

    +-------+-------------+-------+--------------+-----------+--------------------------+
    |channel|id           |cls    |channel_url   |description|origin_url                |
    |       |             |       |              |           |                          |
    +-------+-------------+-------+--------------+-----------+--------------------------+
    |CNN    |channel      |channel|http://cnn.com|Some news  |                          |
    |       |             |       |              |website    |                          |
    +-------+-------------+-------+--------------+-----------+--------------------------+
    |CNN    |abcde-ffff-..|article|              |           |http://cnn/com/article_1  |
    +-------+-------------+-------+--------------+-----------+--------------------------+
    |CNN    |abcde-ffff-..|article|              |           |http://cnn/com/article_2  |
    +-------+-------------+-------+--------------+-----------+--------------------------+
    """

    class Meta:
        """Configurations required for creating table."""

        billing_mode = "PAY_PER_REQUEST"
        table_name = "Channels"
        region = "eu-west-1"

    channel = UnicodeAttribute(hash_key=True)
    id = UnicodeAttribute(range_key=True)
    cls = DiscriminatorAttribute()
    channel_index = ChannelIndex()


class ChannelModel(SingleTable, discriminator="Channel"):
    """Channel objects are stored on the parent table."""

    id = UnicodeAttribute(range_key=True)
    channel_url = UnicodeAttribute()
    description = UnicodeAttribute()
    date = TimestampAttribute()


class ArticleModel(SingleTable, discriminator="Article"):
    """Article objects are stored on the parent table."""

    id = UUIDAttribute(range_key=True)
    status = UnicodeEnumAttribute(ArticleStatusEnum, null=True)
    title = UnicodeAttribute(null=True)
    wordcount = NumberAttribute(null=True)
    date = TimestampAttribute(null=True)
    origin_url = UnicodeAttribute(null=True)
    article_text = UnicodeAttribute(null=True)
    channel_index = ChannelIndex()
