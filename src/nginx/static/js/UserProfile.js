import { ComponentBaseClass } from './componentBaseClass.js';

export class UserProfile extends ComponentBaseClass {
    constructor() {
        super();
        //done to check on visibility of the element
        this.observer = new IntersectionObserver(this.handleVisibilityChange.bind(this), {
            root: null,
            threshold: 0.1
        });
    }

    // Update the getElementHTML method to include a spinner
    getElementHTML() {
        const template = document.createElement('template');
        template.innerHTML = `
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
      <style>
      .form-container {
        padding: 1rem;
        width: 100vw;
        max-width: 400px;
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
        height: auto;
        cursor: pointer;
        display: block;
        margin: 0 auto 1rem;
        border-radius: 50%;
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
      <div class="form-container bg-dark text-white">
        <img src="https://i.pravatar.cc/150?img=52" class="profile-image" id="profileImage" alt="Profile Image">
        <div id="imageWarning" class="mt-2"></div>
        <input type="file" id="imageUpload" style="display: none;">
        <form id="profileForm">
          <div class="mb-3">
            <label for="displayName" class="form-label">Display Name</label>
            <input type="text" class="form-control" id="displayName">
          </div>
          <div class="mb-3">
            <label for="email" class="form-label">Email address</label>
            <input type="email" class="form-control" id="email" disabled readonly>
          </div>
          <button type="button" class="btn btn-primary" id="saveProfile">Save</button>
          <div class="spinner-border text-light" role="status" id="saveProfileSpinner">
            <span class="visually-hidden">Loading...</span>
          </div>
        </form>
        <hr>
        <form id="passwordForm">
          <div class="mb-3 input-group">
            <label for="oldPassword" class="form-label">Old Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="oldPassword">
              <span class="input-group-text" id="oldPasswordToggle">Show</span>
            </div>
          </div>
          <div class="mb-3 input-group">
            <label for="newPassword" class="form-label">New Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="newPassword">
              <span class="input-group-text" id="newPasswordToggle">Show</span>
            </div>
          </div>
          <div class="mb-3">
            <label for="confirmPassword" class="form-label">Confirm New Password</label>
            <div class="input-group">
              <input type="password" class="form-control" id="confirmPassword">
              <span class="input-group-text" id="confirmPasswordToggle">Show</span>
            </div>
            <div class="warning-message" id="passwordWarning">Passwords do not match</div>
          </div>
          <button type="button" class="btn btn-primary" id="changePassword" disabled>Change Password</button>
          <div class="spinner-border text-light" role="status" id="changePasswordSpinner">
            <span class="visually-hidden">Loading...</span>
          </div>
        </form>
      </div>
    `;
        return template;
    }

    connectedCallback() {
        super.connectedCallback();
        this.shadowRoot.getElementById('saveProfile').addEventListener('click', this.saveProfile.bind(this));
        this.shadowRoot.getElementById('changePassword').addEventListener('click', this.changePassword.bind(this));
        this.shadowRoot.getElementById('newPassword').addEventListener('input', this.validatePasswords.bind(this));
        this.shadowRoot.getElementById('confirmPassword').addEventListener('input', this.validatePasswords.bind(this));
        this.shadowRoot.getElementById('profileImage').addEventListener('click', () => this.shadowRoot.getElementById('imageUpload').click());
        this.shadowRoot.getElementById('imageUpload').addEventListener('change', this.handleImageUpload.bind(this));
        this.shadowRoot.getElementById('oldPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('oldPassword', 'oldPasswordToggle'));
        this.shadowRoot.getElementById('newPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('newPassword', 'newPasswordToggle'));
        this.shadowRoot.getElementById('confirmPasswordToggle').addEventListener('click', () => this.togglePasswordVisibility('confirmPassword', 'confirmPasswordToggle'));

        this.shadowRoot.addEventListener('click', (event) => {
            event.stopPropagation();
        });
        this.observer.observe(this);
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

    handleVisibilityChange(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadUserData();
            }
        });
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        this.observer.unobserve(this);
    }

     async loadUserData() {
        try {
            // Fetch user data from global app object or API
            const response = await this.apiFetch('/um/profile', { method: 'GET', cache: 'no-store' });
            this.shadowRoot.getElementById('displayName').value = response.displayname;
            //this.shadowRoot.getElementById('email').value = userData.email;

            // Check if the image URL is reachable
            const imageUrl = response.image;
            const image = new Image();
            image.onload = () => {
                this.shadowRoot.getElementById('profileImage').src = imageUrl;
            };
            image.onerror = () => {
                this.shadowRoot.getElementById('profileImage').src = 'https://i.pravatar.cc/300';
            };
            image.src = imageUrl;
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    }

    handleImageUpload(event) {
        const file = event.target.files[0];
        const allowedTypes = ['image/jpeg', 'image/png'];
        const maxSize = 1024 * 1024; // 1MB
        console.log('Image selected:', file);

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
                this.selectedImage = file;
            };
            //TODO: Add API call to upload image, use base64 string to transmit
            reader.readAsDataURL(file);
        }
    }

    async saveProfile() {
        const saveButton = this.shadowRoot.getElementById('saveProfile');
        const saveSpinner = this.shadowRoot.getElementById('saveProfileSpinner');
        saveButton.disabled = true;
        saveSpinner.style.display = 'inline-block';

        const displayName = this.shadowRoot.getElementById('displayName').value;
        const profileImage = this.selectedImage;

        // Simulate API call, can be removed later
        //await new Promise(resolve => setTimeout(resolve, 500));

        const formData = new FormData();
        formData.append('displayName', displayName);
        if (profileImage) {
            formData.append('profileImage', profileImage);
        }

        try {
            await this.apiFetch('/um/profile', {method: 'PATCH', body: formData});
            console.log('Profile saved: ', formData);
        } catch (error) {
            console.error('Error saving profile:', error);
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
        changeButton.disabled = true;
        changeSpinner.style.display = 'inline-block';

        const oldPassword = this.shadowRoot.getElementById('oldPassword').value;
        const newPassword = this.shadowRoot.getElementById('newPassword').value;
        const confirmPassword = this.shadowRoot.getElementById('confirmPassword').value;
        if (newPassword !== confirmPassword) {
            return;
        }

        // Simulate API call, can be removed later
        //await new Promise(resolve => setTimeout(resolve, 500));
        try {
            await this.apiFetch("/registration/change_password", {method: "POST", body: JSON.stringify({"current_password": oldPassword, "new_password": newPassword})});
            console.log('Changed password');
        } catch (error) {
            console.error('Error changing password: ', error);
        }

        changeButton.disabled = false;
        changeSpinner.style.display = 'none';
    }
}

customElements.define('user-profile', UserProfile);