# Guide d'Exécution des Tests

Ce document explique comment lancer les différents types de tests dans le projet.

---

## Prérequis

### 1. Environnement Python
```powershell
# Activer l'environnement virtuel
& "D:/Projets/Projet_final test/cod_test/env/Scripts/Activate.ps1"
```

### 2. Vérifier les dépendances
```powershell
pip list | findstr playwright
pip list | findstr pytest
pip list | findstr django
```

### 3. Lancer le serveur Django (dans un terminal séparé)
```powershell
python manage.py runserver
```

---

## Lancer les Tests

### Tests Fonctionnels (Playwright)

#### Mode Normal (Sans visualisation)
```powershell
# Tous les tests fonctionnels
pytest tests/functional/ -v

# Un test spécifique
pytest tests/functional/cart_full_scenario_test.py::test_full_cart_scenario -v
```

#### Mode Visuel (Avec navigateur visible)
```powershell
# Configuration pour mode visuel
$env:PLAYWRIGHT_HEADLESS="false"
$env:PLAYWRIGHT_SLOW_MO="2500"

# Lancer le test
pytest tests/functional/cart_full_scenario_test.py::test_full_cart_scenario -v -s
```

#### Tests Disponibles
```powershell
# Test complet end-to-end (16 étapes)
pytest tests/functional/cart_full_scenario_test.py -v -s

# Test navigation panier via hover
pytest tests/functional/cart_navigation_test.py -v -s

# Test connexion utilisateur
pytest tests/functional/login_test.py -v -s

# Test exploration produits
pytest tests/functional/product_explore_test.py -v -s

# Test opérations panier (avec problèmes Vue.js connus)
pytest tests/functional/cart_test.py -v -s
```

---

## Tests par Type

### Tests Unitaires
```powershell
# Lancer tous les tests unitaires
pytest tests/unit/ -v

# Avec couverture de code
pytest tests/unit/ --cov=. --cov-report=html
```

### Tests d'Intégration
```powershell
# Tests d'API et intégration entre modules
pytest tests/integration/ -v
```

### Tests Fonctionnels (UI)
```powershell
# Tests end-to-end avec Playwright
pytest tests/functional/ -v -s
```

---

## Options Utiles

### Verbosité et Output
```powershell
# Mode verbose avec output détaillé
pytest -v -s

# Mode très verbose (affiche les noms de tests)
pytest -vv

# Afficher seulement les résumés
pytest -q
```

### Filtrage des Tests
```powershell
# Par nom de test
pytest -k "cart" -v

# Par marker
pytest -m "slow" -v

# Exclure certains tests
pytest -k "not cart_test" -v
```

### Gestion des Échecs
```powershell
# Arrêter au premier échec
pytest -x

# Arrêter après N échecs
pytest --maxfail=3

# Relancer seulement les tests échoués
pytest --lf
```

### Performance
```powershell
# Afficher les tests les plus lents
pytest --durations=10

# Mode parallèle (nécessite pytest-xdist)
pytest -n auto
```

---

## Configurations Spéciales

### Mode Démo/Présentation
```powershell
# Configuration optimale pour démonstration
$env:PLAYWRIGHT_HEADLESS="false"
$env:PLAYWRIGHT_SLOW_MO="2500"
pytest tests/functional/cart_full_scenario_test.py::test_full_cart_scenario -v -s
```

### Mode CI/CD
```powershell
# Configuration pour intégration continue
$env:PLAYWRIGHT_HEADLESS="true"
pytest tests/functional/ -v --maxfail=1
```

### Mode Debug
```powershell
# Avec debugger
pytest --pdb

# Avec traces
pytest --trace
```

---

## Résultats et Rapports

### Générer un Rapport HTML
```powershell
pytest tests/functional/ --html=report.html --self-contained-html
```

### Couverture de Code
```powershell
# Génerer rapport de couverture
pytest --cov=. --cov-report=html --cov-report=term

# Ouvrir le rapport
start htmlcov/index.html
```

---

## Résolution de Problèmes

### Le serveur localhost n'est pas démarré
```powershell
# Vérifier si le serveur tourne
curl http://localhost:8000

# Démarrer le serveur dans un autre terminal
python manage.py runserver
```

### Base de données de test
```powershell
# Recréer la base de données de test
python manage.py test --keepdb=false
```

### Problèmes Playwright
```powershell
# Réinstaller les navigateurs
playwright install chromium

# Vérifier l'installation
playwright --version
```

### Timeout des tests
```powershell
# Augmenter le timeout global
pytest --timeout=300
```

---

## Tests Spécifiques par Fonctionnalité

### Authentification
```powershell
pytest tests/functional/login_test.py -v
```

### Panier
```powershell
# Navigation et visualisation
pytest tests/functional/cart_navigation_test.py -v

# Opérations complètes
pytest tests/functional/cart_test.py -v
```

### Checkout et Paiement
```powershell
pytest tests/functional/cart_full_scenario_test.py -v -k "paiement"
```

### Profil Utilisateur
```powershell
pytest tests/functional/cart_full_scenario_test.py -v -k "profil"
```

---

## Récapitulatif des Commandes Essentielles

```powershell
# 1. Activer l'environnement
& "D:/Projets/Projet_final test/cod_test/env/Scripts/Activate.ps1"

# 2. Démarrer Django (terminal séparé)
python manage.py runserver

# 3. Lancer le test complet avec visualisation
$env:PLAYWRIGHT_HEADLESS="false"; $env:PLAYWRIGHT_SLOW_MO="2500"
pytest tests/functional/cart_full_scenario_test.py::test_full_cart_scenario -v -s

# 4. Lancer tous les tests (mode CI)
pytest tests/ -v --maxfail=1
```

---

## Métriques de Performance

| Test | Temps Moyen | Statut |
|---|---|---|
| test_full_cart_scenario | ~4 min | ✅ |
| test_access_cart_via_hover_menu | ~30 sec | ✅ |
| test_login | ~15 sec | ✅ |
| test_product_explore | ~45 sec | ✅ |

---

**Date** : Février 2026  
**Dernière mise à jour** : 03/02/2026
