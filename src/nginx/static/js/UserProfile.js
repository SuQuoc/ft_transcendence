import { ComponentBaseClass } from "./componentBaseClass.js";

export class UserProfile extends ComponentBaseClass {
	// Update the getElementHTML method to include a spinner
	getElementHTML() {
		const template = document.createElement("template");
		template.innerHTML = `
		<scripts-and-styles></scripts-and-styles>
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
				width: 150px;
				height: 150px;
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
				<img src="/media_url/profile_images/default_avatar.png" class="profile-image" id="profileImage" alt="Profile Image" onerror='this.src = "/media_url/profile_images/default_avatar.png"' tabindex="0">
				<div id="imageWarning" class="mt-2"></div>
				<input type="file" id="imageUpload" style="display: none;">
				<form id="profileForm">
					<div class="mb-3">
						<label for="displayName" class="form-label">Display Name</label>
						<div class="input-group mb-3">
							<input type="text" class="form-control" id="displayName" minlength="1" maxlength="20" pattern="[A-Za-z0-9\\-_]{1,20}" disabled>
							<span class="input-group-text btn btn-custom" id="changeDisplayNameButton" tabindex="0">Change</span>
						</div>
						<div class="warning-message" id="profileDisplayNameWarning">Error changing display name</div>
					</div>
					<div class="mb-3">
						<label for="email" class="form-label">Email address</label>
						<div class="input-group">
							<input type="email" class="form-control" id="email" disabled>
							<span id="changeEmailButton" class="input-group-text btn btn-custom" tabindex="0">Change</span>
						</div>
						<span class="warning-message" id="emailWarning" style="display:none;">Choose a different Email address</span>
						<div id="oldEmailContainer" hidden>
							<div class="form-check form-switch mt-3">
  								<input class="form-check-input" type="checkbox" role="switch" id="changeUsernameSwitchBackupCode">
  								<label class="form-check-label text-white" for="changeUsernameSwitchBackupCode" tabindex="0">No access to email? Use backup code instead</label>
							</div>
							<label for="oldEmailOTP" class="form-label">OTP sent to old E-Mail</label>
							<div class="input-group">
								<input type="text" class="form-control" id="oldEmailOTP" pattern="[0-9A-Za-z]{16}" minlength="16" maxlength="16">
								<span class="input-group-text btn btn-custom" id="requestOldEmailOTP" tabindex="0">New OTP</span>
							</div>
						</div>
						<div id="newEmailContainer" hidden>
							<label for="newEmailOTP" class="form-label mt-3">OTP sent to new E-Mail</label>
							<div class="input-group">
								<input type="text" class="form-control" id="newEmailOTP" pattern="[0-9A-Za-z]{16}" minlength="16" maxlength="16">
								<span class="input-group-text btn btn-custom" id="requestNewEmailOTP" tabindex="0">New OTP</span>
							</div>
							<div class="d-flex justify-content-between">
    							<button type="submit" class="btn btn-custom mt-3 me-2" id="saveNewEmailButton" disabled>Change Email</button>
    							<button type="button" class="btn btn-secondary mt-3" id="cancelEmailButton" tabindex="0">Cancel</button>
							</div>
						</div>
					</div>
				</form>
				<hr>
				<div id="passwordForm">
					<div class="mb-3 input-group" id="oldPasswordContainer">
						<label for="oldPassword" class="form-label">Old Password</label>
						<div class="input-group">
							<input type="password" class="form-control" id="oldPassword" name="current-password" autocomplete="current-password">
							<span class="input-group-text btn btn-custom" id="oldPasswordToggle" tabindex="0">Show</span>
						</div>
					</div>
					<div class="mb-3 input-group" id="newPasswordContainer">
						<label for="newPassword" class="form-label">New Password</label>
						<div class="input-group">
							<input type="password" class="form-control" id="newPassword" name="new-password" autocomplete="new-password">
							<span class="input-group-text btn btn-custom" id="newPasswordToggle" tabindex="0">Show</span>
						</div>
					</div>
					<div class="mb-3" id="confirmPasswordContainer">
						<label for="confirmPassword" class="form-label">Confirm New Password</label>
						<div class="input-group">
							<input type="password" class="form-control" id="confirmPassword" name="new-password-confirm" autocomplete="new-password">
							<span class="input-group-text btn btn-custom" id="confirmPasswordToggle" tabindex="0">Show</span>
						</div>
					</div>
					<div class="mb-3" id="newPasswordOTPContainer" hidden>
						<label for="newPasswordOTP" class="form-label">OTP sent to E-Mail</label>
						<div class="input-group">
							<input type="text" class="form-control" id="newPasswordOTP" pattern="[0-9A-Za-z]{16}" minlength="16" maxlength="16">
							<span class="input-group-text btn btn-custom" id="requestNewEmailOTP" tabindex="0">New OTP</span>
						</div>
					</div>
				</div>
				<div id="changePasswordOTPSection" class="d-none mb-3">
					<label for="changePasswordOTP" class="form-label">Enter OTP</label>
					<div class="input-group">
						<input type="text" class="form-control" id="changePasswordOTP" placeholder="OTP" aria-placeholder="OTP" maxlength="16" pattern="[0-9A-Za-z]{16}">
						<span class="input-group-text btn btn-custom" id="changePasswordRequestOTP" tabindex="0">New OTP</span>
					</div>
					<button type="button" class="btn btn-danger mt-3" id="changePasswordOTPCancel">Cancel</button>
				</div>
				<button type="submit" class="btn btn-custom" id="changePassword" disabled>Change Password</button>
				<div class="warning-message" id="changePasswordWarning">Error changing password</div>
				<hr>
				<label for="changeFontSize" class="form-label">Change Font Size</label>
				<div class="btn-group w-100" id="changeFontSize">
					<a href="#" class="btn btn-custom" onclick="document.documentElement.style.setProperty('--bs-font-size-base', '1rem');">Regular</a>
					<a href="#" class="btn btn-custom" onclick="document.documentElement.style.setProperty('--bs-font-size-base', '1.1rem');">Large</a>
					<a href="#" class="btn btn-custom" onclick="document.documentElement.style.setProperty('--bs-font-size-base', '1.2rem');">Extra-large</a>
				</div>
				<hr>
				<button type="button" class="btn btn-secondary mt-3" id="logoutButton" aria-label="Logout">Logout</button>
			</div>
			<button type="button" class="btn btn-danger mt-3" id="deleteUserButton" aria-label="Delete User">Delete User</button>
			<div id="deleteUserConfirmation" style="display: none;">
				<div class="mb-3" id="passwordSection">
					<label for="deleteUserPassword" class="form-label">Enter Current Password</label>
					<input type="password" class="form-control" id="deleteUserPassword" placeholder="Current password" aria-placeholder="Current Password">
				</div>
				<button type="button" class="btn btn-custom" id="requestDeleteUserButton">Delete User</button>
				<div class="mb-3" id="otpSection" style="display: none;">
					<label for="deleteUserOTP" class="form-label">Enter OTP</label>
					<input type="text" class="form-control" id="deleteUserOTP" placeholder="OTP" aria-placeholder="OTP" maxlength="16">
				</div>
				<button type="button" class="btn btn-danger" id="confirmDeleteUserButton" style="display: none;">Really? Action can't be undone</button>
				<div class="alert alert-danger d-none mt-3" role="alert" id="deleteError" aria-live="polite">
					<i class="bi bi-exclamation-triangle-fill me-2"></i>
					<span class="error-message"></span>
				</div>
			</div>
		</div>
    `;
		return template;
	}

	connectedCallback() {
		this.loadUserData();
		switch (document.documentElement.style.getPropertyValue("--bs-font-size-base")) {
			case "1.1rem":
				this.shadowRoot.getElementById("changeFontSize").querySelectorAll("a")[1].classList.add("active");
				break;
			case "1.2rem":
				this.shadowRoot.getElementById("changeFontSize").querySelectorAll("a")[2].classList.add("active");
				break;
			default:
				this.shadowRoot.getElementById("changeFontSize").querySelector("a").classList.add("active");
		}
		this.addMultipleEventListeners(["oldPassword", "newPassword", "confirmPassword"], ["input"], this.validatePasswords.bind(this));
		this.addMultipleEventListeners(["changeDisplayNameButton"], ["click", "keydown"], (event) => this.toggleDisplayname(event));
		this.addMultipleEventListeners(["changePassword"], ["click", "keydown"], (event) => this.changePassword(event));
		this.addMultipleEventListeners(["profileImage"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.shadowRoot.getElementById("imageUpload").click()});
		this.addMultipleEventListeners(["imageUpload"], ["change"], this.handleImageUpload.bind(this));
		this.addMultipleEventListeners(["changeEmailButton"], ["click", "keydown"], (event) => this.emailChange(event));
		this.addMultipleEventListeners(["oldEmailOTP", "newEmailOTP"], ["input"], this.emailValidateOTP.bind(this));
		this.addMultipleEventListeners(["oldPasswordToggle"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.togglePasswordVisibility("oldPassword", "oldPasswordToggle");
		});
		this.addMultipleEventListeners(["newPasswordToggle"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.togglePasswordVisibility("newPassword", "newPasswordToggle");
		});
		this.addMultipleEventListeners(["confirmPasswordToggle"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.togglePasswordVisibility("confirmPassword", "confirmPasswordToggle");
		});
		this.addMultipleEventListeners(["requestOldEmailOTP", "requestNewEmailOTP"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.emailRequestOTP();
		});
		this.addMultipleEventListeners(["changePasswordRequestOTP"], ["click", "keydown"], (event) => {
			if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
				return;
			}
			this.changePasswordGetNewOTP();
		});
		this.shadowRoot
			.getElementById("logoutButton")
			.addEventListener("click", this.handleLogout.bind(this));
		this.shadowRoot
			.getElementById("deleteUserButton")
			.addEventListener("click", this.handleDeleteUser.bind(this));
		this.shadowRoot
			.getElementById("cancelEmailButton")
			.addEventListener("click", this.emailCancelChange.bind(this));
		this.shadowRoot
			.getElementById("saveNewEmailButton")
			.addEventListener("click", this.emailChangeWithOTP.bind(this));
		this.shadowRoot
			.getElementById("changePasswordOTP")
			.addEventListener("input", this.validatePasswordOTP.bind(this));
		this.shadowRoot
			.getElementById("changePasswordOTPCancel")
			.addEventListener("click", this.cancelChangePasswordOTP.bind(this));
		this.shadowRoot
			.getElementById("changeUsernameSwitchBackupCode")
			.addEventListener("change", (event) => {
				const button = this.shadowRoot.getElementById("requestOldEmailOTP");
				const label = this.shadowRoot.querySelector("label[for=oldEmailOTP]");
				const input = this.shadowRoot.querySelector("input#oldEmailOTP");
				if (event.target.checked) {
					input.maxLength = 32;
					input.minLength = 32;
				} else {
					input.minLength = 16;
					input.maxLength = 16;
				}
				button.style.display = event.target.checked ? "none" : "block";
				label.textContent = event.target.checked ? "Backup Code" : "OTP sent to old E-Mail";
				input.pattern = event.target.checked ? "[A-Za-z0-9]{32}" : "[A-Za-z0-9]{16}";
			});
		this.shadowRoot
			.getElementById("changeFontSize")
			.addEventListener("click", (event) => {
				if (event.target.tagName === "A") {
					const buttons = this.shadowRoot.getElementById("changeFontSize").querySelectorAll("a");
					for (const button of buttons) {
						button.classList.remove("active")
					}
					event.target.classList.add("active");
				}
			});
	}

	emailChange(event) {
		if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
			return;
		}
		const email = this.shadowRoot.getElementById("email");
		const button = this.shadowRoot.getElementById("changeEmailButton");
		const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

		if (email.disabled) {
			email.disabled = false;
			button.textContent = "Save";
		} else {
			if (!emailPattern.test(email.value)) {
				email.classList.add("warning");
				return;
			}
			email.classList.remove("warning");
			if (email.value !== window.app.userData.email) {
				this.emailRequestOTP();
			}
			email.disabled = true;
			button.textContent = "Change";
		}
	}

	/**
	* Requests OTP for email change and starts a countdown timer for OTP request buttons.
	*
	* This method sends a POST request to the server to request an OTP for changing the email.
	* It then displays the OTP input fields and starts a countdown timer on the OTP request buttons.
	*/
	async emailRequestOTP() {
		const requestOldEmailOTP = this.shadowRoot.getElementById("requestOldEmailOTP");
		const requestNewEmailOTP = this.shadowRoot.getElementById("requestNewEmailOTP");
		const oldEmailContainer = this.shadowRoot.getElementById("oldEmailContainer");
		const newEmailContainer = this.shadowRoot.getElementById("newEmailContainer");
		const email = this.shadowRoot.getElementById("email");
		const emailWarning = this.shadowRoot.getElementById("emailWarning");

		if (requestOldEmailOTP.hasAttribute("disabled") || requestNewEmailOTP.hasAttribute("disabled")) {
			return;
		}

		emailWarning.style.display = "none";
		email.classList.remove("warning");
		try {
			await this.apiFetch("/registration/change_username", {
				method: "POST",
				body: JSON.stringify({ new_username: email.value }),
			});
			oldEmailContainer.removeAttribute("hidden");
			newEmailContainer.removeAttribute("hidden");
			requestOldEmailOTP.setAttribute("disabled", "");
			requestNewEmailOTP.setAttribute("disabled", "");
			let timer = 60;
			if (this.interval)
				clearInterval(this.interval);
			this.interval = setInterval(() => {
				requestOldEmailOTP.textContent = `${timer}s`;
				requestNewEmailOTP.textContent = `${timer}s`;
				if (--timer < 0) {
					clearInterval(this.interval);
					requestOldEmailOTP.textContent = "New OTP";
					requestNewEmailOTP.textContent = "New OTP";
					requestOldEmailOTP.removeAttribute("disabled");
					requestNewEmailOTP.removeAttribute("disabled");
				}
			}, 1000);
			this.shadowRoot.getElementById("oldEmailOTP").focus();
		} catch (error) {
			email.classList.add("warning");
			this.shadowRoot.getElementById("emailWarning").style.display = "block";
		}
	}

	emailCancelChange() {
		const oldEmailContainer = this.shadowRoot.getElementById("oldEmailContainer");
		const newEmailContainer = this.shadowRoot.getElementById("newEmailContainer");
		const email = this.shadowRoot.getElementById("email");
		const requestOldEmailOTP = this.shadowRoot.getElementById("requestOldEmailOTP");
		const requestNewEmailOTP = this.shadowRoot.getElementById("requestNewEmailOTP");
		const oldEmailOTP = this.shadowRoot.getElementById("oldEmailOTP");
		const newEmailOTP = this.shadowRoot.getElementById("newEmailOTP");
		oldEmailOTP.classList.remove("warning");
		newEmailOTP.classList.remove("warning");
		email.disabled = true;
		email.value = window.app.userData.email;
		oldEmailContainer.hidden = true;
		newEmailContainer.hidden = true;
		requestOldEmailOTP.textContent = "New OTP";
		requestNewEmailOTP.textContent = "New OTP";
		oldEmailOTP.value = "";
		newEmailOTP.value = "";
	}

	/**
	 * Validates the OTP input fields for email change.
	 *
	 * This method validates the OTP input fields for email change and enables the change email button if the OTPs are valid.
	 * The OTPs must be 16 digits long.
	 */
	emailValidateOTP() {
		const oldEmailOTP = this.shadowRoot.getElementById("oldEmailOTP");
		const newEmailOTP = this.shadowRoot.getElementById("newEmailOTP");
		oldEmailOTP.classList.remove("warning");
		newEmailOTP.classList.remove("warning");
		const changeEmailButton = this.shadowRoot.getElementById("saveNewEmailButton");
		if (new RegExp(oldEmailOTP.pattern).test(oldEmailOTP.value) && new RegExp(newEmailOTP.pattern).test(newEmailOTP.value)) {
			changeEmailButton.removeAttribute("disabled");
		} else {
			changeEmailButton.setAttribute("disabled", "");
		}
	}

	async emailChangeWithOTP(event) {
		event.preventDefault();
		const email = this.shadowRoot.getElementById("email");
		const oldEmailOTP = this.shadowRoot.getElementById("oldEmailOTP");
		const newEmailOTP = this.shadowRoot.getElementById("newEmailOTP");
		const toggleSwitch = this.shadowRoot.getElementById("changeUsernameSwitchBackupCode");
		if (oldEmailOTP.value && newEmailOTP.value) {
			try {
				await this.apiFetch("/registration/change_username", {
					method: "POST",
					body: JSON.stringify({
					    new_username: email.value,
					    [toggleSwitch.checked ? "backup_code" : "otp_old_email"]: oldEmailOTP.value,
					    otp_new_email: newEmailOTP.value
					}),
				});
				window.app.userData.email = email.value;
				this.emailCancelChange();
			} catch (error) {
				oldEmailOTP.classList.add("warning");
				newEmailOTP.classList.add("warning");
			}
		}
	}

	async toggleDisplayname(event) {
		if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
			return;
		}
		const displayName = this.shadowRoot.getElementById("displayName");
		const button = this.shadowRoot.getElementById("changeDisplayNameButton");
		const warning = this.shadowRoot.getElementById("profileDisplayNameWarning");
		warning.style.display = "none";
		displayName.classList.remove("warning");
		if (displayName.disabled) {
			this.currentDisplayName = displayName.value;
			displayName.disabled = false;
			button.textContent = "Save";
		} else {
			if (displayName.value !== this.currentDisplayName) {
				const formData = new FormData();
				formData.append("displayname", displayName.value);
				try {
					await this.apiFetch("/um/profile",{
						method: "PATCH",
						body: formData },
						"multipart/form-data",
					);
					this.currentDisplayName = displayName.value;
					window.app.userData.username = displayName.value;
				} catch (error) {
					displayName.value = this.currentDisplayName;
					displayName.classList.add("warning");
					warning.style.display = "block";
					warning.textContent = error;
				}
			}
			displayName.disabled = true;
			button.textContent = "Change";
		}
	}

	showDeleteError(message) {
		const errorDiv = this.shadowRoot.querySelector("#deleteError");
		const messageSpan = errorDiv.querySelector(".error-message");
		messageSpan.textContent = message;
		errorDiv.classList.remove("d-none");
	}

	hideDeleteError() {
		const errorDiv = this.shadowRoot.querySelector("#deleteError");
		errorDiv.classList.add("d-none");
	}

	async deleteUserAPIHandler() {
		const deleteUserPassword =
			this.shadowRoot.getElementById("deleteUserPassword");
		const otpSection = this.shadowRoot.getElementById("otpSection");
		const password = deleteUserPassword.value;
		const otp = this.shadowRoot.getElementById("deleteUserOTP").value;
		if (otpSection.style.display !== "none") {
			otp
				? this.shadowRoot
						.getElementById("deleteUserOTP")
						.classList.remove("warning")
				: this.shadowRoot
						.getElementById("deleteUserOTP")
						.classList.add("warning");
			if (!password || !otp) {
				return;
			}
		} else if (!password) {
			return;
		}
		this.hideDeleteError();

		try {
			if (otpSection.style.display === "none") {
				await this.apiFetch("/registration/delete_user", {
					method: "POST",
					body: JSON.stringify({ password: password }),
				});
				otpSection.style.display = "block";
				this.shadowRoot.getElementById("passwordSection").style.display =
					"none";
				this.shadowRoot.getElementById(
					"requestDeleteUserButton",
				).style.display = "none";
				this.shadowRoot.getElementById(
					"confirmDeleteUserButton",
				).style.display = "block";
				this.shadowRoot.getElementById("deleteUserOTP").focus();
			} else {
				await this.apiFetch("/registration/delete_user", {
					method: "POST",
					body: JSON.stringify({ password: password, otp: otp }),
				});
				await window.app.router.go("/login", true);
			}
		} catch (error) {
			this.showDeleteError(error);
			console.error("Error: ", error);
		}
	}

	async handleDeleteUser() {
		const userManagement = this.shadowRoot.getElementById("userManagement");
		const deleteUserConfirmation = this.shadowRoot.getElementById(
			"deleteUserConfirmation",
		);
		const deleteUserButton = this.shadowRoot.getElementById("deleteUserButton");

		const requestOTPButton = this.shadowRoot.getElementById(
			"requestDeleteUserButton",
		);
		const confirmDeleteUserButton = this.shadowRoot.getElementById(
			"confirmDeleteUserButton",
		);

		const deleteUserPassword =
			this.shadowRoot.getElementById("deleteUserPassword");
		const otpSection = this.shadowRoot.getElementById("otpSection");
		const passwordSection = this.shadowRoot.getElementById("passwordSection");

		if (deleteUserConfirmation.style.display === "none") {
			deleteUserConfirmation.style.display = "block";
			userManagement.style.display = "none";
			deleteUserButton.textContent = "Cancel";
			otpSection.style.display = "none";
			passwordSection.style.display = "block";
			this.hideDeleteError();
			deleteUserPassword.value = "";
			this.shadowRoot.getElementById("deleteUserOTP").value = "";
			deleteUserPassword.focus();
		} else {
			deleteUserConfirmation.style.display = "none";
			userManagement.style.display = "block";
			deleteUserButton.textContent = "Delete User";
			otpSection.style.display = "none";
			requestOTPButton.style.display = "block";
			confirmDeleteUserButton.style.display = "none";
			deleteUserButton.focus();
		}

		//setting aria labels for accessibility
		requestOTPButton.setAttribute(
			"aria-label",
			"Request OTP for deleting user",
		);
		confirmDeleteUserButton.setAttribute("aria-label", "Confirm deleting user");
		deleteUserPassword.setAttribute("aria-label", "Enter current password");
		this.shadowRoot
			.getElementById("deleteUserOTP")
			.setAttribute("aria-label", "Enter OTP to confirm user deletion");

		requestOTPButton.addEventListener(
			"click",
			this.deleteUserAPIHandler.bind(this),
		);
		confirmDeleteUserButton.addEventListener(
			"click",
			this.deleteUserAPIHandler.bind(this),
		);
		this.shadowRoot
			.getElementById("deleteUserPassword")
			.addEventListener("keydown", (e) => {
				if (e.key === "Enter") {
					this.deleteUserAPIHandler();
				}
			});
		this.shadowRoot
			.getElementById("deleteUserOTP")
			.addEventListener("keydown", (e) => {
				if (e.key === "Enter") {
					this.deleteUserAPIHandler();
				}
			});
	}

	async handleLogout() {
		await fetch("/registration/logout", { method: "GET" })
			.then(() => {
				window.localStorage.removeItem("oauthCode");
				window.localStorage.removeItem("oauthState");
				window.app.router.go("/login", true);
			})
			.catch((error) => {
				console.error("Error logging out:", error);
			});
	}

	togglePasswordVisibility(passwordFieldId, toggleButtonId) {
		const passwordField = this.shadowRoot.getElementById(passwordFieldId);
		const toggleButton = this.shadowRoot.getElementById(toggleButtonId);
		if (passwordField.type === "password") {
			passwordField.type = "text";
			toggleButton.textContent = "Hide";
		} else {
			passwordField.type = "password";
			toggleButton.textContent = "Show";
		}
	}

	async loadUserData() {
		try {
			// Fetch user data from global app object or API
			const response = await this.apiFetch("/um/profile", {
				method: "GET",
				cache: "no-store",
			});
			if ("displayname" in response) {
				window.app.userData.username = response.displayname;
				this.shadowRoot.getElementById("displayName").value =
					window.app.userData.username;
			}
			if ("image" in response) {
				window.app.userData.profileImage = response.image;
				this.shadowRoot.getElementById("profileImage").src =
					window.app.userData.profileImage;
			}
			if (!window.app.userData.email) {
				const email_response = await this.apiFetch("/registration/get_email", {
					method: "GET",
					cache: "no-store",
				});
				window.app.userData.email = email_response.email;
			}
			this.shadowRoot.getElementById("email").value = window.app.userData.email;
		} catch (error) {
			console.error("Error loading user data:", error);
		}
	}

	async handleImageUpload(event) {
		const file = event.target.files[0];
		const allowedTypes = ["image/jpeg", "image/png"];
		const maxSize = 1024 * 1024; // 1MB

		const warningMessage = this.shadowRoot.getElementById("imageWarning");
		warningMessage.textContent = "";
		warningMessage.classList.remove("alert", "alert-danger");

		if (file) {
			if (!allowedTypes.includes(file.type)) {
				warningMessage.textContent = "Only JPEG and PNG files are allowed.";
				warningMessage.classList.add("alert", "alert-danger");
				return;
			}

			if (file.size > maxSize) {
				warningMessage.textContent = "File size must be less than 1MB.";
				warningMessage.classList.add("alert", "alert-danger");
				return;
			}

			const reader = new FileReader();
			reader.onload = (e) => {
				this.shadowRoot.getElementById("profileImage").src = e.target.result;
				window.app.userData.profileImage = e.target.result;
			};
			const formData = new FormData();
			formData.append("image", file);
			try {
				await this.apiFetch(
					"/um/profile",
					{ method: "PATCH", body: formData },
					"multipart/form-data",
				);
				reader.readAsDataURL(file);
			} catch {
				warningMessage.textContent = "Error uploading image.";
				warningMessage.classList.add("alert", "alert-danger");
			}
		}
	}

	validatePasswords() {
		const passwordWarning = this.shadowRoot.getElementById("changePasswordWarning");
		passwordWarning.style.display = "none";
		const newPassword = this.shadowRoot.getElementById("newPassword").value;
		const confirmPassword =
			this.shadowRoot.getElementById("confirmPassword").value;
		if (newPassword === "" && confirmPassword === "") {
			return;
		}
		const changePasswordButton =
			this.shadowRoot.getElementById("changePassword");

		if (newPassword !== confirmPassword) {
			this.shadowRoot.getElementById("newPassword").classList.add("warning");
			this.shadowRoot
				.getElementById("confirmPassword")
				.classList.add("warning");
			passwordWarning.style.display = "block";
			passwordWarning.textContent = "Passwords do not match";
			changePasswordButton.disabled = true;
		} else {
			this.shadowRoot.getElementById("newPassword").classList.remove("warning");
			this.shadowRoot
				.getElementById("confirmPassword")
				.classList.remove("warning");
			changePasswordButton.disabled = false;
		}
	}

	cancelChangePasswordOTP() {
		const passwordSection = this.shadowRoot.getElementById("passwordForm");
		const otpSection = this.shadowRoot.getElementById("changePasswordOTPSection");
		const oldPassword = this.shadowRoot.getElementById("oldPassword");
		const newPassword = this.shadowRoot.getElementById("newPassword");
		const confirmPassword = this.shadowRoot.getElementById("confirmPassword");
		const otp = this.shadowRoot.getElementById("changePasswordOTP");
		const error = this.shadowRoot.getElementById("changePasswordWarning");
		const newOTPButton = this.shadowRoot.getElementById("changePasswordRequestOTP");

		oldPassword.value = "";
		newPassword.value = "";
		confirmPassword.value = "";
		otp.value = "";
		oldPassword.removeAttribute("disabled");
		newPassword.removeAttribute("disabled");
		confirmPassword.removeAttribute("disabled");
		passwordSection.classList.remove("d-none");
		otpSection.classList.add("d-none");
		error.textContent = "";
		newOTPButton.removeAttribute("disabled");
		otp.focus();
	}

	validatePasswordOTP() {
		const newPasswordOTP = this.shadowRoot.getElementById("changePasswordOTP");
		const changePasswordButton = this.shadowRoot.getElementById("changePassword");
		const pattern = /^[0-9A-Za-z]{16}$/;
		if (pattern.test(newPasswordOTP.value)) {
			changePasswordButton.removeAttribute("disabled");
		} else {
			changePasswordButton.setAttribute("disabled", "");
		}
	}

	async changePasswordGetNewOTP() {
		const newOTPButton = this.shadowRoot.getElementById("changePasswordRequestOTP");
		if (newOTPButton.hasAttribute("disabled")) {
			return;
		}
		const oldPassword = this.shadowRoot.getElementById("oldPassword").value;
		const newPassword = this.shadowRoot.getElementById("newPassword").value;
		await this.apiFetch("/registration/change_password", {
			method: "POST",
			body: JSON.stringify({
				current_password: oldPassword,
				new_password: newPassword,
			}),
		});
		newOTPButton.setAttribute("disabled", "");
		let timer = 60;
		newOTPButton.textContent = `${timer}s`;
		if (this.interval)
			clearInterval(this.interval);
		this.interval = setInterval(() => {
			newOTPButton.textContent = `${timer}s`;
			if (--timer < 0) {
				clearInterval(this.interval);
				newOTPButton.textContent = "New OTP";
				newOTPButton.removeAttribute("disabled");
			}
		}, 1000);
		this.shadowRoot.getElementById("newPasswordOTP").focus();
	}

	async changePassword(event) {
		if (event.type === "keydown" && event.key !== "Enter" && event.key !== " ") {
			return;
		}
		const changeButton = this.shadowRoot.getElementById("changePassword");
		const changePasswordWarning = this.shadowRoot.getElementById("changePasswordWarning");
		const otpSection = this.shadowRoot.getElementById("changePasswordOTPSection");
		const passwordSection = this.shadowRoot.getElementById("passwordForm");
		changeButton.disabled = true;
		changePasswordWarning.style.display = "none";
		changePasswordWarning.textContent = "";

		const oldPassword = this.shadowRoot.getElementById("oldPassword").value;
		const newPassword = this.shadowRoot.getElementById("newPassword").value;
		const confirmPassword =
			this.shadowRoot.getElementById("confirmPassword").value;
		if (newPassword !== confirmPassword) {
			return;
		}

		if (otpSection.classList.contains("d-none")) {
			try {
				await this.changePasswordGetNewOTP();
				passwordSection.classList.add("d-none");
				otpSection.classList.remove("d-none");
			} catch (error) {
				changePasswordWarning.textContent = error;
				changePasswordWarning.style.display = "block";
			}
		} else {
			const otp = this.shadowRoot.getElementById("changePasswordOTP");
			otp.classList.remove("warning");
			if (!otp.value || otp.value.length !== 16) {
				otp.classList.add("warning");
				return;
			}
			try {
				await this.apiFetch("/registration/change_password", {
					method: "POST",
					body: JSON.stringify({
						current_password: oldPassword,
						new_password: newPassword,
						otp: otp.value,
					}),
				});
				this.shadowRoot.getElementById("oldPassword").value = "";
				this.shadowRoot.getElementById("newPassword").value = "";
				this.shadowRoot.getElementById("confirmPassword").value = "";
				this.shadowRoot.getElementById("changePasswordOTP").value = "";
				otp.value = "";
				otpSection.classList.add("d-none");
				passwordSection.classList.remove("d-none");
			} catch (error) {
				changePasswordWarning.textContent = error;
				changePasswordWarning.style.display = "block";
			}
		}
	}
}

customElements.define("user-profile", UserProfile);
