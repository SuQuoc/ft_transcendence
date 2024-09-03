import re

from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import expect
from playwright.sync_api import Page
from playwright.sync_api import sync_playwright
import pytest

BASE_URL = "https://localhost:8000"


def test_profile(page, login):
    page.locator("#profileButton").click()


# def test_friend_page(page: Page):
#    test_login(page)
#    page.goto(BASE_URL)
