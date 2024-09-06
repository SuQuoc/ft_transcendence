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


# Fixtures to test anything after successful signup/login, the fixtures avoid re-login all the time
@pytest.fixture(scope="session")
def authenticate():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        page: Page = context.new_page()
        page.goto(BASE_URL)

        try:
            page.click("#loginGoToSignup")
            expect(page.locator("#signupForm")).to_be_visible()
            page.locator("#signupEmail").fill("test1@test.at")
            page.locator("#signupPassword1").fill("12345678")
            page.locator("#signupPassword2").fill("12345678")
            page.locator("#signupSubmitButton").click()

            page.wait_for_selector("#displayNameForm", timeout=5000)
            page.locator("#displayNameInput").fill("test1")
            page.locator("#displayNameSubmitButton").click()
            
            page.wait_for_selector("#navbar", timeout=5000)
        except Exception as e:
            print(f"Signup failed probably because user already exists ;) : {e}")
            print("Trying login...")
            page.goto(BASE_URL)
            page.locator("#loginEmail").fill("test1@test.at")
            page.locator("#loginPassword").fill("12345678")
            page.locator("#loginSubmitButton").click()
            try:
                page.wait_for_selector("#navbar", timeout=5000)
            except:
                print(f"Error both signup and login failed to get auth cookies, your tests will fail haha: {e}")

            # Save the authentication state
            # page.locator("#displayNameForm").fill("test1")
            # page.locator("#displayNameSubmitButton").click()

        finally:
            context.storage_state(path=AUTH_STATE_PATH)
            context.close()
            browser.close()


@pytest.fixture(scope="function")
def context(authenticate):
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


# @pytest.fixture(scope="function", autouse=True)
# def goto(page: Page, request: SubRequest):
#    """Fixture to navigate to the base URL based on the user.
#
#    If the 'storage_state' is set in 'browser_context_args', it navigates to the inventory page,
#    otherwise, it navigates to the login page.
#
#    Args:
#        page (Page): Playwright page object.
#        request (SubRequest): Pytest request object to get the 'browser_context_args' fixture value.
#            If 'browser_context_args' is set to a user parameter (e.g., 'standard_user'),
#            the navigation is determined based on the user.
#
#    Example:
#        @pytest.mark.parametrize('browser_context_args', ["standard_user"], indirect=True)
#    """
#    if request.getfixturevalue("browser_context_args").get("storage_state"):
#        page.goto(f"{BASE_URL}")
#    else:
#        page.goto("/signup")
#
#
# @pytest.fixture(scope="function")
# def browser_context_args(
#    browser_context_args: Dict, request: SubRequest
# ):
#    """This fixture allows setting browser context arguments for Playwright.
#
#    Args:
#        browser_context_args (dict): Base browser context arguments.
#        request (SubRequest): Pytest request object to get the 'browser_context_args' fixture value.
#        base_url (str): The base URL for the application under test.
#    Returns:
#        dict: Updated browser context arguments.
#    See Also:
#        https://playwright.dev/python/docs/api/class-browser#browser-new-contex
#
#    Returns:
#        dict: Updated browser context arguments.
#    """
#
#    context_args = {
#        **browser_context_args,
#        "no_viewport": True,
#        "user_agent": AUTOMATION_USER_AGENT,
#        "ignore_https_errors": True,
#    }
#
#    if hasattr(request, "param"):
#        if request.param == "standard_user":
#            pass
#        context_args["storage_state"] = {
#            "cookies": [
#                {
#                    "name": "session-username",
#                    "value": request.param,
#                    "url": "https://localhost:8000",
#                }
#            ]
#        }
#    return context_args
#
