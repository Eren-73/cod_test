<!--
1. File: d:/Projets/Projet_final test/cod_test/README.md
2. This file tracks test automation work and usage notes for the project.
3. It exists so contributors understand the pytest configuration, available test cases, and how to rerun the suite.
4. RELEVANT FILES: pytest.ini, contact/tests.py, shop/tests.py, tests/functional/login_test.py
-->

# Suivi de la couverture des tests

- **Commande pour exécuter toute la suite :** `python -m pytest`
- Pytest recherche désormais tous les fichiers `tests.py` et `test_*` grâce à `pytest.ini`.
- Dernière exécution (14 déc. 2025) : 13 tests lancés sur les apps `base`, `client`, `contact`, `customer`, `shop`, `site_config`, `website` et tous réussis.

## Tests par application

| App | Tests clés | Type |
| --- | --- | --- |
| `base` | `test_base_app_config_found`, `test_graphql_hello_endpoint` | Unitaire + Intégration (AppConfig + GraphQL) |
| `client` | `test_qrcode_base64_returns_png` | Unitaire (utilitaire) |
| `contact` | `test_contact_str_returns_nom`, `test_get_contact_page`, `test_post_contact_success`, `test_post_newsletter_invalid_email`, `test_add_to_cart_endpoint`, `test_add_coupon_endpoint` | Unitaire + Intégration (vues JSON + API panier) |
| `customer` | `test_password_reset_token_validity`, `test_password_reset_token_expired`, `test_islogin_endpoint_authenticates`, `test_islogin_endpoint_rejects_invalid_credentials` | Unitaire + Intégration (modèle + API connexion) |
| `shop` | `test_produit_check_promotion_true`, `test_produit_check_promotion_false_outside_window` | Unitaire (logique de promotion) |
| `site_config` | `test_site_config_app_registered` | Unitaire (AppConfig) |
| `website` | `test_siteinfo_str_uses_title` | Unitaire (méthode `__str__`) |
| `base/tests/test_base.py` | `test_base_sanity` | Héritage placeholder |

## Remarques

- La couverture d’intégration cible les vues `contact` (page HTML et endpoints JSON), les APIs `add_to_cart`, `add_coupon`, `customer/post` et le point GraphQL de base.

## Rapport de couverture

- Pour générer un rapport de couverture :
	```sh
	python -m pytest --cov=.
	```
	Cela produit un résumé de couverture et un dossier `.coverage`. Ajoute `--cov-report=html` si tu veux un rendu HTML.
- On pourra ajouter des scénarios d’intégration supplémentaires pour les paiements une fois les services externes simulés.
- Quand tu ajoutes de nouveaux fichiers de test, veille à respecter la configuration de `pytest.ini` ou mets-la à jour.

## Tests fonctionnels Playwright

- Playwright lance les parcours UI clés. Assure-toi que `playwright` est déjà installé et que `chromium` a été téléchargé (`playwright install chromium`).
- Démarre un serveur Django actif : `python manage.py runserver`.
- Défini `PLAYWRIGHT_BASE_URL` si tu utilises un autre port ou domaine :
	```ps1
	$env:PLAYWRIGHT_BASE_URL = "http://localhost:8000"
	```
- Tu peux forcer l’ouverture du navigateur en définissant `PLAYWRIGHT_HEADLESS=false` (par défaut `false`, mets `true` pour exécuter en headless).
- Pour voir les étapes en temps réel, Playwright applique maintenant par défaut `PLAYWRIGHT_SLOW_MO=1500` (1,5 s entre chaque action). Tu peux réduire le délai en positionnant un autre millisecondage, par exemple `set PLAYWRIGHT_SLOW_MO=400`.
- Exécute la suite fonctionnelle :
	```sh
	python -m pytest tests/functional
	```
- Playwright couvre aussi le parcours de découverte :
	```sh
	python -m pytest tests/functional/site_tour_test.py
	```
- Pour valider les pages marketing (Accueil, Deals, À propos, Contact) et leurs scrolls, lance :
	```sh
	python -m pytest tests/functional/page_sweep_test.py
	```
- Ce test clique explicitement sur les liens de navigation (Accueil / Deal / À propos / Contact) et scrolle doucement pour que tu voies la transition complète.
- Une fois le tour terminé, il poursuit directement sur la page de connexion et effectue un login avec les identifiants `eren73` / `eren12345`, donc tu vois la transition explorer → authentification en une seule passe.
- Pour simuler la visite de la boutique apres connexion, incluant liste et detail d un produit :
	```sh
	python -m pytest tests/functional/product_explore_test.py
	```
- Ce test se connecte avec `eren73` / `eren12345`, ouvre la page /shop/, verifie la presence d un produit puis consulte sa page de detail.
- Le fichier `tests/functional/login_test.py` vérifie :
	1. la page de connexion se charge,
	2. la navigation vers la réinitialisation de mot de passe,
	3. une connexion complète avec les identifiants `eren73` / `eren12345` après avoir parcouru la page d’accueil et scrollé pour découvrir le site.
- Le scénario `tests/functional/login_test.py` vérifie que la page de connexion s’affiche et que la navigation vers la réinitialisation de mot de passe fonctionne.
