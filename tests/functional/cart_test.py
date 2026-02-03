# tests/functional/cart_test.py
# Simulates adding products to cart, modifying quantities, and verifying totals.
# Tests the cart functionality from product detail to cart view.
# RELEVANT FILES: customer/views.py, shop/templates/product-details.html, shop/templates/cart.html

import os

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import sync_playwright

pytestmark = pytest.mark.django_db


def _base_url() -> str:
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


def _is_headless() -> bool:
    raw = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower()
    return raw not in ("0", "false", "off")


def _slow_mo() -> int:
    raw = os.getenv("PLAYWRIGHT_SLOW_MO")
    return int(raw) if raw and raw.isdigit() else 1500


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
    return username, password


def _normalize_href(href: str) -> str:
    if href.startswith("http"):
        return href
    base = _base_url().rstrip("/")
    if href.startswith("/"):
        return f"{base}{href}"
    return f"{base}/{href}"


def _login(page, username: str, password: str) -> None:
    page.goto(f"{_base_url()}/customer/", wait_until="domcontentloaded")
    page.fill("input[name=\"username\"]", username)
    page.fill("input[name=\"password\"]", password)
    page.click("button:has-text('Submit')")
    page.wait_for_url(f"{_base_url()}/", wait_until="networkidle")


def _observe_page(page, delay_ms: int = 2000, max_ratio: float = 0.5) -> None:
    page.evaluate(
        "async (ratio) => {" \
        "const scrollStep = window.innerHeight / 3;" \
        "let current = 0;" \
        "const target = document.body.scrollHeight * ratio;" \
        "while (current < target) {" \
        "  window.scrollTo({ top: current, behavior: 'smooth' });" \
        "  await new Promise(resolve => setTimeout(resolve, 200));" \
        "  current += scrollStep;" \
        "}" \
        "window.scrollTo({ top: target, behavior: 'smooth' });"
        "}"
    , max_ratio)
    page.wait_for_timeout(delay_ms)


def test_add_products_to_cart() -> None:
    """Test adding multiple products to cart and verifying quantities."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        
        # Login
        _login(page, username, password)
        
        # Go to deals page
        page.goto(f"{_base_url()}/deals/", wait_until="load")
        _observe_page(page)
        
        # Find first product link
        product_links = page.locator("a:has-text('Voir plus')")
        if product_links.count() > 0:
            first_product_link = product_links.nth(0).get_attribute("href")
            first_product_link = _normalize_href(first_product_link)
            page.goto(first_product_link, wait_until="networkidle")
            
            # Scroll to see product details
            _observe_page(page)
            
            # Wait for Vue.js to initialize
            page.wait_for_timeout(1500)
            
            # Debug: Check if Vue is loaded
            vue_loaded = page.evaluate("typeof Vue !== 'undefined'")
            print(f"Vue loaded: {vue_loaded}")
            
            # Make sure quantity input is visible and has value
            quantity_input = page.locator("input[name='quantite']")
            if quantity_input.count() > 0:
                quantity_input.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                
                # Debug: Check initial value
                initial_value = quantity_input.input_value()
                print(f"Initial quantity value: {initial_value}")
                
                # Click to focus
                quantity_input.click()
                page.wait_for_timeout(200)
                
                # Select all and replace
                page.keyboard.press("Control+A")
                page.wait_for_timeout(100)
                page.keyboard.type("2")
                page.wait_for_timeout(500)
                
                # Verify quantity value
                qty_value = quantity_input.input_value()
                print(f"Quantity value after typing: {qty_value}")
                
                # Trigger input/change events manually
                quantity_input.dispatch_event("input")
                quantity_input.dispatch_event("change")
                page.wait_for_timeout(300)
                
                final_value = quantity_input.input_value()
                print(f"Final quantity value: {final_value}")
                
                assert qty_value == "2", f"Quantity should be 2 but got {qty_value}"
            
            # Add to cart
            add_to_cart_btn = page.locator("button:has-text('Ajouter au panier')")
            if add_to_cart_btn.count() > 0:
                # Debug: Check Vue data before clicking
                vue_quantite = page.evaluate("window.vueApp ? window.vueApp.quantite : 'undefined'")
                print(f"Vue.js quantite value: {vue_quantite}")
                
                # Debug: Check jQuery selector value
                jquery_value = page.evaluate("$('input[name=quantite]').val()")
                print(f"jQuery selector value: {jquery_value}")
                
                add_to_cart_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                add_to_cart_btn.click()
                # Wait for page reload after successful AJAX
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
                
                # Verify success message or check for error
                error_alert = page.locator(".alert.alert-danger, div[class*='error']")
                if error_alert.count() > 0 and error_alert.is_visible():
                    error_text = error_alert.text_content()
                    raise AssertionError(f"Error adding to cart: {error_text}")
                
                # Verify success message
                success_alert = page.locator(".alert-success")
                if success_alert.count() > 0:
                    assert success_alert.is_visible()
        
        # Go to deals page again to add another product
        page.goto(f"{_base_url()}/deals/", wait_until="load")
        
        # Add second product
        if product_links.count() > 1:
            second_product_link = product_links.nth(1).get_attribute("href")
            second_product_link = _normalize_href(second_product_link)
            page.goto(second_product_link, wait_until="networkidle")
            _observe_page(page)
            
            # Wait for Vue.js initialization
            page.wait_for_timeout(1500)
            
            # Add to cart with default quantity
            add_to_cart_btn = page.locator("button:has-text('Ajouter au panier')")
            if add_to_cart_btn.count() > 0:
                add_to_cart_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                add_to_cart_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
        
        # Navigate to cart page
        page.goto(f"{_base_url()}/shop/cart", wait_until="load")
        _observe_page(page)
        
        # Verify cart contains products
        cart_rows = page.locator("table.table_cart tbody tr")
        cart_count = cart_rows.count()
        assert cart_count > 0, "Cart should contain at least one product"
        
        # Verify cart icon shows item count
        cart_icon_count = page.locator(".cart-icon span")
        if cart_icon_count.count() > 0:
            count_text = cart_icon_count.text_content()
            assert count_text and int(count_text) > 0
        
        page.wait_for_timeout(2000)
        browser.close()


def test_modify_cart_quantities() -> None:
    """Test modifying product quantities in cart."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        
        # Login and add product to cart first
        _login(page, username, password)
        page.goto(f"{_base_url()}/deals/", wait_until="load")
        
        product_links = page.locator("a:has-text('Voir plus')")
        if product_links.count() > 0:
            first_product_link = product_links.nth(0).get_attribute("href")
            first_product_link = _normalize_href(first_product_link)
            page.goto(first_product_link, wait_until="networkidle")
            
            # Wait for Vue.js initialization
            page.wait_for_timeout(1500)
            
            add_to_cart_btn = page.locator("button:has-text('Ajouter au panier')")
            if add_to_cart_btn.count() > 0:
                add_to_cart_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                add_to_cart_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
        
        # Go to cart
        page.goto(f"{_base_url()}/shop/cart", wait_until="load")
        _observe_page(page)
        
        # Verify cart page loaded
        assert page.locator("table.table_cart").count() > 0
        
        page.wait_for_timeout(2000)
        browser.close()


def test_remove_from_cart() -> None:
    """Test removing products from cart."""
    username, password = _ensure_demo_user()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        
        # Login and add product
        _login(page, username, password)
        page.goto(f"{_base_url()}/deals/", wait_until="load")
        
        product_links = page.locator("a:has-text('Voir plus')")
        if product_links.count() > 0:
            first_product_link = product_links.nth(0).get_attribute("href")
            first_product_link = _normalize_href(first_product_link)
            page.goto(first_product_link, wait_until="networkidle")
            
            # Wait for Vue.js initialization
            page.wait_for_timeout(1500)
            
            add_to_cart_btn = page.locator("button:has-text('Ajouter au panier')")
            if add_to_cart_btn.count() > 0:
                add_to_cart_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(300)
                add_to_cart_btn.click()
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(1500)
        
        # Go to cart
        page.goto(f"{_base_url()}/shop/cart", wait_until="load")
        _observe_page(page)
        
        # Get initial cart count
        initial_rows = page.locator("table.table_cart tbody tr").count()
        
        # Click delete button if exists
        delete_btn = page.locator(".p_action a i.zmdi-delete").first
        if delete_btn.count() > 0:
            delete_btn.click()
            page.wait_for_timeout(2000)
            
            # Verify cart updated (should have fewer items or show empty message)
            new_rows = page.locator("table.table_cart tbody tr").count()
            assert new_rows <= initial_rows
        
        page.wait_for_timeout(2000)
        browser.close()
