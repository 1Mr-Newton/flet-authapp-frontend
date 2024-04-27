import base64
import json
from datetime import datetime
import requests


class AuthProvider:
    def __init__(self, *, page):
        self.page = page
        self.on_event_change = None  # Placeholder for the callback function

    @property
    def is_authenticated(self):
        access_token = self.get_access_token()
        if not access_token:
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
                    return False
                return True
        except Exception as e:
            print(f"Error decoding JWT: {e}")
            return False

    def get_access_token(self):
        return self.page.client_storage.get("access_token")

    def login(self, username: str, password: str):
        try:
            url = "http://0.0.0.0:8000/token"
            headers = {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            data = {"username": username, "password": password}

            response = requests.post(url, headers=headers, data=data)
            response_data = response.json()
            response_data["status_code"] = response.status_code

            if response.status_code == 200:
                self.page.client_storage.set(
                    "access_token", response_data["access_token"]
                )
                self.page.client_storage.set(
                    "refresh_token", response_data["refresh_token"]
                )
                if self.on_event_change:
                    self.on_event_change("LOGIN", response_data)
            return response_data
        except Exception as e:
            print(e)
            return {
                "detail": "Login failed. Please try again later.",
                "status_code": 500,
            }

    def logout(self):
        self.page.client_storage.remove("access_token")
        self.page.client_storage.remove("refresh_token")
        if self.on_event_change:
            self.on_event_change("LOGOUT", True)


# Example of setting up the callback function
def my_callback_func(event_type, data):
    if event_type == "LOGIN":
        print("User logged in. Access token:", data.get("access_token"))
    elif event_type == "LOGOUT":
        print("User logged out.")


# Assuming 'page' is previously defined somewhere in your code
auth_provider = AuthProvider(page=page)
auth_provider.on_event_change = my_callback_func
