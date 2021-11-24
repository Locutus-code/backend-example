import requests

from faker import Faker


class TestUsersApi:

    user_keys = ("identifier", "name", "phone_number")
    faker = Faker("fi-FI")

    def test_get_all_users_succeeds(self, base_url: str):
        response = requests.get(f"{base_url}/users")
        assert response.status_code == 200

        for user in response.json():
            for key in self.user_keys:
                assert key in user.keys()

    def test_get_single_user_succeeds(self, base_url: str):
        response = requests.get(f"{base_url}/users/1")
        assert response.status_code == 200
        user = response.json()
        assert user.get("identifier") == 1
        for key in self.user_keys:
            assert key in user.keys()

    def test_get_non_existing_single_user_fails(self, base_url: str):
        response = requests.get(f"{base_url}/users/10000")
        assert response.status_code == 404

    def test_create_new_user_succeeds(self, base_url):
        payload = {"name": self.faker.name(), "phone_number": "123456789"}
        response = requests.post(f"{base_url}/users", json=payload)
        assert response.status_code == 200

        user = response.json()
        assert user.get("name") == payload["name"]
        assert user.get("phone_number") == payload["phone_number"]
        assert isinstance(user.get("identifier"), int)

    def test_create_new_user_invalid_payload_fails(self, base_url):
        payload = {"name": self.faker.name(), "phone_number": None}
        response = requests.post(f"{base_url}/users", json=payload)
        assert response.status_code == 400

    def test_create_duplicate_user_fails(self, base_url):
        payload = {
            "identifier": 1,
            "name": self.faker.name(),
            "phone_number": "123456789",
        }
        response = requests.post(f"{base_url}/users", json=payload)
        assert response.status_code == 400

    def test_update_existing_user_succeeds(self, base_url):
        payload = {"name": self.faker.name(), "phone_number": self.faker.phone_number()}
        existing_user = requests.get(f"{base_url}/users/1").json()
        response = requests.put(f"{base_url}/users/1", json=payload)
        assert response.status_code == 200
        updated_user = response.json()

        assert updated_user.get("identifier") == existing_user.get("identifier")
        assert updated_user.get("name") == payload["name"]
        assert updated_user.get("phone_number") == payload["phone_number"]

        assert updated_user.get("name") != existing_user.get("name")
        assert updated_user.get("phone_number") != existing_user.get("phone_number")

    def test_update_non_existing_user_fails(self, base_url):
        payload = {"name": self.faker.name(), "phone_number": self.faker.phone_number()}
        response = requests.put(f"{base_url}/users/100000000", json=payload)
        print(response.text)
        assert response.status_code == 404

    def test_delete_existing_user_succeeds(self, base_url):
        response = requests.delete(f"{base_url}/users/1")
        assert response.status_code == 200
        assert response.json().get("status") == "Deleted"

    def test_delete_nonexisting_user_fails(self, base_url):
        response = requests.delete(f"{base_url}/users/1000000")
        assert response.status_code == 400
