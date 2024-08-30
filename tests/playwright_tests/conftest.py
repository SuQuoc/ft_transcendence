import re
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, expect
import os






from typing import Dict

import pytest
import requests
from _pytest.fixtures import FixtureRequest, SubRequest
from _pytest.nodes import Item
from playwright.sync_api import Page, Playwright


# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36
AUTOMATION_USER_AGENT = "Chrome/91.0.4472.124"
BASE_URL = "https://localhost:8000"
AUTH_STATE_PATH = os.path.join(os.path.dirname(__file__), "auth_state.json")

@pytest.fixture(scope="session")
def authenticate():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        page: Page = context.new_page()
        page.goto(BASE_URL)

        try:
            page.click("#loginGoToSignup")
            expect(page).to_have_url(f"{BASE_URL}/signup")
            page.locator("#signupEmail").fill("play@wright.at")
            page.locator("#signupPassword1").fill("12345678")
            page.locator("#signupPassword2").fill("12345678")
            page.locator("#signupSubmitButton").click()
            #page.wait_for_url(f"{BASE_URL}", timeout=5000)
            if page.url == f"{BASE_URL}":
                print("Signup successful, proceeding with the next steps.")
            else:
                print("Trying login.")
                page.goto(BASE_URL)
                page.locator("#loginEmail").fill("play@wright.at")
                page.locator("#loginPassword").fill("12345678")
                page.locator("#loginSubmitButton").click()

            page.wait_for_selector("#navbar")

            # Save the authentication state
            context.storage_state(path=AUTH_STATE_PATH)
            print(f"Authentication state saved to {AUTH_STATE_PATH}")
            #context.storage_state(path=AUTH_STATE_PATH)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            context.close()
            browser.close()


@pytest.fixture(scope="function")
def context(authenticate):
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(
            ignore_https_errors=True, 
            storage_state=AUTH_STATE_PATH
        )
        yield context
        context.close()
        browser.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext):
    page: Page = context.new_page()
    yield page
    page.close()




#@pytest.fixture(scope="function", autouse=True)
#def goto(page: Page, request: SubRequest):
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
#@pytest.fixture(scope="function")
#def browser_context_args(
#    browser_context_args: Dict, request: SubRequest
#):
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

