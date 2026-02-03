# tests/functional/page_sweep_test.py
# Confirms the main marketing pages exist and respond while performing gentle smooth scrolling.
# RELEVANT FILES: website/views.py, base/views.py, contact/views.py, shop/views.py

import os

from django.contrib.auth import get_user_model
import pytest
from playwright.sync_api import sync_playwright


NAV_ITEMS = [
    ("Accueil", "/"),
    ("Deal", "/deals/"),
    ("À propos", "/a-propos"),
    ("Contact", "/contact/"),
]

pytestmark = pytest.mark.django_db


def _login_after_tour(page, username: str, password: str) -> None:
    page.goto(f"{_base_url()}/customer/", wait_until="networkidle")
    page.fill("input[name=\"username\"]", username)
    page.fill("input[name=\"password\"]", password)
    page.click("button:has-text('Submit')")
    page.wait_for_load_state("load")
    assert page.url.startswith(f"{_base_url()}/" )


def _base_url() -> str:
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


def _is_headless() -> bool:
    raw = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower()
    return raw not in ("0", "false", "off")


def _slow_mo() -> int:
    raw = os.getenv("PLAYWRIGHT_SLOW_MO")
    return int(raw) if raw and raw.isdigit() else 1500


def _smooth_scroll(page) -> None:
    page.evaluate("window.scrollTo({ top: 500, behavior: 'smooth' })")
    page.wait_for_timeout(1200)
    page.evaluate("window.scrollTo({ top: 0, behavior: 'smooth' })")
    page.wait_for_timeout(1200)


def _ensure_demo_user() -> tuple[str, str]:
    username = "eren73"
    password = "eren12345"
    User = get_user_model()
    user, created = User.objects.get_or_create(username=username, defaults={
        "email": "eren73@example.com",
    })
    if created or not user.check_password(password):
        user.set_password(password)
        user.save()
    return username, password


def _click_nav(page, label: str, path: str) -> None:
    locator = page.get_by_role("link", name=label)
    if locator.count():
        locator.first.click()
    else:
        page.goto(f"{_base_url()}{path}", wait_until="domcontentloaded")


def test_pages_load_with_scroll() -> None:
    username, password = _ensure_demo_user()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        for label, path in NAV_ITEMS:
            _click_nav(page, label, path)
            page.wait_for_timeout(500)
            page.wait_for_load_state("load")
            assert page.url.startswith(f"{_base_url()}{path}")
            _smooth_scroll(page)
        _login_after_tour(page, username, password)
        browser.close()
