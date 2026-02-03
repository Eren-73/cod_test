from django.apps import apps

import pytest

from django.urls import reverse

from graphene_django.settings import graphene_settings

# Tests unitaires et d'intégration pour l'app 'base'

def test_base_app_config_found():
    app_config = apps.get_app_config('base')
    assert app_config.name == 'base'


def test_graphql_hello_endpoint(client):
    query = '{ hello }'
    response = client.post(
        reverse('graphql'),
        data={'query': query},
        content_type='application/json'
    )

    data = response.json()
    assert response.status_code == 200
    assert data['data']['hello'] == 'Salut depuis GraphQL'
