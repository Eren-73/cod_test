from django.apps import apps

# Tests unitaires et d'intégration pour l'app 'site_config'

def test_site_config_app_registered():
    config = apps.get_app_config('site_config')
    assert config.name == 'site_config'
