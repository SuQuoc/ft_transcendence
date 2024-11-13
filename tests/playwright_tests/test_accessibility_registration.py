from playwright.sync_api import Playwright, sync_playwright, expect
from conftest import delete_user, set_display_name, get_otp, BASE_URL
import re

USERMAIL = "transcendence42vienna+accessibility2@gmail.com"
USERPW = "r8tA9JVquw"
NEWUSERPW = "cmR8AqIw03"
USERDISPLAYNAME = "accessibility2"

class TestAccessibility:

    def test_signup(playwright: Playwright) -> None:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
                page.goto(BASE_URL) 
                page.locator("#loginGoToSignup").press("Enter")
            # [aguilmea] we cannot press enter and have to clikc on the link
                page.locator("#loginGoToSignup").click()
                page.locator("#loginWith42").press("Enter")
                expect(page).to_have_url(re.compile("https://auth.42.fr/*"))

                page.goto(BASE_URL)
                page.locator("#loginGoToSignup").click()
                page.locator("#signupGoToLogin").press("Enter")
                expect(page.locator("#loginForm")).to_be_visible()

                page.goto(BASE_URL)
                page.locator("#loginGoToSignup").click()
                page.locator("#signupEmail").fill(USERMAIL)
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill(USERPW)
                page.locator("#signupSubmitButton").press("Enter")
                otp = get_otp()
                page.wait_for_selector("#otpCode", state="visible")
                page.locator("#otpCode").fill(otp)
                expect(page.locator("#signupSubmitButton")).to_be_enabled()
                page.locator("#signupSubmitButton").press("Enter")
                set_display_name(page, USERDISPLAYNAME)
                delete_user(page, USERPW)
            
            except:
                expect(page.locator("#FAIL")).to_be_visible() # causing an intended failure

            finally:
                context.close()
                browser.close()

    def test_forgot_password(playwright: Playwright) -> None:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
    
                page.goto(BASE_URL)
                page.locator("#loginGoToSignup").click()
                page.locator("#forgotPassword").press("Enter")
                expect(page.locator("#forgotPasswordForm")).to_be_visible()
                page.locator("#resetEmail").fill(USERMAIL)
                page.locator("#requestOTP").press("Enter")
                otp = get_otp()
                page.wait_for_selector("#otpCode", state="visible")
                page.locator("#otpCode").fill(otp)
                page.locator("#newPassword1").fill(NEWUSERPW)
                page.locator("#newPassword2").fill(NEWUSERPW)
                page.locator("#resetSubmitButton").press("Enter")
                expect(page.locator("#loginForm")).to_be_visible()
            
            except:
                expect(page.locator("#FAIL")).to_be_visible()

            finally:
                context.close()
                browser.close()

    def test_login(playwright: Playwright) -> None:
        with sync_playwright() as playwright:

            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
    
                page.goto(BASE_URL)
                page.locator("#loginEmail").fill(USERMAIL)
                page.locator("#loginPassword").fill(NEWUSERPW)
                page.locator("#loginSubmitButton").press("Enter")
                otp = get_otp()
                page.wait_for_selector("#otpCode", state="visible")
                page.locator("#otpCode").fill(otp)
                page.locator("#loginSubmitButton").press("Enter")
                expect(page.locator("#mainContent")).to_be_visible()
            
            except:
                expect(page.locator("#FAIL")).to_be_visible()

            finally:
                context.close()
                browser.close()
