
from playwright.sync_api import expect
from playwright.sync_api import Page


class TestHome:
    def test_home_page_after_login(self, page: Page):
        expect(page.locator("#playMenuGoToTournament")).to_be_visible()

    
