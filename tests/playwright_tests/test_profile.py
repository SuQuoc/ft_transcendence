import re

from conftest import BASE_URL
from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import pytest


class TestProfile:
    def test_user_profile_dropdown(self, page: Page):

        page.locator("#userDropdown").click()
        expect(page.locator("#displayName")).to_be_visible()


# def test_friend_page(page: Page):
#    test_login(page)
#    page.goto(BASE_URL)
