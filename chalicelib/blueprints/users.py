from chalice import (
    Blueprint,
    Response,
    NotFoundError,
    BadRequestError,
)

from aws_lambda_powertools.utilities.parser import parse, ValidationError

from chalicelib.managers.users.usermanager import UserManager
from chalicelib.models.user import UserModel

usersapi = Blueprint(__name__)


@usersapi.route("/users", methods=["GET"])
def get_users_list():
    return Response(status_code=200, body=UserManager().get_all_users().json())


@usersapi.route("/users/{identifier}", methods=["GET"])
def get_single_user(identifier):
    user = UserManager().get_user_by_identifier(int(identifier))
    if user:
        return Response(status_code=200, body=user.json())
    raise NotFoundError(f"User {identifier} not found")


@usersapi.route("/users/{identifier}", methods=["DELETE"])
def delete_single_user(identifier):
    return Response(
        status_code=200, body=UserManager().delete_user(int(identifier)).json()
    )


@usersapi.route("/users", methods=["POST"])
def user_post():
    try:
        payload = parse(
            usersapi.current_request.json_body,
            model=UserModel,
        )
    except ValidationError as exc:
        raise BadRequestError(f"bad payload: f{exc}") from exc
    return Response(status_code=200, body=UserManager().insert_new_user(payload).json())


@usersapi.route("/users/{identifier}", methods=["PUT"])
def user_update(identifier):
    try:
        payload = parse(
            usersapi.current_request.json_body,
            model=UserModel,
        )
    except ValidationError as exc:
        raise BadRequestError(f"bad payload: f{exc}") from exc
    return Response(
        status_code=200, body=UserManager().update_user(int(identifier), payload).json()
    )
