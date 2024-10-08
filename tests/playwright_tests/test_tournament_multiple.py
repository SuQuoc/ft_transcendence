import os
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import pytest
from conftest import signup, login, set_display_name, N_USERS, USERPW, T_DISPLAYNAME, T_NAME



class TestTournamentMultiple:
       # test creating tournament with same name
    def test_create_tournament(self, pages):
        # going to tournament page
        for page in pages[:N_USERS - 1]:
            page.locator("#playMenuGoToTournament").click()
        #expect(pages[0].locator("#joinNoTournamentsAvailable")).to_be_visible()
        expect(pages[0].locator("#createTournamentForm")).to_be_visible()

        # creating tournaments
        for page in pages[:3]:
            tournament_name = f"{T_NAME}{pages.index(page)}"
            create_tournament(page, tournament_name=tournament_name, n_players=8, points_to_win=10)            
            # checking if the tournament is visible for other users in lobby
            expect(pages[-2].locator(f"join-tournament-element[name='{tournament_name}']")).to_be_visible()
        
        # checking if the tournaments are visible when going to lobby page after they are created
        pages[-1].locator("#playMenuGoToTournament").click()
        for i in range(3):
            expect(pages[-1].locator(f"join-tournament-element[name='{T_NAME}{i}']")).to_be_visible()



    def test_join_tournament(self, pages):
        tname=f"{T_NAME}0"
        
        # going to tournament page
        for page in pages:
            page.locator("#playMenuGoToTournament").click()
        expect(pages[0].locator("#createTournamentForm")).to_be_visible()
        
        create_tournament(pages[0], tournament_name=tname, n_players=8, points_to_win=1)
        join_tournament(pages[1], tournament_name=tname)
        
        # checking if the current_player_num is correctly updated after joining a tournament
        expect(pages[2].locator(f"join-tournament-element[name='{tname}']").locator("[name='join_current_player_num']")).to_have_text("2")

        # checking if the info of the tournament is correctly sent and displayed on the lobby page
        for page in pages[:2]:
            expect(page.locator(f"tournament-lobby-player-element[name='{T_DISPLAYNAME}0']")).to_be_visible()
            expect(page.locator(f"tournament-lobby-player-element[name='{T_DISPLAYNAME}1']")).to_be_visible()
            
            expect(page.locator("#lobbyTournamentName")).to_have_text(tname)
            expect(page.locator("#lobbyPointsToWin")).to_have_text("1")
            expect(page.locator("#lobbyMaxPlayerNum")).to_have_text("8")
            expect(page.locator("#lobbyCurrentPlayerNum")).to_have_text("2")

        expect(page.locator(f"tournament-lobby-player-element[name='{T_DISPLAYNAME}0']")).to_be_visible()
 
    
    def test_leave_tournament(self, pages):
        tname=f"{T_NAME}0"
        
        # going to tournament page
        for page in pages:
            page.locator("#playMenuGoToTournament").click()
        expect(pages[0].locator("#createTournamentForm")).to_be_visible()
        
        create_tournament(pages[0], tournament_name=tname, n_players=8, points_to_win=1)
        join_tournament(pages[1], tournament_name=tname)
        
        # checking if the user is BACK on the join tournament page and the current_player_num is correctly updated
        leave_tournament(pages[0])
        expect(pages[0].locator(f"join-tournament-element[name='{tname}']").locator("[name='join_current_player_num']")).to_have_text("1")

        # checking if the current_player_num is correctly updated ON the tournament lobby page
        expect(pages[1].locator("#lobbyCurrentPlayerNum")).to_have_text("1")
        
        # checking if the join tournament element is removed from the lobby page when all players leave
        leave_tournament(pages[1])
        expect(pages[1].locator("#joinTournamentElements")).to_be_empty()


def change_slider_value(page, slider_selector, value):
    # Set the value of the slider
    page.eval_on_selector(slider_selector, f"el => el.value = {value}")
    # Dispatch the input event to simulate user interaction
    page.eval_on_selector(slider_selector, "el => el.dispatchEvent(new Event('input'))")
    # Dispatch the change event to ensure any change listeners are triggered
    page.eval_on_selector(slider_selector, "el => el.dispatchEvent(new Event('change'))")


def leave_tournament(page):
    page.locator("#lobbyLeaveButton").click()
    expect(page.locator("#createTournamentForm")).to_be_visible()


def join_tournament(page, tournament_name):
    """Joins a tournament with the given name and checks if the lobby page is visible.

    !!! page needs to be on the tournament page !!!"""
    expect(page.locator(f"join-tournament-element[name='{tournament_name}']")).to_be_visible()
    page.locator(f"join-tournament-element[name='{tournament_name}']").locator("button").click()
    expect(page.locator("tournament-lobby-page")).to_be_visible()


def create_tournament(page, tournament_name, n_players=4, points_to_win=5):
    """Creates a tournament with the given parameters and checks if the lobby page is visible.

    !!! page needs to be on the tournament page !!!"""
    page.locator("#createName").fill(tournament_name)
    
    if n_players == 4:
        page.locator("label[for='create4PlayerInput']").click()
    elif n_players == 8:
        page.locator("label[for='create8PlayerInput']").click()
    elif n_players == 16:
        page.locator("label[for='create16PlayerInput']").click()
    else:
        raise ValueError(f"Unsupported number of players: {n_players}")
    
    if 0 < points_to_win and points_to_win < 26:
        change_slider_value(page, "#createPointsToWin", points_to_win)
    else:    
        raise ValueError(f"Points to win must be between 1 and 25, got {points_to_win}")

    page.locator("#createTournamentButton").click()
    expect(page.locator("tournament-lobby-page")).to_be_visible()