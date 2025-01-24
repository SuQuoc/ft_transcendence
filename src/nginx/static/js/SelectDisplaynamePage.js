import { ComponentBaseClass } from "./componentBaseClass.js";

export class SelectDisplaynamePage extends ComponentBaseClass {

	constructor() {
		super();

		this.handleSubmitDisplaynameVar = this.handleSubmitDisplayname.bind(this);
		this.handleHidingDisplaynameTakenWarningVar = this.handleHidingDisplaynameTakenWarning.bind(this);
		this.handlePasswordInputVar = this.handlePasswordInput.bind(this)
	}

	connectedCallback() {
		// getting elements
		this.displayname_form = this.shadowRoot.getElementById("displayNameForm");
		this.input_field = this.shadowRoot.getElementById("displayNameInput");
		this.displayname_warning = this.shadowRoot.getElementById("displayNameWarning");
		this.password_warning = null;
		this.current_password = "";

		// adding event listeners
		this.displayname_form.addEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.addEventListener("input", this.handleHidingDisplaynameTakenWarningVar);

		// adding event listener for logout button
		this.shadowRoot.getElementById("logoutButton").addEventListener("click", this.handleLogout);

		// setting focus on displayname input when the page is loaded 
		this.shadowRoot.getElementById("displayNameInput").focus();

		this.fetchEmailandPasswordStatus();
	}
	
	disconnectedCallback() {
		// remove event listeners
		this.displayname_form.removeEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.removeEventListener("input", this.handleHidingDisplaynameTakenWarningVar);
	}

	async fetchEmailandPasswordStatus() {
		try {
			const response = await this.apiFetch('/registration/get_email', {method: 'GET'});
			if (!response.password_set) {
				this.showPasswordFields();
			}
			if (!app.userData.backupCodes?.length) {
				const backup_codes = await this.apiFetch('/registration/backup_rotate_codes', {method: 'POST'});
				app.userData.backupCodes = backup_codes;
			}
			if (app.userData.backupCodes && app.userData.backupCodes.length > 0) {
				this.displayBackupCodes(app.userData.backupCodes);
			}
			if (response.email) {
				app.userData.email = response.email;
			}
		} catch (error) {
			console.error('Error getting email and password status:', error);
		}
	}

	displayBackupCodes(backupCodes) {
	  const backupCodesContainer = `
		<div class="backup-codes text-white" style="max-width:600px;">
	    	<b class="text-warning">Important: Backup Codes</b>
	    	<p>Save these backup codes in a safe place. You can use them to access your account if you lose access to your OTP device. Just enter one of them on the login page instead of the OTP.</p>
	    	<ul>
	    		${backupCodes.map(code => `<li>${code}</li>`).join('')}
	    	</ul>
	    	<button id="copyBackupCodesButton" class="btn btn-secondary" type="button">Copy to Clipboard</button>
	    	<button id="downloadBackupCodesButton" class="btn btn-secondary" type="button">Download as File</button>
	    </div>
		`;
	  this.shadowRoot.getElementById("displayNameSubmitButton")
		  .insertAdjacentHTML('beforebegin', backupCodesContainer);

	  this.shadowRoot.getElementById("copyBackupCodesButton").addEventListener("click", () => {
		  const codesText = backupCodes.join('\n');
		  navigator.clipboard.writeText(codesText).then(() => {
			  alert("Backup codes copied to clipboard");
		  }).catch(err => {
			  console.error("Failed to copy backup codes: ", err);
		  });
	  });

	  this.shadowRoot.getElementById("downloadBackupCodesButton").addEventListener("click", () => {
		  const codesText = backupCodes.join('\n');
		  const blob = new Blob([codesText], { type: 'text/plain' });
		  const url = URL.createObjectURL(blob);
		  const a = document.createElement('a');
		  a.href = url;
		  a.download = 'backup_codes.txt';
		  a.click();
		  URL.revokeObjectURL(url);
	  });
	}

	showPasswordFields() {
		const passwordFieldsHTML = `
   			<label for="displayNamePasswordInput" class="form-label text-white">Password</label>
   			<input name="displayNamePassword" id="displayNamePasswordInput" type="password" class="form-control" minlength="8" maxlength="120" required>
   			<label for="displayNameConfirmPasswordInput" class="form-label text-white">Confirm Password</label>
   			<input name="displayNameConfirmPassword" id="displayNameConfirmPasswordInput" type="password" class="form-control mb-3" minlength="8" maxlength="120" required>
			<div id="displayNamePasswordWarning" class="form-text text-danger" style="display: none;"></div>  		
		`;
  		this.shadowRoot.getElementById("displayNameSubmitButton").insertAdjacentHTML('beforebegin', passwordFieldsHTML);
		this.password_input = this.shadowRoot.getElementById("displayNamePasswordInput");
		this.confirm_password_input = this.shadowRoot.getElementById("displayNameConfirmPasswordInput");
		this.password_warning = this.shadowRoot.getElementById("displayNamePasswordWarning");
 		this.password_input.addEventListener("input", this.handlePasswordInputVar);
		this.confirm_password_input.addEventListener("input", this.handlePasswordInputVar);
	}

	handlePasswordInput() {
		const password = this.password_input.value;
		const confirmPassword = this.confirm_password_input.value;

		if (password !== confirmPassword) {
			this.password_warning.innerHTML = "Passwords do not match";
			this.password_warning.setAttribute("aria-invalid", "true");
			this.password_warning.style.display = "";
		} else {
			this.password_warning.style.display = "none";
			this.password_warning.innerHTML = "";
			this.password_warning.setAttribute("aria-invalid", "false");
		}
 	}

	/// ----- Methods ----- ///

	isDisplaynameValid(displayname) {
		if (displayname === "") {
			this.displayname_warning.innerHTML = "Please enter a displayname";
			this.displayname_warning.setAttribute("aria-invalid", "true");
			this.displayname_warning.style.display = "";
			return false;
		}
		if (/\s/.test(displayname)) { // checks if the displayname has any whitespaces
			this.displayname_warning.innerHTML = "Whitespaces are not allowed";
			this.displayname_warning.setAttribute("aria-invalid", "true");
			this.displayname_warning.style.display = "";
			return false;
		}
		return true;
	}


	/// ----- Event Handlers ----- ///
	
	async handleSubmitDisplayname(event) {
		event.preventDefault();
		
		const displayname = event.target.displayname.value;

		// check if displayname is valid
		if (!this.isDisplaynameValid(displayname)) {
			return;
		}

		if (this.password_input && this.confirm_password_input) {
			const password = this.password_input.value;
			const confirmPassword = this.confirm_password_input.value;

			if (password !== confirmPassword || password.length < 8 || password.length > 120) {
				this.password_warning.innerHTML = "Invalid password";
				this.password_warning.setAttribute("aria-invalid", "true");
				this.password_warning.style.display = "";
				return;
			}
			try {
				await this.apiFetch("/registration/change_password", {method: "POST", body: JSON.stringify({ current_password: this.current_password, new_password: password})});
				this.current_password = password;
			} catch (error) {
				this.password_warning.innerHTML = error;
				this.password_warning.setAttribute("aria-invalid", "true");
				this.password_warning.style.display = "";
				return;
			}
		}
		try {
			await this.apiFetch('/um/user-creation', {method: 'POST', body: JSON.stringify({ displayname })});
			window.app.userData.username = displayname;
			window.app.router.go("/", false);
		} catch (error) {
			this.displayname_warning.innerHTML = error;
			this.displayname_warning.setAttribute("aria-invalid", "true");
			this.displayname_warning.style.display = "";
		}
	}

	handleHidingDisplaynameTakenWarning() {
		this.displayname_warning.style.display = "none";
		this.displayname_warning.innerHTML = "";
		this.displayname_warning.setAttribute("aria-invalid", "false");
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

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="displayNameForm" class="d-flex flex-column gap-3">
					<h3 class="text-center text-white m-0">We need additional information</h3>

					<div>
						<label for="displayNameInput"
						class="form-label text-white">Displayname</label>
						<input name="displayname"
						id="displayNameInput"
						type="text"
						class="form-control"
						maxlength="20"
						required
						aria-describedby="displayNameWarning"
						>
						<div class="form-text text-secondary">Other users can see this name</div>
						<div id="displayNameWarning" class="text-danger mt-2" style="display: none;"></div>
					</div>
					
					<button type="submit" class="btn btn-custom w-100" id="displayNameSubmitButton" form="displayNameForm">submit</button>
					<button type="button" class="btn btn-secondary w-100" id="logoutButton" aria-label="Logout">Logout</button>
					<div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
						<span class="visually-hidden">Loading...</span>
					</div>
				</form>
			</div>
		`;
		return template;
	};
}

customElements.define('select-displayname-page', SelectDisplaynamePage);