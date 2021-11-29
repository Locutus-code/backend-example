from chalice import (
    Blueprint,
    Response,
)

from aws_lambda_powertools.utilities.parser import parse
from chalicelib.managers.channels.channelmanager import ChannelManager
from chalicelib.models.payloads.channels import (
    GetChannelsModel,
    PostSingleChannelModel,
    UpdateSingleChannelModel,
    GetSingleChannelModel,
)
from chalicelib.models.generic import StatusOkMsg, StatusFailMsg

channels = Blueprint(__name__)


@channels.route("/channels", methods=["GET"])
def get_all_channels() -> GetChannelsModel:
    """
    summary: Get a list of all channels and their descriptions.
    responses:
        200:
            description: GetChannelsModel
            schema:
                $ref: '#/definitions/GetChannelsModel'
    """
    return Response(status_code=200, body=ChannelManager().get_all_channels().json())


@channels.route("/channels", methods=["POST"])
def post_new_channel() -> PostSingleChannelModel:
    """
    summary: Create a new channel in system.
    responses:
        201:
            description: PostSingleChannelModel
            schema:
                $ref: '#/definitions/PostSingleChannelModel'
        409:
            description: PostSingleChannelConflict
            schema:
                $ref: '#/definitions/StatusMsgFail'
    """
    payload = parse(channels.current_request.json_body, model=PostSingleChannelModel)
    return Response(status_code=201, body=ChannelManager().save_channel(payload).json())


@channels.route("/channels/{channel}", methods=["PUT"])
def update_channel(channel: str) -> StatusOkMsg:
    """
    summary: Update a currently existing channel.
    responses:
        200:
            description: StatusOkMsg
            schema:
                $ref: '#/definitions/StatusOkMsg'
        404:
            description: UpdateChannelNotFoundmsg
            schema:
                $ref: '#/definitions/StatusMsgFail'
    """
    payload = parse(channels.current_request.json_body, UpdateSingleChannelModel)
    return Response(
        status_code=200, body=ChannelManager().update_channel(channel, payload).json()
    )


@channels.route("/channels/{channel}", methods=["DELETE"])
def delete_channel(channel: str):
    """
    summary: Delete a channel and all its articles.
    responses:
        200:
            description: StatusOkMsg
            schema:
                $ref: '#/definitions/StatusOkMsg'
    """
    return Response(
        status_code=200, body=ChannelManager().delete_channel(channel).json()
    )


@channels.route("/channels/{channel}", methods=["GET"])
def get_single_channel(channel: str) -> GetSingleChannelModel:
    """
    summary: Get a single channel.
    responses:
        200:
            description: GetSingleChannelModel
            schema:
                $ref: '#/definitions/GetSingleChannelModel'
        404:
            description: GetChannelNotFoundmsg
            schema:
                $ref: '#/definitions/StatusMsgFail'
    """
    return Response(
        status_code=200, body=ChannelManager().get_single_channel(channel).json()
    )
