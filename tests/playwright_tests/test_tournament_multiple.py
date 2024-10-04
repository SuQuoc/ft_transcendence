import os
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import pytest
from conftest import signup, login, set_display_name, N_USERS, USERPW



class TestTournamentMultiple:
    def change_slider_value(self, page, slider_selector, value):
        # Set the value of the slider
        page.eval_on_selector(slider_selector, f"el => el.value = {value}")
        # Dispatch the input event to simulate user interaction
        page.eval_on_selector(slider_selector, "el => el.dispatchEvent(new Event('input'))")
        # Dispatch the change event to ensure any change listeners are triggered
        page.eval_on_selector(slider_selector, "el => el.dispatchEvent(new Event('change'))")

    # test creating tournament with same name
    def test_create_tournament(self, pages):
        # going to tournament page
        for page in pages[:N_USERS - 1]:
            page.locator("#playMenuGoToTournament").click()
        #expect(pages[0].locator("#joinNoTournamentsAvailable")).to_be_visible()
        expect(pages[0].locator("#createTournamentForm")).to_be_visible()

        # creating tournaments
        for page in pages[:3]:
            tournament_name = f"tnametuser{pages.index(page)}"
            page.locator("#createName").fill(tournament_name)
            page.locator("label[for='create8PlayerInput']").click() # needs to locate label because the input can't be clicked
            self.change_slider_value(page, "#createPointsToWin", 10)
            page.locator("#createTournamentButton").click()
            expect(page.locator("tournament-lobby-page")).to_be_visible()
            # checking if the tournament is visible for other users in lobby
            expect(pages[-2].locator(f"join-tournament-element[name='{tournament_name}']")).to_be_visible()
        
        # checking if the tournaments are visible when going to lobby page after they are created
        pages[-1].locator("#playMenuGoToTournament").click()
        for i in range(3):
            expect(pages[-1].locator(f"join-tournament-element[name='tnametuser{i}']")).to_be_visible()