# Tests unitaires et d'intégration pour l'app 'contact'

import json

import pytest
from django.urls import reverse

from contact.models import Contact
from shop.models import (
    CategorieEtablissement,
    CategorieProduit,
    Etablissement,
    Produit,
)

from customer.models import Panier, CodePromotionnel
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_contact_str_returns_nom():
    contact = Contact.objects.create(
        nom="Ali",
        sujet="Bug",
        email="ali@test.com",
        message="Test",
    )

    assert str(contact) == "Ali"


@pytest.mark.django_db
def test_get_contact_page(client):
    response = client.get(reverse('contact'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_contact_success(client):
    payload = {
        'nom': 'Jean',
        'email': 'jean@test.com',
        'sujet': 'Test',
        'messages': 'Bonjour',
    }
    response = client.post(
        reverse('post_contact'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True


@pytest.mark.django_db
def test_post_newsletter_invalid_email(client):
    payload = {'email': 'bad'}
    response = client.post(
        reverse('post_newsletter'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is False


def _create_test_product():
    User = get_user_model()
    user = User.objects.create_user(username="produser", password="pwd")
    cat_etab = CategorieEtablissement.objects.create(nom="cat", description="desc")
    cat_prod = CategorieProduit.objects.create(
        nom="cprod",
        description="desc",
        categorie=cat_etab,
    )
    etab = Etablissement.objects.create(
        user=user,
        nom="Etab",
        description="desc",
        logo="logo.png",
        couverture="cov.png",
        categorie=cat_etab,
        nom_du_responsable="Resp",
        prenoms_duresponsable="Pren",
        adresse="addr",
        pays="Pays",
        contact_1="000000",
        email="contact@test.com",
    )
    produit = Produit.objects.create(
        nom="Produit",
        description="desc",
        description_deal="deal",
        prix=50.0,
        prix_promotionnel=40.0,
        categorie=cat_prod,
        etablissement=etab,
    )
    return produit


@pytest.mark.django_db
def test_add_to_cart_endpoint(client):
    produit = _create_test_product()
    panier = Panier.objects.create()
    payload = {'panier': panier.id, 'produit': produit.id, 'quantite': 3}
    response = client.post(
        reverse('add_to_cart'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert panier.produit_panier.count() == 1


@pytest.mark.django_db
def test_add_coupon_endpoint(client):
    produit = _create_test_product()
    panier = Panier.objects.create()
    coupon = CodePromotionnel.objects.create(
        libelle="Promo",
        etat=True,
        date_fin="2099-01-01",
        reduction=0.1,
        code_promo="PROMO10",
        nombre_u=1,
    )
    payload = {'panier': panier.id, 'coupon': coupon.code_promo}
    response = client.post(
        reverse('add_coupon'),
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    panier.refresh_from_db()
    assert panier.coupon == coupon
