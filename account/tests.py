import uuid
from unittest.mock import patch, MagicMock

import pytest
from factory import Faker
from factory.django import DjangoModelFactory
from rest_framework.test import APIClient
from rest_framework import status

from account.models import User


# Factory to create test users
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    id = Faker("uuid4")
    username = Faker("user_name")
    email = Faker("email")
    password = Faker("password")


@pytest.mark.django_db
class TestUserListView:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.admin_user.set_password("password")
        self.admin_user.save()
        self.normal_user = UserFactory(is_staff=False, is_superuser=False)
        self.normal_user.set_password("password")
        self.normal_user.save()

    def test_user_list_successful(self):
        # Authenticate as admin user
        self.client.login(username=self.admin_user.username, password="password")

        response = self.client.get("/user/", secure=True)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_user_list_unauthenticated(self):
        response = self.client.get("/user/", secure=True)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_list_forbidden(self):
        # Authenticate as normal user
        self.client.login(username=self.normal_user.username, password="password")

        response = self.client.get("/user/", secure=True)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_user_list_ordering(self):
        # Authenticate as admin user
        self.client.login(username=self.admin_user.username, password="password")

        response = self.client.get("/user/", {"ordering": "date_joined"}, secure=True)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

        # Assert ordering is correct
        results = response.data["results"]
        if results:
            assert all(
                results[i]["date_joined"] <= results[i + 1]["date_joined"]
                for i in range(len(results) - 1)
            )

    def test_user_list_pagination(self):
        # Authenticate as admin user
        self.client.login(username=self.admin_user.username, password="password")

        response = self.client.get("/user/", {"page_size": 1}, secure=True)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_user_list_search(self):
        # Authenticate as admin user
        self.client.login(username=self.admin_user.username, password="password")

        response = self.client.get(
            "/user/", {"search": self.normal_user.username}, secure=True
        )

        assert response.status_code == status.HTTP_200_OK
        assert any(
            user["username"] == self.normal_user.username
            for user in response.data["results"]
        )

    def test_user_profile_authenticated(self):
        # Prepare authenticated request
        self.client.login(username=self.admin_user.username, password="password")

        # Make profile request
        response = self.client.get("/user/profile/", secure=True)

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        # Add more assertions based on your serializer response structure
        assert "username" in response.data
        assert "email" in response.data

    def test_user_profile_unauthenticated(self):
        # Make profile request without authentication
        response = self.client.get("/user/profile/", secure=True)

        # Assert response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_retrieve_authenticated_owner(self):
        # Authenticate as the owner user
        self.client.force_login(self.admin_user)

        # Make retrieve request for own user id
        response = self.client.get(f"/user/{self.admin_user.id}/", secure=True)

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(
            self.admin_user.id
        )  # Example assertion based on serializer output

    def test_retrieve_authenticated_admin(self):
        # Create an admin user (if needed)
        admin_user = User.objects.create_superuser(
            username="admin", password="admin", email="admin@localhost"
        )

        # Authenticate as admin user
        self.client.force_login(admin_user)

        # Make retrieve request for another user id (in this case, self.user)
        response = self.client.get(f"/user/{self.admin_user.id}/", secure=True)

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(
            self.admin_user.id
        )  # Example assertion based on serializer output

    def test_retrieve_unauthenticated(self):
        # Make retrieve request without authentication
        response = self.client.get(f"/user/{self.admin_user.id}/", secure=True)

        # Assert response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )


@pytest.mark.django_db
class TestUserAuthEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

    def test_user_login_success(self):
        # Prepare test user
        username = "admin"
        password = "admin"
        user = User.objects.create_user(
            username=username, password=password, email="admin@localhost"
        )

        # Make login request
        response = self.client.post(
            "/user/login/", {"username": username, "password": password}, secure=True
        )

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_user_login_invalid_credentials(self):
        # Make login request with invalid credentials
        response = self.client.post(
            "/user/login/",
            {"username": "invalid_user", "password": "invalid_password"},
            secure=True,
        )

        # Assert response
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "Invalid credentials"

    @patch("account.utils.signinup.requests.post")
    @patch("account.views.requests.get")
    def test_wechat_mini_login_success(self, mock_requests_get, mock_requests_post):
        # Mock requests.get to return mocked data
        mock_requests_get.return_value.json.return_value = {
            "session_key": "session_key",
            "openid": "openid",
        }

        # Mock requests.post to return mocked data
        mock_response_post = MagicMock()
        mock_response_post.status_code = 201
        mock_response_post.json.return_value = {"user": {"id": str(uuid.uuid4())}}
        mock_requests_post.return_value = mock_response_post

        # Make wechat_mini_login request
        response = self.client.post(
            "/user/wechat_mini_login/", {"code": "mocked_code"}, secure=True
        )

        # Assert response
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_wechat_mini_login_missing_code(self):
        # Make wechat_mini_login request without code
        response = self.client.post("/user/wechat_mini_login/", {}, secure=True)

        # Assert response
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"][0] == "This field is required."

    @patch("account.views.requests.get")
    def test_wechat_mini_login_failure(self, mock_requests_get):
        # Mock requests.get to return empty data
        mock_requests_get.return_value.json.return_value = {}

        # Make wechat_mini_login request
        response = self.client.post(
            "/user/wechat_mini_login/", {"code": "mocked_code"}, secure=True
        )

        # Assert response
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["detail"] == "Can not get wechat openid"
