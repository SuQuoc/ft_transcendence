import os, re, time
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import pytest
from pathlib import Path

# KEYNOTE: If the test is started from another folder other than the ROOT PROJECT FOLDER,
# the .env file will not be found (e.g. you are in the tests folder and run pytest from there)
 
load_dotenv("./docker_compose_files/.env")
BASE_URL = os.getenv("SERVER_URL", "https://localhost:8443") # Using the defined SERVER_URL from the env, if not defined, use localhost
print(f"Using BASE_URL !!!!!!!!!!!!: {BASE_URL}")

# Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36
AUTOMATION_USER_AGENT = "Chrome/91.0.4472.124"
AUTH_STATE_PATH = os.path.join(os.path.dirname(__file__), "auth_state.json")
USERMAIL = "transcendence42vienna+test1@gmail.com"
USERPW = "RShLrG2vV3"
USERDISPLAYNAME = "test1"

# DEFINES for tournament tests
N_USERS = 6 # min 6
T_DISPLAYNAME = "tuser"
T_NAME = "tname"

# Fixtures to test anything after successful signup/login, the fixtures avoid re-login all the time
@pytest.fixture(scope="session")
def authenticate():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        page: Page = context.new_page()
        try:
            signup(page, USERMAIL, USERPW, USERPW)
            set_display_name(page, USERDISPLAYNAME)
        except Exception as e:
            print(f"Signup failed probably because user already exists ;) : {e}")
            print("Trying login...")
            try:
                login(page, USERMAIL, USERPW)
                page.wait_for_selector("#navbar", timeout=5000)
            except Exception as e:
                print(f"Error both signup and login failed to get auth cookies, your tests will fail haha: {e}")

        finally:
            context.storage_state(path=AUTH_STATE_PATH)
            context.close()
            browser.close()


@pytest.fixture(scope="session")
def pages():
    with sync_playwright() as p:
        browser: Browser = p.chromium.launch()
        pages = []
        contexts = []
        for i in range(N_USERS):
            context: BrowserContext = browser.new_context(ignore_https_errors=True)
            context.set_default_timeout(3000)
            contexts.append(context)
            
            page: Page = context.new_page()
            pages.append(page)
            try:
                signup(page, f"transcendence42vienna+tuser{i}@gmail.com", USERPW, USERPW)
                set_display_name(page, f"{T_DISPLAYNAME}{i}")
            except Exception as e:
                try:
                    login(page, f"transcendence42vienna+tuser{i}@gmail.com", USERPW)
                    page.wait_for_selector("#navbar", timeout=5000)
                except Exception as e:
                    print(f"failed to create user tuser{i}: {e}")
        
        yield pages

        for page, context in zip(pages, contexts):
            page.close()
            context.close()

        browser.close()
        

@pytest.fixture(scope="function", params=["chromium"])
def browser_type(request):
    return request.param


@pytest.fixture(scope="function")
def context(browser_type, authenticate):
    """
    Sets up browser context to include auth cookies
    """
    with sync_playwright() as p:
        if browser_type == "chromium":
            browser: Browser = p.chromium.launch()
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")
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
        browser: Browser = p.chromium.launch() # only testing with one browser because we cant do signup with same user twice
        context: BrowserContext = browser.new_context(ignore_https_errors=True)
        login_page: Page = context.new_page()
        yield login_page
        login_page.close()
        context.close()
        browser.close()


### utils ##############################
def signup(page: Page, email: str, password1: str, password2: str):
    page.goto(BASE_URL)
    page.click("#loginGoToSignup")
    expect(page.locator("#signupForm")).to_be_visible()
    page.locator("#signupEmail").fill(email)
    page.locator("#signupPassword1").fill(password1)
    page.locator("#signupPassword2").fill(password2)
    page.locator("#signupSubmitButton").click()
    otp = get_otp()
    page.locator("#otpCode").fill(otp)
    page.locator("#signupSubmitButton").click()


def login(page: Page, email: str, password: str):
    page.goto(BASE_URL)
    page.locator("#loginEmail").fill(email)
    page.locator("#loginPassword").fill(password)
    page.locator("#loginSubmitButton").click()
    otp = get_otp()
    page.locator("#otpCode").fill(otp)
    page.locator("#loginSubmitButton").click()


def set_display_name(page: Page, display_name: str):
    page.wait_for_selector("#displayNameForm", timeout=5000)
    page.locator("#displayNameInput").fill(display_name)
    page.locator("#displayNameSubmitButton").click()
    page.wait_for_selector("#navbar", timeout=5000)


def delete_user(page: Page, password: str):
    page.locator("#userProfileButton").click()
    page.locator("#deleteUserButton").click()
    page.locator("#deleteUserPassword").fill(password)
    page.locator("#requestDeleteUserButton").click()
    # [aguilmea] delete user has no otp in the front end but in the backend it has - so it is not working rigth now


def get_otp():
    base = Path(__file__).resolve().parent.parent.parent  # Correct usage of parent
    directory = base / 'src/registration/project/emails/'
    time.sleep(2)  # Wait for 2 seconds the email to be created
    files = [f for f in directory.iterdir() if f.is_file()]
    last_saved_file = max(files, key=os.path.getmtime)
    with open(last_saved_file, 'r') as f:
        content = f.read().strip()
    match = re.search(r'The code is:\s*([A-Za-z0-9]{16})', content)
    if match:
        otp = match.group(1)  # Extract the matched OTP
        return otp
    else:
        return None
############################################


