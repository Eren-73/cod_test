# Pourquoi prioriser les tests ?

- **Tests critiques en premier** : Ceux qui impactent la sécurité et la stabilité.
- **Tests des fonctionnalités principales avant les secondaires.**

---

## Méthode de priorisation : Matrice de risque

| Fonctionnalité | Probabilité d'échec | Impact | Priorité |
|---|---|---|---|
| Connexion utilisateur | Élevée | Critique | Haute |
| Paiement en ligne | Moyenne | Très critique | Haute |
| Ajout au panier | Moyenne | Critique | Haute |
| Navigation profil | Faible | Moyen | Moyenne |
| Page de contact | Faible | Mineur | Moyenne |

---

## Tests Dynamiques (avec exécution du code)

| Type de test | Objectif | Exemple |
|---|---|---|
| **Tests unitaires** | Vérifier les fonctions individuellement. | pytest, unittest |
| **Tests d'intégration** | Tester l'interaction entre plusieurs modules. | API tests avec requests |
| **Tests fonctionnels** | Vérifier le comportement global du logiciel. | Playwright pour UI testing |

---

## Test Cases Implémentés (Playwright)

### Exemple de tableau de test

| ID | Cas de test | Entrées | Résultat attendu | Statut |
|---|---|---|---|---|
| TC01 | Vérifier la connexion utilisateur | username: test, password: test123 | Redirection vers /deals/ | ✅ |
| TC02 | Vérifier l'ajout d'un produit au panier | Produit: Massage Premium, Quantité: 1 | Produit ajouté au panier | ✅ |
| TC03 | Vérifier la navigation vers le panier via hover | Hover sur icône panier, Clic "Voir panier" | Navigation vers /deals/cart | ✅ |
| TC04 | Vérifier le processus de paiement | Panier avec 2 produits | Paiement réussi, redirection vers /success | ✅ |
| TC05 | Vérifier l'exploration du profil | Navigation via dropdown, Scroll sur pages | Toutes les sections accessibles | ✅ |

### Détails du Test Principal

**test_full_cart_scenario** - 16 étapes :
1. Connexion avec compte test
2. Navigation vers /deals/
3. Sélection du premier produit
4. Ajout au panier (Produit 1)
5. Sélection du deuxième produit
6. Ajout au panier (Produit 2)
7. Navigation vers le panier via hover
8. Vérification du contenu du panier
9. Scroll lent vers le bas
10. Clic sur "Procéder au paiement"
11. Observation page de paiement
12. Scroll sur la page de paiement
13. Clic sur "Payer"
14. Observation page de succès
15. Téléchargement de la facture
16. Exploration complète du profil (Mes Commandes, Liste de Souhaits, Paramètres)

**Temps d'exécution** : ~4 minutes  
**Statut** : ✅ Tous les tests passent

---

**Date** : Février 2026
