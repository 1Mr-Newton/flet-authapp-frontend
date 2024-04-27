from urllib.parse import parse_qs, urlparse
import flet as ft
from models.models import AuthEvents
from providers.providers import PageData
from routes.routes import Routes
from routes.router import ROUTER
import threading
import time


PUBLIC_ROUTES = [Routes.LOGIN_ROUTE, Routes.NOT_FOUND_ROUTE]


class ViewSates:
    def __init__(self):
        self.data = {}

    def get_view_state(self, route):
        return self.data.get(route, None)

    def set_view_state(self, route, view: ft.View):
        self.data[route] = view


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.data = PageData(page=page)
        self.views_state = ViewSates()
        self.page.snack_bar = ft.SnackBar(content=ft.Text(""))
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        self.page.data.auth.on_event_change = self.handle_event_change
        self.page.views.clear()
        self.page.data.auth.is_authenticated
        self._mount()

    def _mount(self):
        self.check_auth_thread = threading.Thread(target=self.check_authentication)
        self.check_auth_thread.daemon = True
        self.check_auth_thread.start()

    def check_authentication(self):
        while True:
            self.page.data.auth.is_authenticated
            time.sleep(0.5)

    def route_change(self, route):
        _route = urlparse(route.route)
        params = parse_qs(_route.query)
        params = {key: value[0] for key, value in params.items()}
        path = _route.path
        new_view_class = ROUTER.get(path)
        existing_view = self.views_state.get_view_state(path)
        if not self.page.data.auth.is_authenticated and path not in PUBLIC_ROUTES:
            return self.page.go(Routes.LOGIN_ROUTE)

        if params.get("clear", "").lower() == "true":
            self.page.views.clear()
            self.views_state.data.clear()
        if not new_view_class:
            return self.page.go(Routes.NOT_FOUND_ROUTE)

        elif not self.page.views or self.page.views[-1].route != path:
            view_to_use = existing_view if existing_view else new_view_class(self.page)
            self.page.views.append(view_to_use)
            self.views_state.set_view_state(path, view_to_use)
        self.page.update()

    def view_pop(self, event):
        if self.page.views:
            self.page.views.pop()
            if self.page.views:
                top_view = self.page.views[-1]
                self.page.go(top_view.route)

    def handle_event_change(self, event: AuthEvents, data):
        if event == AuthEvents.LOGIN:
            return self.page.data.navigator.replace(Routes.DASHBOARD_ROUTE)
        elif event == AuthEvents.LOGOUT:
            self.views_state.data.clear()

            return self.page.data.navigator.replace(Routes.LOGIN_ROUTE)
        elif event == AuthEvents.AUTH_CHECK:
            if not data:
                return self.page.data.navigator.replace(Routes.LOGIN_ROUTE)
            return self.page.data.navigator.replace(Routes.DASHBOARD_ROUTE)


ft.app(App, assets_dir="assets")
