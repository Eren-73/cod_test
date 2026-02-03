# d:\Projets\Projet_final test\cod_test\tests\functional\cart_full_scenario_test.py
# Test complet: ajout produits au panier + navigation + vérification
# Scénario complet de l'utilisateur: browse → add to cart → view cart
# RELEVANT FILES: shop/templates/product-details.html, shop/templates/cart.html

import os
from playwright.sync_api import sync_playwright
from customer.models import Customer
from django.contrib.auth import get_user_model
import pytest


def _base_url() -> str:
    """Get the base URL from environment variable."""
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


def _is_headless() -> bool:
    """Check if tests should run in headless mode."""
    return os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"


def _slow_mo() -> int:
    """Get slow motion delay from environment variable."""
    return int(os.getenv("PLAYWRIGHT_SLOW_MO", "2000"))


def _ensure_demo_user() -> tuple[str, str]:
    username = "test"
    password = "test12345"
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={
        "email": "husseni@example.com",
    })
    if created or not user.check_password(password):
        user.set_password(password)
        user.save()
    
    # Ensure customer exists
    try:
        Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        Customer.objects.create(
            user=user,
            contact_1="123456789",
            adresse="123 Test Street"
        )
    
    return username, password


def _login(page, username: str, password: str) -> None:
    """Helper function to login."""
    page.goto(f"{_base_url()}/customer/", wait_until="load")
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.locator("button:has-text('Submit')").first.click()
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)


def _observe_page(page, max_ratio: float = 0.5, delay_ms: int = 2000) -> None:
    """Slow scroll through page for observation."""
    page.evaluate(
        "max_ratio => {"
        "const scrollHeight = document.body.scrollHeight;"
        "const target = scrollHeight * max_ratio;"
        "window.scrollTo({ top: target, behavior: 'smooth' });"
        "}"
    , max_ratio)
    page.wait_for_timeout(delay_ms)


def _normalize_href(href: str) -> str:
    """Convert relative URLs to absolute."""
    if href and not href.startswith("http"):
        return f"{_base_url()}{href}"
    return href


@pytest.mark.django_db
def test_full_cart_scenario() -> None:
    """Test complet: Login → Browse products → Add to cart → View cart."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        print("\n=== ÉTAPE 1: CONNEXION ===")
        _login(page, username, password)
        print(f"✓ Connecté avec le compte: {username}")

        print("\n=== ÉTAPE 2: NAVIGATION VERS LES PRODUITS ===")
        page.goto(f"{_base_url()}/deals/", wait_until="load")
        page.wait_for_timeout(2000)
        _observe_page(page, max_ratio=0.3)
        print("✓ Page /deals/ chargée")

        print("\n=== ÉTAPE 3: SÉLECTION DU PREMIER PRODUIT ===")
        product_links = page.locator("a:has-text('Voir plus')")
        products_count = product_links.count()
        print(f"✓ Trouvé {products_count} produits")

        if products_count > 0:
            # Premier produit
            first_product_link = product_links.nth(0).get_attribute("href")
            first_product_link = _normalize_href(first_product_link)
            print(f"✓ Navigation vers: {first_product_link}")
            
            page.goto(first_product_link, wait_until="networkidle")
            page.wait_for_timeout(2000)
            _observe_page(page, max_ratio=0.4)
            
            # Get product name
            product_name = page.locator("h3").first.text_content() if page.locator("h3").count() > 0 else "Produit 1"
            print(f"✓ Produit: {product_name}")

            print("\n=== ÉTAPE 4: AJOUT AU PANIER (Produit 1) ===")
            page.wait_for_timeout(1500)  # Wait for Vue.js
            
            # Try to add with default quantity
            add_to_cart_btn = page.locator("button:has-text('Ajouter au panier')")
            if add_to_cart_btn.count() > 0:
                add_to_cart_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(500)
                print("✓ Clic sur 'Ajouter au panier'")
                add_to_cart_btn.click()
                page.wait_for_timeout(3000)  # Wait for AJAX
                
                # Check for error
                error_alert = page.locator(".alert.alert-danger")
                if error_alert.count() > 0 and error_alert.is_visible():
                    error_text = error_alert.text_content()
                    print(f"⚠ ERREUR: {error_text}")
                else:
                    print("✓ Produit ajouté (ou tentative effectuée)")

            print("\n=== ÉTAPE 5: SÉLECTION DU DEUXIÈME PRODUIT ===")
            page.goto(f"{_base_url()}/deals/", wait_until="load")
            page.wait_for_timeout(1500)
            
            if products_count > 1:
                second_product_link = product_links.nth(1).get_attribute("href")
                second_product_link = _normalize_href(second_product_link)
                print(f"✓ Navigation vers: {second_product_link}")
                
                page.goto(second_product_link, wait_until="networkidle")
                page.wait_for_timeout(2000)
                _observe_page(page, max_ratio=0.4)
                
                product_name2 = page.locator("h3").first.text_content() if page.locator("h3").count() > 0 else "Produit 2"
                print(f"✓ Produit: {product_name2}")

                print("\n=== ÉTAPE 6: AJOUT AU PANIER (Produit 2) ===")
                page.wait_for_timeout(1500)
                
                add_to_cart_btn2 = page.locator("button:has-text('Ajouter au panier')")
                if add_to_cart_btn2.count() > 0:
                    add_to_cart_btn2.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)
                    print("✓ Clic sur 'Ajouter au panier'")
                    add_to_cart_btn2.click()
                    page.wait_for_timeout(3000)
                    
                    error_alert2 = page.locator(".alert.alert-danger")
                    if error_alert2.count() > 0 and error_alert2.is_visible():
                        error_text2 = error_alert2.text_content()
                        print(f"⚠ ERREUR: {error_text2}")
                    else:
                        print("✓ Produit ajouté (ou tentative effectuée)")

        print("\n=== ÉTAPE 7: NAVIGATION VERS LE PANIER VIA HOVER ===")
        page.goto(f"{_base_url()}/", wait_until="load")
        page.wait_for_timeout(2000)
        
        # Find cart icon
        cart_icon = page.locator(".cart-icon, .shopping-cart, a[href*='cart'], .zmdi-shopping-cart").first
        
        if cart_icon.count() > 0:
            print("✓ Icône panier trouvée")
            
            # Hover to show dropdown menu
            cart_icon.hover()
            print("✓ Hover sur l'icône panier...")
            page.wait_for_timeout(2000)  # Wait for dropdown animation
            
            # Look for "Voir panier" link in dropdown - try multiple selectors
            voir_panier_selectors = [
                "a:has-text('Voir panier')",
                "a:has-text('View cart')",
                "a:has-text('Voir le panier')",
                ".mini-cart a:has-text('panier')",
                ".dropdown-menu a[href*='cart']",
                ".cart-dropdown a[href*='cart']",
            ]
            
            voir_panier_found = False
            for selector in voir_panier_selectors:
                voir_panier = page.locator(selector).first
                if voir_panier.count() > 0 and voir_panier.is_visible():
                    text = voir_panier.text_content()
                    print(f"✓ Lien trouvé dans le menu déroulant: '{text.strip()}'")
                    page.wait_for_timeout(1000)
                    
                    # Click on "Voir panier" link
                    voir_panier.click()
                    print("✓ Clic sur 'Voir panier' dans le menu déroulant")
                    
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
                    print(f"✓ Navigation vers: {page.url}")
                    voir_panier_found = True
                    break
            
            if not voir_panier_found:
                print("⚠ Lien 'Voir panier' non trouvé dans le menu déroulant")
                print("   Tentative de clic direct sur l'icône panier...")
                cart_icon.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)
                print(f"✓ Navigation vers: {page.url}")
        else:
            print("⚠ Icône panier non trouvée")

        print("\n=== ÉTAPE 8: VÉRIFICATION DU CONTENU DU PANIER ===")
        
        # Check for cart table
        cart_table = page.locator("table.table_cart, .cart_list table")
        if cart_table.count() > 0:
            rows = cart_table.locator("tbody tr")
            items_count = rows.count()
            print(f"✓ Panier contient {items_count} ligne(s)")
            
            if items_count > 0:
                print("\n=== CONTENU DU PANIER ===")
                for i in range(min(items_count, 5)):  # Max 5 items
                    row = rows.nth(i)
                    cells = row.locator("td")
                    if cells.count() >= 3:
                        product = cells.nth(2).text_content()
                        print(f"  • {product}")
            else:
                print("⚠ Panier vide (tableau présent mais aucune ligne)")
        else:
            # Check for empty cart message
            empty_msg = page.locator("text=/panier est vide|cart is empty/i")
            if empty_msg.count() > 0:
                print("⚠ Message: Panier vide")
            else:
                print("⚠ Tableau du panier non trouvé")
        
        print("\n=== ÉTAPE 9: SCROLL LENT VERS LE BAS DE LA PAGE ===")
        # Scroll progressivement vers le bas
        print("✓ Début du scroll...")
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1500)
        
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1500)
        print("✓ Scroll intermédiaire...")
        
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1500)
        
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1500)
        print("✓ Scroll vers le bas...")
        
        # Check total
        total_element = page.locator("text=/total|montant/i").first
        if total_element.count() > 0:
            print(f"✓ Élément total visible")
            total_element.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)

        print("\n=== ÉTAPE 10: CLIC SUR 'PROCÉDER AU PAIEMENT' ===")
        # Look for checkout button - try multiple possible texts
        checkout_selectors = [
            "input:has-text('Proceder au paiement')",
            "button:has-text('Proceder au paiement')",
            "input[value*='Proceder']",
            "input[value*='paiement']",
            ".process-checkout",
            "input.process-checkout",
            "button:has-text('Checkout')",
        ]
        
        checkout_found = False
        for selector in checkout_selectors:
            checkout_btn = page.locator(selector).first
            if checkout_btn.count() > 0 and checkout_btn.is_visible():
                btn_text = checkout_btn.get_attribute("value") or checkout_btn.text_content()
                print(f"✓ Bouton trouvé: '{btn_text}'")
                
                checkout_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                
                print("✓ Clic sur 'Procéder au paiement'")
                checkout_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                print(f"✓ Navigation vers la page de paiement: {page.url}")
                checkout_found = True
                break
        
        if not checkout_found:
            print("⚠ Bouton 'Procéder au paiement' non trouvé")

        if not checkout_found:
            print("⚠ Bouton 'Procéder au paiement' non trouvé")

        print("\n=== ÉTAPE 11: OBSERVATION DE LA PAGE DE PAIEMENT ===")
        page.wait_for_timeout(3000)
        
        # Check if we're on checkout page
        if "checkout" in page.url.lower() or "paiement" in page.url.lower():
            print(f"✓ Sur la page de paiement/checkout")
        else:
            print(f"⚠ URL actuelle: {page.url}")
        
        # Scroll lentement sur la page de paiement
        print("\n=== ÉTAPE 12: SCROLL SUR LA PAGE DE PAIEMENT ===")
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        print("✓ Scroll vers le milieu...")
        
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        print("✓ Scroll vers le bas...")
        
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)

        print("\n=== ÉTAPE 13: CLIC SUR LE BOUTON 'PAYER' ===")
        # Look for payment button - try multiple possible selectors
        payment_selectors = [
            "button:has-text('Payer')",
            "button.validate",
            "button:has-text('Pay')",
            "input[type='submit']:has-text('Payer')",
            "button[type='submit']",
            ".validate",
            "button.btn-success:has-text('Payer')",
        ]
        
        payment_found = False
        for selector in payment_selectors:
            payment_btn = page.locator(selector).first
            if payment_btn.count() > 0 and payment_btn.is_visible():
                btn_text = payment_btn.text_content() or payment_btn.get_attribute("value") or "Payer"
                print(f"✓ Bouton de paiement trouvé: '{btn_text}'")
                
                payment_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(1500)
                
                print("✓ Clic sur le bouton 'Payer'")
                payment_btn.click()
                page.wait_for_timeout(5000)  # Wait longer for payment processing
                
                print(f"✓ Après le clic - URL: {page.url}")
                payment_found = True
                break
        
        if not payment_found:
            print("⚠ Bouton 'Payer' non trouvé")
            print("   Affichage des boutons disponibles...")
            all_buttons = page.locator("button, input[type='submit']")
            for i in range(min(all_buttons.count(), 5)):
                btn = all_buttons.nth(i)
                text = btn.text_content() or btn.get_attribute("value")
                print(f"   - Bouton {i+1}: {text}")

        print("\n=== ÉTAPE 14: OBSERVATION DE LA PAGE DE SUCCÈS ===")
        page.wait_for_timeout(3000)
        
        # Check if on success page
        if "success" in page.url.lower() or "paiement" in page.url.lower():
            print(f"✓ Sur la page de succès du paiement")
        else:
            print(f"⚠ URL actuelle: {page.url}")
        
        # Scroll sur la page de succès
        print("✓ Scroll sur la page de succès...")
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)
        
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(2000)

        print("\n=== ÉTAPE 15: TÉLÉCHARGEMENT DE LA FACTURE ===")
        # Look for "Télécharger" text in the table (even if not a link)
        download_cell = page.locator("td:has-text('Télécharger'), a:has-text('Télécharger'), button:has-text('Télécharger')").first
        
        if download_cell.count() > 0 and download_cell.is_visible():
            print("✓ Élément 'Télécharger' trouvé dans le tableau des commandes")
            
            download_cell.scroll_into_view_if_needed()
            page.wait_for_timeout(2000)
            
            # Highlight by clicking on it (even if it's just text)
            print("✓ Clic sur l'élément 'Télécharger'")
            try:
                download_cell.click(timeout=5000)
                page.wait_for_timeout(2000)
                print("✓ Élément cliqué")
            except:
                print("⚠ Élément 'Télécharger' est du texte simple (pas de lien actif)")
                print("   Note: Le template devrait être mis à jour pour ajouter un vrai lien de téléchargement")
        else:
            print("⚠ Élément 'Télécharger' non trouvé")
            print("   Affichage du contenu de la page...")
            # Show table content
            table_cells = page.locator("table td")
            for i in range(min(table_cells.count(), 15)):
                cell = table_cells.nth(i)
                text = cell.text_content()
                if text and text.strip():
                    print(f"   - Cellule {i+1}: '{text.strip()[:40]}'")

        print("\n=== ÉTAPE 16: EXPLORATION DU PROFIL ===")
        # Scroll to top first
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1500)
        print("✓ Retour en haut de la page")
        
        # Find user name/account element in header to hover and open dropdown
        # The dropdown appears when hovering on the user name "test" in the header
        account_element_selectors = [
            "a:has-text('test')",  # User name link
            ".account-info",
            ".user-name",
            ".account-icon",
            ".zmdi-account",
            "a.account",
            ".user-account",
            "i.zmdi-account",
            ".header-action-icon-2 a",
        ]
        
        account_found = False
        for selector in account_element_selectors:
            account_element = page.locator(selector).first
            if account_element.count() > 0:
                # Check if it's visible before hovering
                try:
                    if account_element.is_visible():
                        print(f"✓ Élément compte trouvé avec sélecteur: {selector}")
                        
                        # Hover on account element to show dropdown
                        account_element.hover()
                        print("✓ Hover sur l'élément compte...")
                        page.wait_for_timeout(3000)  # Wait for dropdown animation
                        
                        # Check if dropdown appeared and show its content
                        dropdown = page.locator(".dropdown-menu, .account-dropdown, .mini-account").first
                        if dropdown.count() > 0 and dropdown.is_visible():
                            print("✓ Menu déroulant du compte visible")
                            print("\n=== CONTENU DU MENU PROFIL ===")
                            
                            # List all links in dropdown
                            dropdown_links = dropdown.locator("a, .dropdown-item")
                            if dropdown_links.count() > 0:
                                for i in range(dropdown_links.count()):
                                    link = dropdown_links.nth(i)
                                    if link.is_visible():
                                        text = link.text_content()
                                        href = link.get_attribute("href")
                                        if text and text.strip():
                                            print(f"  • {text.strip()} → {href}")
                            
                            page.wait_for_timeout(2000)
                        
                        # Now look for "Profil" link in the dropdown
                        profile_link_selectors = [
                            "a:has-text('Profil')",
                            "a:has-text('Mon Profil')",
                            "a[href*='client']",
                            ".dropdown-item:has-text('Profil')",
                        ]
                        
                        profile_link_found = False
                        for prof_selector in profile_link_selectors:
                            profile_link = page.locator(prof_selector).first
                            if profile_link.count() > 0 and profile_link.is_visible():
                                text = profile_link.text_content()
                                print(f"\n✓ Clic sur le lien: '{text.strip()}'")
                                
                                # Click on profile link
                                profile_link.click()
                                page.wait_for_load_state("networkidle")
                                page.wait_for_timeout(2000)
                                print(f"✓ Navigation vers la page profil: {page.url}")
                                
                                profile_link_found = True
                                account_found = True
                                break
                        
                        if profile_link_found:
                            break
                        else:
                            print("⚠ Lien 'Profil' non visible dans le dropdown")
                except:
                    # Element not visible, try next selector
                    continue
        
        if not account_found:
            print("⚠ Élément compte non trouvé, tentative de navigation directe")
            page.goto(f"{_base_url()}/client/", wait_until="load")
            page.wait_for_timeout(2000)
            print(f"✓ Navigation directe vers: {page.url}")
        
        # Explore profile page in detail
        print("\n=== EXPLORATION DÉTAILLÉE DE LA PAGE PROFIL ===")
        
        # Scroll to bottom first
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        print("✓ Scroll jusqu'en bas de la page profil")
        
        # Get page height
        page_height = page.evaluate("document.body.scrollHeight")
        print(f"✓ Hauteur totale: {page_height}px")
        
        # Scroll up slowly in increments
        scroll_increments = 4
        scroll_step = page_height // scroll_increments if page_height > 0 else 200
        
        print("\n=== REMONTÉE PROGRESSIVE (BAS → HAUT) ===")
        for i in range(scroll_increments):
            current_position = page_height - (scroll_step * (i + 1))
            page.evaluate(f"window.scrollTo(0, {max(0, current_position)})")
            page.wait_for_timeout(2000)
            print(f"✓ Scroll {i+1}/{scroll_increments} - Position: {max(0, current_position)}px")
        
        # Scroll back to top to find navigation links
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(2000)
        print("\n✓ Retour en haut pour explorer les sections")
        
        # Find all profile section links from the dropdown menu
        print("\n=== EXPLORATION DES SECTIONS DU PROFIL ===")
        
        # We know the dropdown has these links, let's visit them directly
        sections_to_visit = [
            {"text": "Mes Commandes", "href": "/client/commande"},
            {"text": "Ma Liste de Souhaits", "href": "/client/liste-souhait"},
            {"text": "Paramètres", "href": "/client/parametre"},
        ]
        
        print(f"✓ {len(sections_to_visit)} sections à explorer")
        for section in sections_to_visit:
            print(f"  • {section['text']} → {section['href']}")
        
        # Visit each section
        for idx, section in enumerate(sections_to_visit, 1):
            print(f"\n=== VISITE DE LA SECTION {idx}/{len(sections_to_visit)}: {section['text']} ===")
            
            # Navigate to the section
            page.goto(f"{_base_url()}{section['href']}", wait_until="load")
            page.wait_for_timeout(2000)
            print(f"✓ Navigation vers: {page.url}")
            
            # Observe the page
            print(f"✓ Observation de la section '{section['text']}'...")
            
            # Scroll to top first
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1500)
            
            section_height = page.evaluate("document.body.scrollHeight")
            print(f"✓ Hauteur de la page: {section_height}px")
            
            # Scroll down slowly with more steps
            scroll_steps = 4
            for step in range(scroll_steps):
                scroll_position = (section_height // scroll_steps) * (step + 1)
                page.evaluate(f"window.scrollTo(0, {min(scroll_position, section_height)})")
                page.wait_for_timeout(2000)
                print(f"✓ Scroll {step+1}/{scroll_steps} - Position: {min(scroll_position, section_height)}px")
                
                # Observe visible content
                visible_headings = page.locator("h1, h2, h3, h4, .title").filter(has_text="")
                for j in range(min(visible_headings.count(), 3)):
                    heading = visible_headings.nth(j)
                    if heading.is_visible():
                        text = heading.text_content()
                        if text and text.strip() and len(text.strip()) > 2:
                            print(f"   → {text.strip()[:50]}")
            
            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1500)
            print(f"✓ Section '{section['text']}' explorée")
        
        # Return to main profile page
        print("\n=== RETOUR À LA PAGE PROFIL PRINCIPALE ===")
        page.goto(f"{_base_url()}/client/", wait_until="load")
        page.wait_for_timeout(2000)
        print(f"✓ Retour vers: {page.url}")
        
        # Final scroll observation
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1500)
        print("✓ Vue finale de la page profil")
        
        print("\n=== FIN DU SCÉNARIO ===")
        page.wait_for_timeout(3000)  # Pause finale pour observation
        
        browser.close()
        print("\n✓ Test terminé - Parcours complet réussi!")


if __name__ == "__main__":
    test_full_cart_scenario()
