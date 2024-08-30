from playwright.sync_api import Page, expect
from conftest import BASE_URL


class TestTournament:
    def test_tournament_page(self, page: Page):
        page.goto(BASE_URL)
        
        page.locator("#playMenuGoToTournament").click()
        expect(page.locator("#createTournamentButton")).to_be_visible()


    def test_lobby_leave_button(self, page: Page):
        self.test_tournament_page(page)
        #page.goto(BASE_URL)
        #expect(page.locator("#playMenuGoToTournament")).to_be_visible()
        #page.locator("#playMenuGoToTournament").click()
#
        #expect(page.locator("#createTournamentButton")).to_be_visible()
        page.locator("#createTournamentButton").click()

        expect(page.locator("#lobbyLeaveButton")).to_be_visible()
        page.locator("#lobbyLeaveButton").click()
        expect(page.locator("#createTournamentButton")).to_be_visible()




        