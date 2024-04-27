import flet as ft
from models.models import LoginResponse
from routes.routes import Routes


class LoginScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route=Routes.LOGIN_ROUTE)
        self.page: ft.Page = page
        self.expand = True

        self.username = ft.Ref()
        self.passwordRef = ft.Ref()

        self.controls = [
            ft.TextField(
                ref=self.username,
                label="Username",
                value="test",
            ),
            ft.TextField(
                ref=self.passwordRef,
                value="test123.",
                label="Password",
            ),
            ft.ElevatedButton(
                text="Login",
                on_click=self.login,
            ),
            ft.ElevatedButton(
                text="Visit Protected Route",
                on_click=lambda _: self.page.data.navigator.push(
                    Routes.DASHBOARD_ROUTE
                ),
            ),
        ]

    def login(self, e):
        response: LoginResponse = self.page.data.auth.login(
            username=self.username.current.value,
            password=self.passwordRef.current.value,
        )
        status_code = response.status_code
        detail = response.detail
        if self.page and self.page.snack_bar and status_code != 200:
            self.page.snack_bar.content = ft.Text(
                detail or "An error occurred while trying to login."
            )
            self.page.snack_bar.open = True
            self.page.update()
