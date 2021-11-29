"""Manager for operating on Channels."""


from chalice.app import BadRequestError, NotFoundError, ConflictError
from chalicelib.helpers.utils import now
from chalicelib.models.database import (
    ChannelModel,
    ArticleModel,
)
from chalicelib.models.generic import StatusOkMsg
from chalicelib.models.payloads.channels import (
    PostSingleChannelModel,
    GetSingleChannelModel,
    GetChannelsModel,
    UpdateSingleChannelModel,
)


class ChannelManager:
    """Manager class containing methods for operating on Channels."""

    def save_channel(self, payload: PostSingleChannelModel) -> PostSingleChannelModel:
        """Create a new channel."""
        payload.channel = payload.channel.upper().replace(" ", "_")
        try:
            ChannelModel.get(payload.channel, "Channel")
            raise ConflictError(f"Channel {payload.channel} already exists")
        except ChannelModel.DoesNotExist:
            channel = ChannelModel(**payload.dict())
            channel.date = now()
            channel.id = "Channel"
            channel.save()
            return payload

    def update_channel(
        self, channel: str, payload: UpdateSingleChannelModel
    ) -> StatusOkMsg:
        """Update an existing channel."""
        try:
            channel = ChannelModel.get(channel, "Channel")
            channel.description = payload.description
            channel.save()
            return StatusOkMsg(status="OK", message="Updated")
        except ChannelModel.DoesNotExist:
            raise NotFoundError(f"Channel {channel} doesn't exist")

    def delete_channel(self, channel: str) -> StatusOkMsg:
        """Delete an existing channel and all its articles."""
        try:
            ChannelModel.get(channel, "Channel").delete()
        except ChannelModel.DoesNotExist:
            raise NotFoundError(f"Channel {channel} doesn't exist")
        articles = ArticleModel.query(channel)
        with ArticleModel.batch_write() as batch:
            for article in articles:
                article.delete()
            batch.commit()
        return StatusOkMsg(status="OK", message="Deleted")

    def get_all_channels(self) -> GetChannelsModel:
        """Get all channels and their descriptions."""
        return GetChannelsModel.parse_obj(
            [GetSingleChannelModel.from_orm(n) for n in ChannelModel.scan()]
        )

    def get_single_channel(self, channel) -> GetSingleChannelModel:
        """Get a single channel."""
        try:
            channel = ChannelModel.get(channel, "Channel")
            return GetSingleChannelModel.from_orm(channel)
        except ChannelModel.DoesNotExist:
            raise NotFoundError(f"Channel {channel} does not exist")
