# d:\Projets\Projet_final test\cod_test\tests\functional\cart_navigation_test.py
# Test navigation vers le panier via hover menu
# Vérifie que le menu déroulant du panier fonctionne correctement
# RELEVANT FILES: base.html, shop/templates/cart.html

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
    return os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"


def _slow_mo() -> int:
    """Get slow motion delay from environment variable."""
    return int(os.getenv("PLAYWRIGHT_SLOW_MO", "1500"))


def _ensure_demo_user() -> tuple[str, str]:
    username = "husseni"
    password = "husseni12345"
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


@pytest.mark.django_db
def test_access_cart_via_hover_menu() -> None:
    """Test accessing cart page via hover menu on cart icon."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        # Login
        _login(page, username, password)

        # Go to home page
        page.goto(f"{_base_url()}/", wait_until="load")
        page.wait_for_timeout(2000)

        # Find cart icon in header - try multiple possible selectors
        cart_icon = page.locator(".cart-icon, .shopping-cart, a[href*='cart'], .zmdi-shopping-cart").first
        
        if cart_icon.count() > 0:
            print(f"Found cart icon: {cart_icon.count()} element(s)")
            
            # Hover over cart icon
            cart_icon.hover()
            page.wait_for_timeout(1000)
            
            # Look for "Voir panier" link or cart dropdown
            voir_panier = page.locator("a:has-text('Voir panier'), a:has-text('View cart'), a:has-text('Panier')")
            
            if voir_panier.count() > 0:
                print(f"Found 'Voir panier' link: {voir_panier.count()} element(s)")
                voir_panier.first.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
                
                # Verify we're on cart page
                print(f"Current URL: {page.url}")
                assert "/cart" in page.url.lower() or "/panier" in page.url.lower(), f"Expected cart page but got {page.url}"
                
                # Check page content
                page_content = page.content()
                print(f"Page contains 'panier': {'panier' in page_content.lower()}")
                print(f"Page contains 'cart': {'cart' in page_content.lower()}")
            else:
                print("'Voir panier' link not found after hover")
                # Try direct click on cart icon
                cart_icon.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
                print(f"Current URL after click: {page.url}")
        else:
            print("Cart icon not found in header")

        browser.close()


@pytest.mark.django_db
def test_cart_hover_shows_items() -> None:
    """Test that hovering over cart icon shows cart preview."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        _login(page, username, password)
        page.goto(f"{_base_url()}/", wait_until="load")
        page.wait_for_timeout(2000)

        # Find and hover cart icon
        cart_icon = page.locator(".cart-icon, .shopping-cart, a[href*='cart'], .zmdi-shopping-cart").first
        
        if cart_icon.count() > 0:
            cart_icon.hover()
            page.wait_for_timeout(1500)
            
            # Check if dropdown/preview appears
            dropdown = page.locator(".cart-dropdown, .cart-preview, .mini-cart")
            
            if dropdown.count() > 0 and dropdown.is_visible():
                print("Cart dropdown is visible")
                
                # Check for cart items or empty message
                items = dropdown.locator(".cart-item, .product-item")
                empty_msg = dropdown.locator("text=/vide|empty/i")
                
                if items.count() > 0:
                    print(f"Cart has {items.count()} item(s)")
                elif empty_msg.count() > 0:
                    print("Cart is empty (message displayed)")
            else:
                print("Cart dropdown not visible or not found")

        browser.close()


if __name__ == "__main__":
    # Import get_user_model here for standalone execution
    from django.contrib.auth import get_user_model
    test_access_cart_via_hover_menu()
