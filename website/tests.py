# Tests unitaires et d'intégration pour l'app 'website'

import pytest

from website.models import SiteInfo


@pytest.mark.django_db
def test_siteinfo_str_uses_title():
    info = SiteInfo.objects.create(
        titre="Vectal",
        slogan="AI",
        description="desc",
        horaire_description="jour",
        text_pourquoi_nous_choisir="exp",
        logo="logo.png",
        icon="icon.png",
        arriere_plan_appreciation="bg.png",
        image_session_pourquoi_nous_choisir="img.png",
        image_page_contact="img2.png",
        image_pied_de_page="img3.png",
        couverture_page_contact="img4.png",
        couverture_page_panier="img5.png",
        couverture_page_paiement="img6.png",
        couverture_page_shop="img7.png",
        couverture_page_about="img8.png",
        contact_1="000",
        contact_2="111",
        email="info@test.com",
        adresse="addr",
        map_url="map",
        facebook_url="fb",
        instagram_url="insta",
        twitter_url="tw",
        whatsapp="wa",
    )

    assert str(info) == "Vectal"
