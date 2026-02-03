# tests/functional/product_explore_test.py
# Simulates a customer visiting every available deal, category, and product link.
# Helps ensure the authenticated browsing paths covering categories and products stay clickable.
# RELEVANT FILES: shop/views.py, shop/templates/shop.html, shop/templates/product-details.html

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


def _collect_hrefs(locator) -> list[str]:
    total = locator.count()
    raw_hrefs = []
    for index in range(total):
        href = locator.nth(index).get_attribute("href")
        if href:
            raw_hrefs.append(href)
    return list(dict.fromkeys(raw_hrefs))


def _extract_product_links(page) -> list[str]:
    return _collect_hrefs(page.locator("a:has-text('Voir plus')"))


def _observation_delay(default: int = 3000) -> int:
    raw = os.getenv("PLAYWRIGHT_OBSERVATION_DELAY")
    return int(raw) if raw and raw.isdigit() else default


def _observe_page(page, delay_ms: int | None = None, max_ratio: float = 0.55) -> None:
    actual_delay = delay_ms if delay_ms is not None else 3000
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
    page.wait_for_timeout(_observation_delay(actual_delay))


def _visit_product_detail(page, product_url: str) -> None:
    page.goto(product_url, wait_until="networkidle")
    assert page.locator("h3").count() >= 1
    assert page.locator("text=En Stock").count() >= 1
    
    # Click through product image thumbnails to explore the gallery.
    thumbnails = page.locator(".product-gallery img, .product-thumbnails img, img[class*='thumb']")
    thumbnail_count = thumbnails.count()
    for idx in range(min(thumbnail_count, 5)):
        try:
            thumbnails.nth(idx).click(timeout=1000)
            page.wait_for_timeout(500)
        except:
            pass
    
    # Scroll so the description/details area appears for each product.
    _observe_page(page)


def _visit_category(page, category_url: str, visited: set[str]) -> None:
    page.goto(category_url, wait_until="load")
    assert page.locator("h2").count() >= 1
    _observe_page(page, max_ratio=0.50)
    product_links = _extract_product_links(page)
    for raw_href in product_links:
        product_url = _normalize_href(raw_href)
        if product_url in visited:
            continue
        visited.add(product_url)
        _visit_product_detail(page, product_url)
        page.goto(category_url, wait_until="load")
        page.wait_for_timeout(800)


def test_login_and_browse_all_categories() -> None:
    username, password = _ensure_demo_user()
    base_deals = f"{_base_url()}/deals/"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        page.goto(f"{_base_url()}/customer/", wait_until="domcontentloaded")
        page.fill("input[name=\"username\"]", username)
        page.fill("input[name=\"password\"]", password)
        page.click("button:has-text('Submit')")
        page.wait_for_url(f"{_base_url()}/", wait_until="networkidle")
        page.goto(base_deals, wait_until="load")
        _observe_page(page)

        visited_products: set[str] = set()
        for raw_href in _extract_product_links(page):
            product_url = _normalize_href(raw_href)
            visited_products.add(product_url)
            _visit_product_detail(page, product_url)
            page.goto(base_deals, wait_until="load")

        category_links = _collect_hrefs(page.locator("aside.widget.categories .widget-categories a"))
        for idx, raw_category in enumerate(category_links, 1):
            normalized_category = _normalize_href(raw_category)
            _visit_category(page, normalized_category, visited_products)
            page.goto(base_deals, wait_until="load")
            page.wait_for_timeout(1000)

        browser.close()
