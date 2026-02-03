# tests/functional/site_tour_test.py
# Exercises a basic tour of the public pages so we can manually observe the main experience via Playwright.
# Walks the home, deals, and contact paths in slow-mo to check navigation health.
# RELEVANT FILES: website/views.py, shop/views.py, contact/views.py

import os

from playwright.sync_api import sync_playwright


def _base_url() -> str:
    return os.getenv("PLAYWRIGHT_BASE_URL", "http://localhost:8000")


def _is_headless() -> bool:
    raw = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower()
    return raw not in ("0", "false", "off")


def _slow_mo() -> int:
    raw = os.getenv("PLAYWRIGHT_SLOW_MO")
    return int(raw) if raw and raw.isdigit() else 1500


def _visit(page, path: str):
    response = page.goto(f"{_base_url()}{path}", wait_until="networkidle")
    assert response and response.ok
    assert page.url.startswith(f"{_base_url()}{path}")
    page.wait_for_timeout(3000)

    def _explore_home(page) -> None:
        _visit(page, "/")
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, 1000)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, -1500)
        page.wait_for_timeout(1200)
        page.mouse.wheel(0, 1000)


def test_site_tour_home_deals_contact() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=_is_headless(), slow_mo=_slow_mo())
        page = browser.new_page()
            _explore_home(page)
        if page.get_by_role("link", name="Deals").count():
            page.get_by_role("link", name="Deals").first.click()
        else:
            page.goto(f"{_base_url()}/deals/", wait_until="domcontentloaded")
        _visit(page, "/deals/")
        page.get_by_role("link", name="Contact").first.click()
        _visit(page, "/contact/")
        browser.close()
