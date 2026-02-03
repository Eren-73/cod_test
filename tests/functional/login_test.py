# tests/functional/login_test.py
# Verifies the customer login page renders for functional sanity checks.
# Ensures the login workflow with a known demo user stays stable before releases.
# RELEVANT FILES: customer/views.py, customer/templates/login.html, cooldeal/urls.py

import os

from django.contrib.auth import get_user_model
import pytest
from playwright.sync_api import Playwright, sync_playwright

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


def _explore_before_login(page) -> None:
    page.goto(f"{_base_url()}/", wait_until="networkidle")
    page.mouse.wheel(0, 800)
    page.wait_for_timeout(1500)
    page.mouse.wheel(0, 800)
    page.wait_for_timeout(1500)
    page.mouse.wheel(0, -1200)
    page.wait_for_timeout(1200)


def test_login_page_loads() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        page.goto(f"{_base_url()}/customer/", wait_until="networkidle")
        assert "Beautyhouse" in page.title()
        assert page.url.startswith(f"{_base_url()}/customer/")
        assert page.locator("text=Connexion").count() >= 1
        browser.close()


def test_can_navigate_to_password_reset() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        page.goto(f"{_base_url()}/customer/forgot_password", wait_until="domcontentloaded")
        form = page.locator("form#contact-form")
        assert form.count() == 1
        assert form.locator("input[name=\"username\"]").count() == 1
        browser.close()


def test_login_flow_authenticates() -> None:
    username, password = _ensure_demo_user()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
        _explore_before_login(page)
        page.goto(f"{_base_url()}/customer/", wait_until="networkidle")
        page.fill("input[name=\"username\"]", username)
        page.fill("input[name=\"password\"]", password)
        page.click("button:has-text('Submit')")
        page.wait_for_url(f"{_base_url()}/", wait_until="networkidle")
        assert page.url.startswith(f"{_base_url()}/")
        browser.close()
