# d:/Projets/Projet_final test/cod_test/customer/tests.py
# Tests unitaires et d'intégration pour l'app 'customer'

import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from customer.models import PasswordResetToken


@pytest.mark.django_db
def test_password_reset_token_validity():
    User = get_user_model()
    user = User.objects.create_user(username="test", password="pwd")
    token = PasswordResetToken.objects.create(user=user, token="abc123")

    assert token.is_valid()


@pytest.mark.django_db
def test_password_reset_token_expired():
    User = get_user_model()
    user = User.objects.create_user(username="test2", password="pwd")
    token = PasswordResetToken.objects.create(user=user, token="def456")
    token.created_at = timezone.now() - timezone.timedelta(hours=2)
    token.save(update_fields=["created_at"])

    assert not token.is_valid()


@pytest.mark.django_db
def test_islogin_endpoint_authenticates(client):
    User = get_user_model()
    user = User.objects.create_user(username="loginuser", email="login@example.com", password="secret")

    payload = {
        "username": "loginuser",
        "password": "secret",
    }
    response = client.post(
        reverse('post'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@pytest.mark.django_db
def test_islogin_endpoint_rejects_invalid_credentials(client):
    payload = {
        "username": "unknown",
        "password": "wrong",
    }
    response = client.post(
        reverse('post'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False
