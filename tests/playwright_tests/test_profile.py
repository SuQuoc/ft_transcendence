
from playwright.sync_api import expect
from playwright.sync_api import Page
from conftest import login, USERMAIL, USERPW, USERDISPLAYNAME


USER_NEWNAME = "newName"
USER_NEWMAIL = "transcendence42vienna+newmail@gmail.com"
USER_NEWPW = "PEvv8uCbpA"

class TestProfile:
    def test_user_profile_dropdown(self, page: Page):
        page.locator("#userDropdown").click()
        expect(page.locator("#displayName")).to_be_visible()
    
    def test_userdata_present(self, page: Page):
        page.locator("#userDropdown").click()
        
        profile_form_loc = page.locator("#profileForm")
        displayname_loc = page.locator("#displayName")
        email_loc = page.locator("#email")

        expect(profile_form_loc).to_be_visible() 
        expect(displayname_loc).to_have_value(USERDISPLAYNAME)
        """ expect(email_loc).to_have_value(USERMAIL) """ # todo !!! - email is not displayed in profile dropdown when u are logged in and open a new tab


    def test_userdata_present_after_login(self, login_page: Page):
        login(login_page, USERMAIL, USERPW)
        login_page.locator("#userDropdown").click()

        profile_form_loc = login_page.locator("#profileForm")
        displayname_loc = login_page.locator("#displayName")
        email_loc = login_page.locator("#email")

        expect(profile_form_loc).to_be_visible() 
        expect(displayname_loc).to_have_value(USERDISPLAYNAME)
        expect(email_loc).to_have_value(USERMAIL)


    # test is wrong, because it doesn't work in our program yet
    """ def test_displayname_change(self, page: Page):
        page.locator("#userDropdown").click()
        page.locator("#displayName").fill(USER_NEWNAME)
        page.locator("#saveProfile").click()

        page.locator("#userDropdown").click()
        page.locator("#userDropdown").click()

        expect(page.locator("#displayName")).to_have_value(USER_NEWNAME)
        # todo !!! - logout and login again to check new displayname """


    """ def test_email_change(self, page: Page):
        page.locator("#userDropdown").click()
        page.locator("#email").fill(USER_NEWMAIL)
        page.locator("#saveProfile").click()

        page.locator("#userDropdown").click()
        page.locator("#userDropdown").click()

        expect(page.locator("#email")).to_have_value(USER_NEWMAIL)
        # todo !!! - logout and login again to check new displayname """


    def test_image_change(self, page: Page):
        """ page.locator("#userDropdown").click()
        page.locator("#profileImage").click()
        page.locator("#imageInput").fill() """



    def test_password_change(self, page: Page):
        page.locator("#userDropdown").click()
        page.locator("#oldPassword").fill(USERPW)
        page.locator("#newPassword").fill(USER_NEWPW)
        page.locator("#confirmPassword").fill(USER_NEWPW)
        page.locator("#changePassword").click()

        """  
        # logout
        login(page, USERMAIL, USER_NEWPW)
        """

        



# def test_friend_page(page: Page):
#    test_login(page)
#    page.goto(BASE_URL)
