import re
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright, expect


BASE_URL = "https://localhost:8000"

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
    page.goto("https://localhost:8000/")
    expect(page).to_have_title(re.compile("ft_transcendence"))

# def test_signup and Tournament button
def test_login(page: Page):
    # goto signup page
    page.goto("https://localhost:8000/")
    page.click("#loginGoToSignup")
    expect(page).to_have_url("https://localhost:8000/signup")
    
    # signup
    page.locator("#signupEmail").fill("lenox@lenox.at")
    page.locator("#signupPassword1").fill("12345678")
    page.locator("#signupPassword2").fill("12345678")
    page.locator("#signupSubmitButton").click()
    expect(page).to_have_url("https://localhost:8000/")
    
    # Tournament button
    page.locator('#playMenuGoToTournament').click()
    expect(page).to_have_url("https://localhost:8000/tournament")

    # Create Tournament
    page.locator('#createName').fill("DieAlone")
    page.locator('#createTournamentButton').click()
    expect(page).to_have_url("https://localhost:8000/tournament-lobby")


@pytest.fixture(scope="function")
def login(page: Page):
        
    print("before the test runs")
    page.goto(BASE_URL)

    page.locator("#loginEmail").fill("play@wright.at")
    page.locator("#loginPassword").fill("12345678")
    page.locator("#loginSubmitButton").click()

    page.wait_for_selector("#navbar")



def test_profile(login):
    page.locator("#profileButton").click()
    
    



#def test_friend_page(page: Page):
#    test_login(page)
#    page.goto(BASE_URL)

    


