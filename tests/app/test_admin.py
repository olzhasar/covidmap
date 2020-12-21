import base64


class TestAdmin:
    def test_unauthorized(self, client):
        response = client.get("/admin/")
        assert response.status_code == 401

    def test_incorrect_password(self, client):
        credentials = base64.b64encode(b"wrong:wrong").decode("utf-8")

        response = client.get(
            "/admin/", headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 401

    def test_authorized(self, config, client):
        username = config["BASIC_AUTH_USERNAME"]
        password = config["BASIC_AUTH_PASSWORD"]

        credentials = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode(
            "utf-8"
        )

        response = client.get(
            "/admin/", headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 200
