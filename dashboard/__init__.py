from app.factory import create_app

from .factory import create_dashboard

app = create_app()

dashboard = create_dashboard(app)


if __name__ == "__main__":
    dashboard.run_server()
