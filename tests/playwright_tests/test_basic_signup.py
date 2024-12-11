from playwright.sync_api import Playwright, sync_playwright, expect
from conftest import delete_user, set_display_name, get_otp, BASE_URL


USERMAIL = "transcendence42vienna+basicsignup1@gmail.com"
USERPW = "Xz8RD3nqw1"
USERDISPLAYNAME = "basic_signup_1"

class TestBasicSignup:

    def test_signup_check_empty_fields(playwright: Playwright) -> None:
        with sync_playwright() as playwright:
            
            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
        
            try:
                page.goto(BASE_URL)
                page.click("#loginGoToSignup")

            # if nothing is filled, the submit buttons should be disabled
                expect(page.locator("#signupEmail")).to_be_empty()
                expect(page.locator("#signupPassword1")).to_be_empty()
                expect(page.locator("#signupPassword2")).to_be_empty()
                expect(page.locator("#signupSubmitButton")).to_be_disabled()

            # if email and pw1 are filled, the submit buttons should be disabled
                page.locator("#signupEmail").fill(USERMAIL)
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill("")
                expect(page.locator("#signupSubmitButton")).to_be_disabled()

            # if email and pw2 are filled, the submit buttons should be disaabled
                page.locator("#signupEmail").fill(USERMAIL)
                page.locator("#signupPassword1").fill("")
                page.locator("#signupPassword2").fill(USERPW)
                expect(page.locator("#signupSubmitButton")).to_be_disabled()

            # if pw1 and pw2 are filled, the submit buttons should be disaabled
                page.locator("#signupEmail").fill("")
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill(USERPW)
                expect(page.locator("#signupSubmitButton")).to_be_disabled()

            # if all fields are filled, signup should be disabled, otp should be enabled
                page.locator("#signupEmail").fill(USERMAIL)
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill(USERPW)
                expect(page.locator("#signupSubmitButton")).to_be_enabled()
                page.locator("#signupSubmitButton").click()

            # filling the otp should enable signup 
                otp = get_otp()
                page.wait_for_selector("#signupOtpCode", state="visible")
                page.locator("#signupOtpCode").fill(otp)
                expect(page.locator("#signupSubmitButton")).to_be_enabled()
                page.locator("#signupSubmitButton").click()
                
            # finishing the signup and deleting the user
                set_display_name(page, USERDISPLAYNAME)
                delete_user(page, USERPW)
            
            except:
                expect(page.locator("#FAIL")).to_be_visible(timeout=1) # causing an intended failure
            
            finally:
                context.close()
                browser.close()



    def test_signup_wrong_username(playwright: Playwright) -> None:
       
        with sync_playwright() as playwright:
            
            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
        
            try:
                page.goto(BASE_URL)
                page.click("#loginGoToSignup")
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill(USERPW)
            
                page.locator("#signupEmail").fill("wrongemail")
                expect(page.locator("#signupErrorMessageEmail")).to_be_visible()
                expect(page.locator("#signupErrorMessageEmail")).to_have_text("Invalid email address")
                
                page.locator("#signupEmail").fill("wrong@email")
                expect(page.locator("#signupErrorMessageEmail")).to_be_visible()
                expect(page.locator("#signupErrorMessageEmail")).to_have_text("Invalid email address")
                
                page.locator("#signupEmail").fill("wrongemail.at")
                expect(page.locator("#signupErrorMessageEmail")).to_be_visible()
                expect(page.locator("#signupErrorMessageEmail")).to_have_text("Invalid email address")
            
            except:
                expect(page.locator("#FAIL")).to_be_visible(timeout=1) # causing an intended failure
            
            finally:
                context.close()
                browser.close()
                  

    def test_signup_password_mismatch(playwright: Playwright) -> None:
       
        with sync_playwright() as playwright:
            
            browser = playwright.chromium.launch()
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()
        
            try:
                page.goto(BASE_URL)
                page.click("#loginGoToSignup")
                page.locator("#signupEmail").fill(USERMAIL)
                page.locator("#signupPassword1").fill(USERPW)
                page.locator("#signupPassword2").fill(USERPW + "1")
                expect(page.locator("#signupErrorMessagePassword")).to_be_visible()
                expect(page.locator("#signupErrorMessagePassword")).to_have_text("Passwords don't match")
            
            except:
                expect(page.locator("#FAIL")).to_be_visible(timeout=1)
        
            finally:        
                context.close()
                browser.close()


