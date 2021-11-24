from typing import List, Dict, Optional

from enum import Enum

from uuid import UUID
from datetime import datetime, timedelta

from chalice import (
    Blueprint,
    Response,
    NotFoundError,
    BadRequestError,
)

from aws_lambda_powertools.utilities.parser import parse, ValidationError
from aws_lambda_powertools.utilities.parser import BaseModel


class ProjectTypeEnum(Enum):
    CUSTOMER = "customer"
    CIRCLES_INTERNAL = "circles"
    CIRCLES_WORKGROUP = "workgroups"
    SELFSTUDY = "selfstudy"


class ProjectModel(BaseModel):
    id: UUID
    name: str
    project_type: ProjectTypeEnum
    circle: Optional[str]
    customer: Optional[str]


class GetProjectsModel(BaseModel):
    __root__: List[ProjectModel]


class DailyReportModel(BaseModel):
    project: UUID
    description: str
    date: datetime
    duration: timedelta


class DailyReportEvent(BaseModel):
    __root__: List[DailyReportModel]


class GetCalendarModel(BaseModel):
    __root__: List[DailyReportEvent]


class PostTimeEntryModel(BaseModel):
    __root__: List[DailyReportModel]


class SuccessResponseModel(BaseModel):
    status: str = "OK"


timetracking = Blueprint(__name__)


@timetracking.route("/projects", methods=["GET"])
def get_current_user_projects() -> GetProjectsModel:
    raise NotImplemented


@timetracking.route("/calendar", methods=["GET"])
def get_current_user_calendar() -> GetCalendarModel:
    month = app.request.query_params["month"]
    year = app.request.query_params["year"]
    raise NotImplemented


@timetracking.route("/timeentry", methods=["POST"])
def insert_new_timeentries_for_current_user() -> SuccessResponseModel:
    data = parse(app.current_request.json_body, PostTimeEntryModel)
    raise NotImplemented
