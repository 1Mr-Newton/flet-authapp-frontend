import threading
from time import sleep
import flet as ft
from helpers.send_request import send_request
from routes.routes import Routes


class Dashboard(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route=Routes.DASHBOARD_ROUTE)
        self.page: ft.Page = page
        self.expand = True
        self.bgcolor = "blue"
        self.is_fetching_user = True
        self.circle_avata_ref = ft.Ref()
        self.username_ref = ft.Ref()

        self._mount()

    def _mount(self):
        self.appbar = ft.AppBar(
            title=ft.Text("Dashboard"),
            adaptive=True,
            actions=[
                ft.CircleAvatar(
                    ref=self.circle_avata_ref,
                    foreground_image_src="https://avatars.githubusercontent.com/u/47231147?v=4",
                ),
                ft.IconButton(
                    icon="logout",
                    on_click=self.page.data.auth.logout,
                ),
            ],
            toolbar_height=80,
        )
        self.controls = [
            ft.Text(
                value="Good Morning, ",
                size=20,
                weight=ft.FontWeight.BOLD,
                spans=[
                    ft.TextSpan(
                        text="",
                        style=ft.TextStyle(
                            size=18,
                            weight=ft.FontWeight.W_400,
                        ),
                        ref=self.username_ref,
                    ),
                ],
            ),
            ft.ElevatedButton(
                text="Logout",
                on_click=self.page.data.auth.logout,
            ),
            ft.ElevatedButton(
                text="Settings",
                on_click=self.go_to_settings,
            ),
        ]
        self.start_user_fetch()

    def start_user_fetch(self, id=1):
        thread = threading.Thread(target=self.update_user_data)
        thread.start()

    def update_user_data(self, e: ft.TapEvent | None = None):
        data = self.page.data.auth.current_user(e)
        if not data:
            self.page.data.auth.logout()
            return
        self.username_ref.current.text = data["username"].title()
        self.username_ref.current.update()

    def go_to_settings(self, e):
        self.page.data.navigator.push(Routes.SETTINGS_ROUTE)
        self.page.update()
