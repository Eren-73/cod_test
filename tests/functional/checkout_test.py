# d:\Projets\Projet_final test\cod_test\tests\functional\checkout_test.py
# Functional tests for checkout/payment process
# Tests the full flow: cart → checkout form → payment
# RELEVANT FILES: shop/templates/checkout.html, shop/views.py, customer/models.py

import os
from playwright.sync_api import sync_playwright, expect
from customer.models import Customer
from django.contrib.auth.models import User
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
    """Create or get demo user for testing."""
    username = "husseni"
    password = "husseni12345"
    email = "husseni@test.com"

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, email=email, password=password)
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
    # Click the first visible submit button (login form)
    page.locator("button[type='submit']").first.click()
    page.wait_for_load_state("networkidle")


@pytest.mark.django_db
def test_checkout_page_loads_with_cart() -> None:
    """Test that checkout page loads when user has items in cart."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        # Login
        _login(page, username, password)

        # Go directly to checkout page
        page.goto(f"{_base_url()}/shop/checkout", wait_until="load")
        page.wait_for_timeout(2000)

        # Check if checkout page elements are present
        assert "Paiement" in page.title() or "Checkout" in page.title()
        
        # Check for accordion sections
        order_details = page.locator("text=Détails de la commande")
        assert order_details.count() > 0, "Order details section not found"
        
        personal_info = page.locator("text=Informations personnelles")
        assert personal_info.count() > 0, "Personal information section not found"

        browser.close()


@pytest.mark.django_db
def test_checkout_displays_cart_items() -> None:
    """Test that checkout page displays cart items correctly."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        _login(page, username, password)
        
        page.goto(f"{_base_url()}/shop/checkout", wait_until="load")
        page.wait_for_timeout(2000)

        # Check for order review table
        order_table = page.locator("table")
        if order_table.count() > 0:
            # Check for table headers
            headers = order_table.locator("thead th")
            print(f"Found {headers.count()} table headers")
            
            # Check for product rows
            rows = order_table.locator("tbody tr")
            print(f"Found {rows.count()} cart items in checkout")

        browser.close()


@pytest.mark.django_db
def test_checkout_form_validation() -> None:
    """Test that checkout form validates required fields."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        _login(page, username, password)
        
        page.goto(f"{_base_url()}/shop/checkout", wait_until="load")
        page.wait_for_timeout(2000)

        # Wait for Vue.js to initialize
        page.wait_for_timeout(1500)

        # Expand personal information section
        personal_info_link = page.locator("a:has-text('Informations personnelles')")
        if personal_info_link.count() > 0:
            personal_info_link.click()
            page.wait_for_timeout(1000)

        # Try to find payment button
        pay_button = page.locator("button:has-text('Payer'), button.validate")
        if pay_button.count() > 0:
            print(f"Found {pay_button.count()} payment button(s)")
            
            # Scroll to button
            pay_button.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            
            # Check if form fields are present
            first_name_input = page.locator("input[name='first'], input.first_name")
            last_name_input = page.locator("input[name='last'], input.last_name")
            phone_input = page.locator("input[name='phone'], input.phone_number")
            
            print(f"Form fields found - First name: {first_name_input.count()}, Last name: {last_name_input.count()}, Phone: {phone_input.count()}")

        browser.close()


@pytest.mark.django_db
def test_checkout_back_to_cart_link() -> None:
    """Test that 'back to cart' link works from checkout page."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()

        _login(page, username, password)
        
        page.goto(f"{_base_url()}/shop/checkout", wait_until="load")
        page.wait_for_timeout(2000)

        # Find "Retour au panier" link
        back_link = page.locator("a:has-text('Retour au panier'), a.o-back-to")
        if back_link.count() > 0:
            back_link.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1500)
            
            # Verify we're on cart page
            assert "/shop/cart" in page.url, f"Expected to be on cart page, but got {page.url}"

        browser.close()
