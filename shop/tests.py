# d:/Projets/Projet_final test/cod_test/shop/tests.py
# Tests unitaires et d'intégration pour l'app 'shop'

import pytest
from datetime import date, timedelta
from django.contrib.auth import get_user_model

from shop.models import (
    CategorieEtablissement,
    CategorieProduit,
    Etablissement,
    Produit,
)


@pytest.mark.django_db
def test_produit_check_promotion_true():
    User = get_user_model()
    user = User.objects.create_user(username="shopuser", password="pwd")

    cat_etab = CategorieEtablissement.objects.create(
        nom="Cat", description="Desc",
    )
    cat_prod = CategorieProduit.objects.create(
        nom="ProdCat", description="Desc", categorie=cat_etab,
    )
    etab = Etablissement.objects.create(
        user=user,
        nom="Etab",
        description="Desc",
        logo="logo.png",
        couverture="cov.png",
        categorie=cat_etab,
        nom_du_responsable="Resp",
        prenoms_duresponsable="Pren",
        adresse="Addr",
        pays="Pays",
        contact_1="000000",
        email="contact@test.com",
    )
    produit = Produit.objects.create(
        nom="Produit",
        description="Desc",
        description_deal="Deal",
        prix=100.0,
        prix_promotionnel=80.0,
        categorie=cat_prod,
        etablissement=etab,
        date_debut_promo=date.today() - timedelta(days=1),
        date_fin_promo=date.today() + timedelta(days=1),
    )

    assert produit.check_promotion


@pytest.mark.django_db
def test_produit_check_promotion_false_outside_window():
    User = get_user_model()
    user = User.objects.create_user(username="shopuser2", password="pwd")

    cat_etab = CategorieEtablissement.objects.create(
        nom="Cat2", description="Desc",
    )
    cat_prod = CategorieProduit.objects.create(
        nom="ProdCat2", description="Desc", categorie=cat_etab,
    )
    etab = Etablissement.objects.create(
        user=user,
        nom="Etab2",
        description="Desc",
        logo="logo2.png",
        couverture="cov2.png",
        categorie=cat_etab,
        nom_du_responsable="Resp2",
        prenoms_duresponsable="Pren2",
        adresse="Addr2",
        pays="Pays2",
        contact_1="111111",
        email="contact2@test.com",
    )
    produit = Produit.objects.create(
        nom="Produit2",
        description="Desc",
        description_deal="Deal",
        prix=100.0,
        prix_promotionnel=80.0,
        categorie=cat_prod,
        etablissement=etab,
        date_debut_promo=date.today() + timedelta(days=5),
        date_fin_promo=date.today() + timedelta(days=7),
    )

    assert not produit.check_promotion
