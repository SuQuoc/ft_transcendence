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

def test_homepage(page: Page):
    page.goto("https://127.0.0.1:8000/")
    expect(page).to_have_title(re.compile("ft_transcendence"))

# def test_signup and Tournament button
def test_login(page: Page):
    # goto signup page
    page.goto("https://127.0.0.1:8000/")
    page.click("#signup-login-page")
    expect(page).to_have_url("https://127.0.0.1:8000/signup")
    
    # signup
    page.locator("#signupEmail").fill("lenox@lenox.at")
    page.locator("#signupPassword1").fill("12345678")
    page.locator("#signupPassword2").fill("12345678")
    page.locator("#signup-submit-button").click()
    expect(page).to_have_url("https://127.0.0.1:8000/")
    
    # Tournament button
    page.locator('#main-content a[href="/tournament"].btn.btn-secondary.w-100').click()
    expect(page).to_have_url("https://127.0.0.1:8000/tournament")
