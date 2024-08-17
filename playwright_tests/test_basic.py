import re
import pytest
import socket
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, expect

@pytest.fixture(scope="function")
def context():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        yield context
        context.close()
        browser.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page: Page = context.new_page()
    yield page
    page.close()

def test_homepage(page: Page):
    page.goto("https://127.0.0.1:8000/")
    expect(page).to_have_title(re.compile("template"))

def test_joinTournamentPage(page: Page):
    page.goto("https://127.0.0.1:8000/")
    page.locator('#main-content a[href="/tournament"].btn.btn-secondary.w-100').click()
    expect(page).to_have_url("https://127.0.0.1:8000/tournament")
