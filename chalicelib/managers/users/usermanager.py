from typing import Optional
from faker import Faker

from chalice import (
    BadRequestError,
    NotFoundError,
)

from chalicelib.models.user import UserModel, UsersList, UserDeletionResponse


class UserManager:
    def __init__(self):
        self.faker = Faker("fi-FI")
        self._users_db = None

    @property
    def users_db(self) -> UsersList:
        if not self._users_db:
            data = []
            for identifier in range(1, 10):
                data.append(
                    UserModel(
                        identifier=identifier,
                        name=self.faker.name(),
                        phone_number=self.faker.phone_number(),
                    )
                )
            self._users_db = UsersList(__root__=data)
        return self._users_db

    def get_all_users(self) -> UsersList:
        return self.users_db

    def get_user_by_identifier(self, identifier: int) -> Optional[UserModel]:
        result = list(
            filter(lambda x: x.identifier == identifier, self.users_db.__root__)
        )
        if result:
            return result[0]
        return None

    def insert_new_user(self, payload: UserModel) -> UserModel:
        if payload.identifier:
            raise BadRequestError("Cannot overwrite existing user")
        payload.identifier = (
            max([user.identifier for user in self.users_db.__root__]) + 1
        )
        return payload

    def update_user(self, identifier: int, payload: UserModel) -> UserModel:
        user = self.get_user_by_identifier(identifier)
        if not user:
            raise NotFoundError(f"Requested user {identifier} does not exist")
        user = user.copy(update=payload.dict(exclude_unset=True))
        return user

    def delete_user(self, identifier: int) -> UserDeletionResponse:
        if not self.get_user_by_identifier(identifier):
            raise BadRequestError("Cannot delete non-existing user")
        return UserDeletionResponse(identifier=identifier)
