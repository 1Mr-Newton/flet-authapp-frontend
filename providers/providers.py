import json
import base64
import flet as ft
import requests
from config.config import Config, Endpoints
from models.models import AuthEvents, LoginResponse
from datetime import datetime
from typing import Any, Callable, Dict, Optional

EventHandler = Callable[[AuthEvents, Dict | Any], None]


class AuthProvider:
    def __init__(self, *, page: ft.Page):
        self.page: ft.Page = page
        self.on_event_change: Optional[EventHandler] = None

    @property
    def is_authenticated(self) -> bool:
        access_token = self.get_access_token()
        if not access_token:
            if self.on_event_change:
                self.on_event_change(AuthEvents.AUTH_CHECK, False)
            return False
        try:
            payload = access_token.split(".")[1]
            decoded_bytes = base64.urlsafe_b64decode(payload + "==")
            decoded_payload = decoded_bytes.decode("utf-8")

            payload_data = json.loads(decoded_payload)

            exp = payload_data.get("exp")
            if exp:
                exp_date = datetime.utcfromtimestamp(exp)
                if exp_date < datetime.utcnow():
                    if self.on_event_change:
                        self.on_event_change(AuthEvents.AUTH_CHECK, False)
                    return False
                if self.on_event_change:
                    self.on_event_change(AuthEvents.AUTH_CHECK, True)
                return True
        except Exception as e:
            if self.on_event_change:
                self.on_event_change(AuthEvents.AUTH_CHECK, False)
            return False
        return False

    def get_access_token(self):
        access_token = self.page.client_storage.get(Config.ACCESS_TOKEN_KEY)
        return access_token

    def login(self, username: str, password: str):
        try:
            url = "http://0.0.0.0:8000/token"

            headers = {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            data = {
                "grant_type": "",
                "username": username,
                "password": password,
                "scope": "",
                "client_id": "",
                "client_secret": "",
            }

            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()
            response_data["status_code"] = response.status_code
            if response.status_code == 200:
                self.save_text(Config.ACCESS_TOKEN_KEY, response_data["access_token"])
                self.save_text(Config.REFRESH_TOKEN_KEY, response_data["refresh_token"])

                if self.on_event_change:
                    self.on_event_change(AuthEvents.LOGIN, response_data)

            return LoginResponse(**response_data)
        except Exception as e:

            return LoginResponse(
                detail="An error occurred while trying to login. \nPlease try again later.",
                status_code=500,
                access_token=None,
                refresh_token=None,
                token_type=None,
            )

    def save_text(self, key, value):
        self.page.client_storage.set(key, value)

    def logout(self, e):
        self.page.client_storage.remove(Config.ACCESS_TOKEN_KEY)
        self.page.client_storage.remove(Config.REFRESH_TOKEN_KEY)
        if self.on_event_change:
            self.on_event_change(AuthEvents.LOGOUT, True)

    def access_token_refresh(self):
        refresh_token = self.page.client_storage.get(Config.REFRESH_TOKEN_KEY)
        if not refresh_token:
            if self.on_event_change:
                self.on_event_change(AuthEvents.ACCESS_TOKEN_REFRESH, False)
            return False

        try:
            url = "http://0.0.0.0:8000/refresh"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = {
                "refresh_token": refresh_token,
            }
            response = requests.post(url, headers=headers, data=payload)
            response_data = response.json()
            response_data["status_code"] = response.status_code
            if response.status_code == 200:
                self.save_text(Config.ACCESS_TOKEN_KEY, response_data["access_token"])
                self.save_text(Config.REFRESH_TOKEN_KEY, response_data["refresh_token"])

                if self.on_event_change:
                    self.on_event_change(AuthEvents.ACCESS_TOKEN_REFRESH, response_data)
            return LoginResponse(**response_data)
        except Exception as e:
            if self.on_event_change:
                self.on_event_change(AuthEvents.ACCESS_TOKEN_REFRESH, False)
            print("Error occurred while refreshing token", e)
            return LoginResponse(
                detail="An error occurred while trying to refresh token. \nPlease try again later.",
                status_code=500,
                access_token=None,
                refresh_token=None,
                token_type=None,
            )

    def send_request_to_backend(
        self,
        *,
        url: str,
        method: str,
        headers: Dict[str, str] = {},
        data: Dict[str, Any] | None = None,
    ):
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {
                    "status_code": 401,
                    "detail": "Unauthorized",
                    "data": None,
                }
            headers["Authorization"] = f"Bearer {access_token}"
            response = requests.request(method, url, headers=headers, data=data)
            response_data = response.json()
            response_data["status_code"] = response.status_code
            return response_data
        except Exception as e:
            print("Error occurred while sending request", e)
            return {
                "status_code": 500,
                "detail": "An error occurred while sending request",
                "data": None,
            }

    def current_user(self, e: ft.TapEvent | None = None):
        url = Config.BACKEND_BASE_URL + Endpoints.ME
        response = self.send_request_to_backend(
            url=url,
            method="GET",
        )
        return response if response["status_code"] == 200 else None


class NavigationProvider:
    def __init__(self, *, page: ft.Page):
        self.page = page

    def push(self, path: str, **params):
        self.page.go(path, **params)

    def replace(self, path: str, **params):
        self.page.go(path, clear=True, **params)


class PageData:
    def __init__(self, page: ft.Page):
        self.attributes = {}
        self.auth = AuthProvider(page=page)
        self.navigator = NavigationProvider(page=page)

    def add(self, key, value):
        self.attributes[key] = value

    def jie(self, key):
        if key in self.attributes:
            del self.attributes[key]

    def get(self, key):
        return self.attributes.get(key, None)

    def __repr__(self):
        return str(self.attributes)


class ViewSates:
    def __init__(self):
        self.data = {}

    def get_view_state(self, route):
        return self.data.get(route, None)

    def set_view_state(self, route, view: ft.View):
        self.data[route] = view
