import os
from random import SystemRandom
from urllib.parse import urlencode

import jwt
import requests
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.http import JsonResponse
from oauthlib.common import UNICODE_ASCII_CHARACTER_SET
from rest_framework import status

from .serializers import PersonSerializer


class GoogleRawLoginCredentials:
    def __init__(self, client_id: str, client_secret: str, project_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.project_id = project_id


class GoogleAccessTokens:
    def __init__(self, id_token: str, access_token: str):
        self.id_token = id_token
        self.access_token = access_token

    def decode_id_token(self) -> [str, str]:
        id_token = self.id_token
        decoded_token = jwt.decode(jwt=id_token, options={"verify_signature": False})
        return decoded_token


def google_raw_login_get_credentials() -> GoogleRawLoginCredentials:
    client_id = os.environ.get("GOOGLE_OAUTH2_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_OAUTH2_CLIENT_SECRET")
    project_id = os.environ.get("GOOGLE_OAUTH2_PROJECT_ID")

    if not client_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_ID missing in env.")

    if not client_secret:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_CLIENT_SECRET missing in env.")

    if not project_id:
        raise ImproperlyConfigured("GOOGLE_OAUTH2_PROJECT_ID missing in env.")

    credentials = GoogleRawLoginCredentials(
        client_id=client_id, client_secret=client_secret, project_id=project_id
    )

    return credentials


class GoogleRawLoginFlowService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

    SCOPES = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self._credentials = google_raw_login_get_credentials()

    @staticmethod
    def _generate_state_session_token(length=30, chars=UNICODE_ASCII_CHARACTER_SET):
        rand = SystemRandom()
        state = "".join(rand.choice(chars) for _ in range(length))
        return state

    def _get_redirect_uri(self):
        return "https://api.workasync.com/api/user/google-login/"

    def get_tokens(self, *, code: str) -> GoogleAccessTokens:
        redirect_uri = self._get_redirect_uri()

        data = {
            "code": code,
            "client_id": self._credentials.client_id,
            "client_secret": self._credentials.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

        tokens = response.json()
        google_tokens = GoogleAccessTokens(
            id_token=tokens["id_token"], access_token=tokens["access_token"]
        )

        return google_tokens

    def get_authorization_url(self):
        redirect_uri = self._get_redirect_uri()

        state = self._generate_state_session_token()

        params = {
            "response_type": "code",
            "client_id": self._credentials.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "access_type": "offline",
            "include_granted_scopes": "true",
            "prompt": "select_account",
        }

        query_params = urlencode(params)
        authorization_url = f"{self.GOOGLE_AUTH_URL}?{query_params}"

        return authorization_url, state

    def get_user_info(self, *, google_tokens: GoogleAccessTokens):
        access_token = google_tokens.access_token

        response = requests.get(
            self.GOOGLE_USER_INFO_URL, params={"access_token": access_token}
        )

        return response.json()


def create_user(person_data):
    user = User.objects.create(
        username=person_data["email"],
        email=person_data["email"],
        first_name=person_data["first_name"],
        last_name=person_data["last_name"],
        is_superuser=False,
        is_active=True,
        is_staff=False,
    )
    user.set_password(person_data["password"])
    user.save()
    return user


def handle_person_serializer(user, person_data):
    person_data["user"] = user.id
    person_serializer = PersonSerializer(data=person_data)
    if person_serializer.is_valid():
        person_serializer.save()
        return JsonResponse(person_serializer.data, status=status.HTTP_201_CREATED)
    else:
        user.delete()
        return JsonResponse(
            person_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
