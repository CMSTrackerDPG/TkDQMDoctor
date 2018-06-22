import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.fixture
def client_with_user_logged_in(client, django_user_model):
    """
    returns a client where a User is already loged in
    """
    username = "example"
    password = "VerySecurePasswort"
    user = django_user_model.objects.create(username=username)
    user.set_password(password)
    user.save()
    assert client.login(username="example", password="VerySecurePasswort")
    return client


@pytest.fixture
def client_with_staff_logged_in(client, django_user_model):
    """
    returns a client where a User is already loged in
    """
    username = "example"
    password = "VerySecurePasswort"
    user = django_user_model.objects.create(username=username, is_staff=True)
    user.set_password(password)
    user.save()
    assert client.login(username="example", password="VerySecurePasswort")
    return client


@pytest.fixture
def client_with_superuser_logged_in(client, django_user_model):
    """
    returns a client where a User is already loged in
    """
    username = "example"
    password = "VerySecurePasswort"
    django_user_model.objects.create_superuser(username=username, password=password, email="")
    assert client.login(username="example", password="VerySecurePasswort")
    return client


class TestIndexPage:
    def test_anonymous(self, client):
        response = client.get(reverse("certhelper:list"))
        assert "List of certified runs" in response.content.decode()
        assert "Login" in response.content.decode()
        assert "Add Run" not in response.content.decode()
        assert "Admin Settings" not in response.content.decode()
        assert response.status_code == 200

    def test_logged_in(self, client_with_user_logged_in):
        client = client_with_user_logged_in
        response = client.get(reverse("certhelper:list"))
        assert "List of certified runs" in response.content.decode()
        assert "Login" not in response.content.decode()
        assert "Add Run" in response.content.decode()
        assert "Admin Settings" not in response.content.decode()
        assert response.status_code == 200

    def test_staffuser(self, client_with_staff_logged_in):
        client = client_with_staff_logged_in
        response = client.get(reverse("certhelper:list"))
        assert "List of certified runs" in response.content.decode()
        assert "Login" not in response.content.decode()
        assert "Add Run" in response.content.decode()
        assert "Admin Settings" in response.content.decode()
        assert response.status_code == 200

    def test_superuser(self, client_with_superuser_logged_in):
        client = client_with_superuser_logged_in
        response = client.get(reverse("certhelper:list"))
        assert "List of certified runs" in response.content.decode()
        assert "Login" not in response.content.decode()
        assert "Add Run" in response.content.decode()
        assert "Admin Settings" in response.content.decode()
        assert response.status_code == 200


class TestCreatePage:
    def test_anonymous(self, client):
        response = client.get(reverse("certhelper:create"))
        assert response.status_code == 302
        assert "login" in response.url

    def test_logged_in(self, client_with_user_logged_in):
        client = client_with_user_logged_in
        response = client.get(reverse("certhelper:create"))
        assert response.status_code == 200

    def test_staffuser(self, client_with_staff_logged_in):
        client = client_with_staff_logged_in
        response = client.get(reverse("certhelper:create"))
        assert response.status_code == 200

    def test_superuser(self, client_with_superuser_logged_in):
        client = client_with_superuser_logged_in
        response = client.get(reverse("certhelper:create"))
        assert response.status_code == 200
