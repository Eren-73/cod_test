# d:/Projets/Projet_final test/cod_test/client/tests.py
# Tests unitaires et d'intégration pour l'app 'client'

import base64

from client.utils import qrcode_base64


def test_qrcode_base64_returns_png():
    data = "client://123"
    encoded = qrcode_base64(data)
    decoded = base64.b64decode(encoded)
    assert decoded.startswith(b"\x89PNG")
