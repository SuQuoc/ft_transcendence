import { ComponentBaseClass } from './componentBaseClass.js';

export class UserProfile extends ComponentBaseClass {
    // Update the getElementHTML method to include a spinner
    getElementHTML() {
        const template = document.createElement('template');
        template.innerHTML = `
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
      <style>
      .form-container {
        padding: 1rem;
        width: 100vw;
        max-width: 100%;
      }
      .form-container form {
        margin-bottom: 1rem;
      }
      .form-container button {
        width: 100%;
      }
      .profile-image {
        width: 100%;
        max-width: 150px;
        max-height: 150px;
        cursor: pointer;
        display: block;
        margin: 0 auto 1rem;
        border-radius: 50%;
        object-fit: cover;
        object-position: center;
      }
      .warning {
        border-color: red;
      }
      .warning-message {
        color: red;
        display: none;
      }
      .spinner-border {
        display: none;
        width: 1rem;
        height: 1rem;
        border-width: 0.2em;
      }
    </style>
    <div class="form-container text-white" style="background-color: var(--custom-bg-color); border-radius: 6px;">
    <div id="userManagement">
        <img src="/media_url/profile_images/default_avatar.png" class="profile-image" id="profileImage" alt="Profile Image" onerror='this.src = "/media_url/profile_images/default_avatar.png"'>
        <div id="imageWarning" class="mt-2"></div>
        <input type="file" id="imageUpload" style="display: none;">
        <form id="profileForm">
          <div class="mb-3">
            <label for="displayName" class="form-label">Display Name</label>
            <input type="text" class="form-control" id="displayName" maxlength="20">
            <div class="warning-message" id="profileDisplayNameWarning">Error changing display name</div>
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="email" disabled readonly>
          </div>
          <button type="submit" class="btn btn-primary" id="saveProfile">Save</button>
          <div class="spinner-border text-light" role="status" id="saveProfileSpinner">
            <span class="visually-hidden">Loading...</span>
          </div>
        </form>
        <hr>
        <form id="passwordForm">
          <div class="mb-3 input-group">
            <label for="oldPassword" class="form-label">Old Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="oldPassword" name="current-password" autocomplete="current-password">
              <span class="input-group-text" id="oldPasswordToggle">Show</span>
            </div>
          </div>
          <div class="mb-3 input-group">
            <label for="newPassword" class="form-label">New Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="newPassword" name="new-password" autocomplete="new-password">
              <span class="input-group-text" id="newPasswordToggle">Show</span>
            </div>
          </div>
          <div class="mb-3">
            <label for="confirmPassword" class="form-label">Confirm New Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="confirmPassword" name="new-password-confirm" autocomplete="new-password">
              <span class="input-group-text" id="confirmPasswordToggle">Show</span>
            </div>
            <div class="warning-message" id="passwordWarning">Passwords do not match</div>
            <div class="warning-message" id="changePasswordWarning">Error changing password</div>
          </div>
          <button type="submit" class="btn btn-primary" id="changePassword" disabled>Change Password</button>
          <div class="spinner-border text-light" role="status" id="changePasswordSpinner">
            <span class="visually-hidden">Loading...</span>
          </div>
        </form>
        <hr>
        <button type="button" class="btn btn-secondary mt-3" id="logoutButton" aria-label="Logout">Logout</button>
        </div>
        <button type="button" class="btn btn-danger mt-3" id="deleteUserButton" aria-label="Delete User">Delete User</button>
        <div id="deleteUserConfirmation" style="display: none;">
            <div class="mb-3" id="passwordSection">
                <label for="deleteUserPassword" class="form-label">Enter Current Password</label>
                <input type="password" class="form-control" id="deleteUserPassword" placeholder="Current password" aria-placeholder="Current Password">
            </div>
            <button type="button" class="btn btn-primary" id="requestDeleteUserButton">Delete User</button>
            <div class="mb-3" id="otpSection" style="display: none;">
                <label for="deleteUserOTP" class="form-label">Enter OTP</label>
                <input type="text" class="form-control" id="deleteUserOTP" placeholder="OTP" aria-placeholder="OTP" maxlength="16">
            </div>
            <button type="button" class="btn btn-danger" id="confirmDeleteUserButton" style="display: none;">Really? Action can't be undone</button>
        </div>
      </div>
    `;
        return template;
    }

    connectedCallback() {
        super.connectedCallback();
        this.loadUserData();
        this.shadowRoot.getElementById('saveProfile').addEventListener('click', this.saveProfile.bind(this));
        this.shadowRoot.getElementById('changePassword').addEventListener('click', this.changePassword.bind(this));
        this.shadowRoot.getElementById('newPassword').addEventListener('input', this.validatePasswords.bind(this));
        this.shadowRoot.getElementById('confirmPassword').addEventListener('input', this.validatePasswords.bind(this));
        this.shadowRoot.getElementById('profileImage').addEventListener('click', () => this.shadowRoot.getElementById('imageUpload').click());
        this.shadowRoot.getElementById('imageUpload').addEventListener('change', this.handleImageUpload.bind(this));
        this.shadowRoot.getElementById('oldPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('oldPassword', 'oldPasswordToggle'));
        this.shadowRoot.getElementById('newPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('newPassword', 'newPasswordToggle'));
        this.shadowRoot.getElementById('confirmPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('confirmPassword', 'confirmPasswordToggle'));
        this.shadowRoot.getElementById('logoutButton').addEventListener('click', this.handleLogout.bind(this));
        this.shadowRoot.getElementById('deleteUserButton').addEventListener('click', this.handleDeleteUser.bind(this));
    }

    /**
     * Temporary function for deleting a user, should be replaced with a single API call to /registration/delete_user
     * @returns {Promise<void>}
     */
    async handleDeleteUser() {
        const userManagement = this.shadowRoot.getElementById('userManagement');
        const deleteUserConfirmation = this.shadowRoot.getElementById('deleteUserConfirmation');
        const deleteUserButton = this.shadowRoot.getElementById('deleteUserButton');

        const requestOTPButton = this.shadowRoot.getElementById('requestDeleteUserButton');
        const confirmDeleteUserButton = this.shadowRoot.getElementById('confirmDeleteUserButton');

        const deleteUserPassword = this.shadowRoot.getElementById('deleteUserPassword');
        const otpSection = this.shadowRoot.getElementById('otpSection');
        const passwordSection = this.shadowRoot.getElementById('passwordSection');

        if (deleteUserConfirmation.style.display === 'none') {
            deleteUserConfirmation.style.display = 'block';
            userManagement.style.display = 'none';
            deleteUserButton.textContent = 'Cancel';
            otpSection.style.display = 'none';
            passwordSection.style.display = 'block';
        } else {
            deleteUserConfirmation.style.display = 'none';
            userManagement.style.display = 'block';
            deleteUserButton.textContent = 'Delete User';
            otpSection.style.display = 'none';
            requestOTPButton.style.display = 'block';
            confirmDeleteUserButton.style.display = 'none';
        }

        //TODO: take event handlers out of the function
        requestOTPButton.addEventListener('click', async () => {
            const password = deleteUserPassword.value;
            password ? deleteUserPassword.classList.remove('warning') : deleteUserPassword.classList.add('warning');

            try {
                await this.apiFetch('/registration/delete_user', { method: 'POST', body: JSON.stringify({ password: password }) });
                otpSection.style.display = 'block';
                passwordSection.style.display = 'none';
                requestOTPButton.style.display = 'none';
                confirmDeleteUserButton.style.display = 'block';
            } catch (error) {
                console.error('Error requesting OTP:', error);
            }
        });

        confirmDeleteUserButton.addEventListener('click', async () => {
            const password = deleteUserPassword.value;
            const otp = this.shadowRoot.getElementById('deleteUserOTP').value;

            password ? deleteUserPassword.classList.remove('warning') : deleteUserPassword.classList.add('warning');
            otp ? this.shadowRoot.getElementById('deleteUserOTP').classList.remove('warning') : this.shadowRoot.getElementById('deleteUserOTP').classList.add('warning');
            if (!password || !otp) return;

            try {
                await this.apiFetch('/registration/delete_user', { method: 'POST', body: JSON.stringify({ password: password, otp: otp }) });
                console.log('User deleted');
                await window.app.router.go('/login', true);
            } catch (error) {
                console.error('Error deleting user:', error);
            }
        });
    }

    async handleLogout() {
        await fetch('/registration/logout', { method: 'GET' })
            .then(() => {
                window.localStorage.removeItem("oauthCode");
				window.localStorage.removeItem("oauthState");
                window.app.router.go('/login', true);
            })
            .catch((error) => {
                console.error('Error logging out:', error);
            });
    }

    togglePasswordVisibility(passwordFieldId, toggleButtonId) {
        const passwordField = this.shadowRoot.getElementById(passwordFieldId);
        const toggleButton = this.shadowRoot.getElementById(toggleButtonId);
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            toggleButton.textContent = 'Hide';
        } else {
            passwordField.type = 'password';
            toggleButton.textContent = 'Show';
        }
    }

    async loadUserData() {
        try {
            // Fetch user data from global app object or API
            const response = await this.apiFetch('/um/profile', { method: 'GET', cache: 'no-store' });
            if ('displayname' in response) {
                window.app.userData.username = response.displayname;
                this.shadowRoot.getElementById('displayName').value = window.app.userData.username;
            }
            if ('image' in response) {
                window.app.userData.profileImage = response.image;
                this.shadowRoot.getElementById('profileImage').src = window.app.userData.profileImage;
            }
            if (!window.app.userData.email) {
                console.log('Email not found in global app object, fetching from API');
                const email_response = await this.apiFetch('/registration/get_email', { method: 'GET', cache: 'no-store' });
                window.app.userData.email = email_response.email;
            }
            this.shadowRoot.getElementById('email').value = window.app.userData.email;
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    async handleImageUpload(event) {
        const file = event.target.files[0];
        const allowedTypes = ['image/jpeg', 'image/png'];
        const maxSize = 1024 * 1024; // 1MB

        const warningMessage = this.shadowRoot.getElementById('imageWarning');
        warningMessage.textContent = '';
        warningMessage.classList.remove('alert', 'alert-danger');

        if (file) {
            if (!allowedTypes.includes(file.type)) {
                warningMessage.textContent = 'Only JPEG and PNG files are allowed.';
                warningMessage.classList.add('alert', 'alert-danger');
                return;
            }

            if (file.size > maxSize) {
                warningMessage.textContent = 'File size must be less than 1MB.';
                warningMessage.classList.add('alert', 'alert-danger');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                this.shadowRoot.getElementById('profileImage').src = e.target.result;
                window.app.userData.profileImage = e.target.result;
            };
            const formData = new FormData();
            formData.append('image', file);
            try {
                await this.apiFetch('/um/profile', { method: 'PATCH', body: formData }, 'multipart/form-data');
                reader.readAsDataURL(file);
            } catch {
                warningMessage.textContent = 'Error uploading image.';
                warningMessage.classList.add('alert', 'alert-danger');
            }
        }
    }

    async saveProfile() {
        const saveButton = this.shadowRoot.getElementById('saveProfile');
        const saveSpinner = this.shadowRoot.getElementById('saveProfileSpinner');
        const profileDisplayNameWarning = this.shadowRoot.getElementById('profileDisplayNameWarning');
        saveButton.disabled = true;
        saveSpinner.style.display = 'inline-block';
        profileDisplayNameWarning.style.display = 'none';

        const displayName = this.shadowRoot.getElementById('displayName').value;
        const imageUpload = this.shadowRoot.getElementById('imageUpload');
        const formData = new FormData();
        formData.append('displayname', displayName);

        if (imageUpload.files.length > 0) {
            const imageFile = imageUpload.files[0];
            formData.append('image', imageFile);
        }

        try {
            const response = await this.apiFetch('/um/profile', {method: 'PATCH', body: formData}, 'multipart/form-data');
            window.app.userData.username = response.displayname;
            window.app.userData.profileImage = response.image;
            console.log('Profile saved');
        } catch (error) {
            console.error('Error saving profile:', error);
            profileDisplayNameWarning.style.display = 'block';
        }

        saveButton.disabled = false;
        saveSpinner.style.display = 'none';
    }

    validatePasswords() {
        const newPassword = this.shadowRoot.getElementById('newPassword').value;
        const confirmPassword = this.shadowRoot.getElementById('confirmPassword').value;
        const changePasswordButton = this.shadowRoot.getElementById('changePassword');
        const passwordWarning = this.shadowRoot.getElementById('passwordWarning');

        if (newPassword !== confirmPassword) {
            this.shadowRoot.getElementById('newPassword').classList.add('warning');
            this.shadowRoot.getElementById('confirmPassword').classList.add('warning');
            passwordWarning.style.display = 'block';
            changePasswordButton.disabled = true;
        } else {
            this.shadowRoot.getElementById('newPassword').classList.remove('warning');
            this.shadowRoot.getElementById('confirmPassword').classList.remove('warning');
            passwordWarning.style.display = 'none';
            changePasswordButton.disabled = false;
        }
    }

    // Update the changePassword method to show/hide the spinner and disable/enable the button
    async changePassword() {
        const changeButton = this.shadowRoot.getElementById('changePassword');
        const changeSpinner = this.shadowRoot.getElementById('changePasswordSpinner');
        const changePasswordWarning = this.shadowRoot.getElementById('changePasswordWarning');
        changeButton.disabled = true;
        changeSpinner.style.display = 'inline-block';
        changePasswordWarning.style.display = 'none';

        const oldPassword = this.shadowRoot.getElementById('oldPassword').value;
        const newPassword = this.shadowRoot.getElementById('newPassword').value;
        const confirmPassword = this.shadowRoot.getElementById('confirmPassword').value;
        if (newPassword !== confirmPassword) {
            return;
        }

        try {
            await this.apiFetch("/registration/change_password", {method: "POST", body: JSON.stringify({"current_password": oldPassword, "new_password": newPassword})});
            this.shadowRoot.getElementById('oldPassword').value = '';
            this.shadowRoot.getElementById('newPassword').value = '';
            this.shadowRoot.getElementById('confirmPassword').value = '';
            console.log('Changed password');
        } catch (error) {
            console.error('Error changing password: ', error);
            changePasswordWarning.style.display = 'block';
        }

        changeButton.disabled = false;
        changeSpinner.style.display = 'none';
    }
}

customElements.define('user-profile', UserProfile);