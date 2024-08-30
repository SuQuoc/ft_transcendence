import pytest
import re
from playwright.sync_api import Page, expect
from conftest import BASE_URL


class TestHome:
    def test_home_page_after_login(self, page: Page):
        page.goto(BASE_URL)
        expect(page.locator("#playMenuGoToTournament")).to_be_visible()

    
    def test_user_dropdown(self, page: Page):
        page.goto(BASE_URL)
        page.locator("#userDropdown").click()
        expect(page.locator("#displayName")).to_be_visible()




    #@pytest.mark.parametrize(
    #    "browser_context_args", ["standard_user"], indirect=True
    #)
    #def test_home_page_after_login(self, browser_context_args, page: Page):
    #    # expect(page).to_have_url(f"{BASE_URL}/")
    #    # expect(page).to_have_title()
#
    #    expect(page.locator("#loginForm")).to_be_visible()
    #    #expect(page.locator("#navbar")).to_be_visible()



    
    