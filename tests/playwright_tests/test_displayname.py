
from playwright.sync_api import expect
from playwright.sync_api import Page, sync_playwright, Browser, BrowserContext
from conftest import signup, login, set_display_name

class TestInputtingDisplayName:
    # closing the window after signup, and logging in to check if you still need to enter a display name
    def test_close_window_after_signup(self):
        with sync_playwright() as p:
            browser: Browser = p.chromium.launch() # only testing with one browser because we cant do signup with same user twice
            context: BrowserContext = browser.new_context(ignore_https_errors=True)
            page: Page = context.new_page()

            try:
                signup(page, "transcendence42vienna+displayname@gmail.com", "password", "password")
                page.wait_for_selector("#displayNameForm", timeout=5000)
                page.close()
                context.close()

                context = browser.new_context(ignore_https_errors=True)
                page: Page = context.new_page()

                login(page, "transcendence42vienna+displayname@gmail.com", "password")
                page.wait_for_selector("#displayNameForm", timeout=5000)
                set_display_name(page, "displayname")
                expect(page.locator("#navbar")).to_be_visible()
            except:
                print("Test doesnt work after executing it once, cuz we cant delete user from db, will be fixed later") # todo !!!
                expect(page.locator("#FAIL")).to_be_visible() # causing an intended failure
            
            finally:
                page.close()
                context.close()
                browser.close()

    # taking the same displayname as the test above to test if i can take it as well (i shouldn't be able to)
    def test_displayname_warnings(self, login_page: Page):
        try:
            signup(login_page, "transcendence42vienna+displayname2@gmail.com", "password", "password")
            expect(login_page.locator("#displayNameForm")).to_be_visible()

            # checking the empty displayname warning (not really a warning, but the form shouldn't be submittable) (the warning is from html(?))
            login_page.locator("#displayNameInput").fill("") # empty displayname
            login_page.locator("#displayNameSubmitButton").click()
            expect(login_page.locator("#displayNameForm")).to_be_visible()

            # maybe add a warning for this case later(?)(maybe)(not important)

            # checking that you can enter 20 characters max
            login_page.locator("#displayNameInput").fill("abcdefghijklmnopqrstuvwxyz") # displayname with too many characters
            expect(login_page.locator("#displayNameInput")).to_have_value("abcdefghijklmnopqrst")

            # checking the whitespace warning
            login_page.locator("#displayNameInput").fill("ee ee") # displayname with spaces
            login_page.locator("#displayNameSubmitButton").click()
            expect(login_page.locator("#displayNameWarning")).to_be_visible()
            expect(login_page.locator("#displayNameWarning")).to_have_text("Whitespaces are not allowed")

            # checking the taken displayname warning
            login_page.locator("#displayNameInput").fill("displayname") # same displayname as function above
            login_page.locator("#displayNameSubmitButton").click()
            expect(login_page.locator("#displayNameWarning")).to_be_visible()
            expect(login_page.locator("#displayNameWarning")).to_have_text("This displayname is already taken")

            # checking if the warning is gone after changing the displayname
            login_page.locator("#displayNameInput").fill("displayname2")
            expect(login_page.locator("#displayNameWarning")).to_be_hidden()
            login_page.locator("#displayNameSubmitButton").click()
            expect(login_page.locator("#navbar")).to_be_visible()
        except:
            print("Test doesnt work after executing it once, cuz we cant delete user from db, will be fixed later") # todo !!!
            expect(login_page.locator("#FAIL")).to_be_visible() # causing an intended failure


    







        
