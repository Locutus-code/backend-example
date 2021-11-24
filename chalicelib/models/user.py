from typing import Optional, List

from aws_lambda_powertools.utilities.parser import BaseModel


class UserModel(BaseModel):
    class Config:
        validate_assignment = True

    identifier: Optional[int]
    name: str
    phone_number: str


class UsersList(BaseModel):
    class Config:
        validate_assignment = True

    __root__: List[UserModel]


class UserDeletionResponse(BaseModel):
    status: str = "Deleted"
    identifier: int
