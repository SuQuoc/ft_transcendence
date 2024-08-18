import re
import pytest
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

def test_has_title(page: Page):
    page.goto("https://127.0.0.1:8000/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("ft_transcendence"))
