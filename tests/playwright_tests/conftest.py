import os
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import pytest

# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36
AUTOMATION_USER_AGENT = "Chrome/91.0.4472.124"
BASE_URL = "https://localhost:8000"
AUTH_STATE_PATH = os.path.join(os.path.dirname(__file__), "auth_state.json")



def signup(page: Page, email: str, password1: str, password2: str):
    page.click("#loginGoToSignup")
    expect(page.locator("#signupForm")).to_be_visible()
    page.locator("#signupEmail").fill(email)
    page.locator("#signupPassword1").fill(password1)
    page.locator("#signupPassword2").fill(password2)
    page.locator("#signupSubmitButton").click()


def login(page: Page, email: str, password: str):
    page.goto(BASE_URL)
    page.locator("#loginEmail").fill(email)
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitButton").click()


def set_display_name(page: Page, display_name: str):
    page.wait_for_selector("#displayNameForm", timeout=5000)
    page.locator("#displayNameInput").fill(display_name)
    page.locator("#displayNameSubmitButton").click()
    page.wait_for_selector("#navbar", timeout=5000)

# Fixtures to test anything after successful signup/login, the fixtures avoid re-login all the time
@pytest.fixture(scope="session")
def authenticate():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        page: Page = context.new_page()
        page.goto(BASE_URL)

        try:
            signup(page, "test1@test.at", "12345678", "12345678")
            set_display_name(page, "test1")
        except Exception as e:
            print(f"Signup failed probably because user already exists ;) : {e}")
            print("Trying login...")
            try:
                login(page, "test1@test.at", "12345678")
                page.wait_for_selector("#navbar", timeout=5000)
            except:
                print(f"Error both signup and login failed to get auth cookies, your tests will fail haha: {e}")

        finally:
            context.storage_state(path=AUTH_STATE_PATH)
            context.close()
            browser.close()

@pytest.fixture(scope="function", params=["chromium", "firefox", "webkit"])
def browser_type(request):
    return request.param


@pytest.fixture(scope="function")
def context(browser_type, authenticate):
    """
    Sets up browser context to include auth cookies
    """
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True, storage_state=AUTH_STATE_PATH)
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """
    returns a Page as a logged in user
    """
    page: Page = context.new_page()
    page.goto(BASE_URL)
    page.wait_for_selector("#navbar", timeout=5000)
    yield page
    page.close()


# fixtures to TEST the signup, login process
@pytest.fixture(scope="function")
def login_page():
    """
    returns a page without auth cookies to test signup and login
    """
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(
            ignore_https_errors=True,
        )
        login_page: Page = context.new_page
        yield login_page
        login_page.close()
        context.close()
        browser.close()


