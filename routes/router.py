from routes.routes import Routes
from screens.dashboard import Dashboard
from screens.login import LoginScreen

ROUTER = {
    Routes.DASHBOARD_ROUTE: Dashboard,
    Routes.LOGIN_ROUTE: LoginScreen,
}
