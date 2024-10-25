import { ComponentBaseClass } from "./componentBaseClass.js";

export class SelectDisplaynamePage extends ComponentBaseClass {

	constructor() {
		super();

		this.handleSubmitDisplaynameVar = this.handleSubmitDisplayname.bind(this);
		this.handleHidingDisplaynameTakenWarningVar = this.handleHidingDisplaynameTakenWarning.bind(this);
		this.handlePasswordInputVar = this.handlePasswordInput.bind(this)
	}

	connectedCallback() {
		super.connectedCallback();

		// getting elements
		this.displayname_form = this.shadowRoot.getElementById("displayNameForm");
		this.input_field = this.shadowRoot.getElementById("displayNameInput");
		this.displayname_warning = this.shadowRoot.getElementById("displayNameWarning");
		this.password_warning = this.shadowRoot.getElementById("passwordWarning");

		// adding event listeners
		this.displayname_form.addEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.addEventListener("input", this.handleHidingDisplaynameTakenWarningVar);

		// setting focus on displayname input when the page is loaded 
		this.shadowRoot.getElementById("displayNameInput").focus();

		this.fetchEmailandPasswordStatus();
	}
	
	disconnectedCallback() {
		super.disconnectedCallback();

		// removind event listeners
		this.displayname_form.removeEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.removeEventListener("input", this.handleHidingDisplaynameTakenWarningVar);
	}

	async fetchEmailandPasswordStatus() {
		try {
			const response = await this.apiFetch('/registration/get_email', 'GET');
			if (!response.password_set) {
				this.showPasswordFields();
			}
			if (response.email) {
				app.userData.email = response.email;
			}
		} catch (error) {
			console.error('Error getting email and password status:', error);
		}
	}

	showPasswordFields() {
		const passwordFieldsHTML = `
   			<label for="passwordInput" class="form-label text-white">Password</label>
   			<input name="password" id="passwordInput" type="password" class="form-control" minlength="8" maxlength="120" required>
   			<label for="confirmPasswordInput" class="form-label text-white">Confirm Password</label>
   			<input name="confirmPassword" id="confirmPasswordInput" type="password" class="form-control mb-3" minlength="8" maxlength="120" required>
			<div id="passwordWarning" class="form-text text-danger" style="display: none;"></div>  		
		`;
  		this.shadowRoot.getElementById("displayNameSubmitButton").insertAdjacentHTML('beforebegin', passwordFieldsHTML);
		this.password_input = this.shadowRoot.getElementById("passwordInput");
		this.confirm_password_input = this.shadowRoot.getElementById("confirmPasswordInput");
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
				await this.apiFetch("/registration/change_password", "POST", JSON.stringify({ "current_password": "", 'new_password': password}));
			} catch (error) {
				console.error('Error changing password:', error);
			}
		}
		try {
			const response = await fetch('/um/user-creation', {
				method: 'POST',
				headers: {
					'Accept': 'application/json',
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ displayname })
			});

			if (response.ok) {
				window.app.userData.username = displayname;
				window.app.router.go("/", false);
			} else {
				// if displayname is already taken
				this.displayname_warning.innerHTML = "This displayname is already taken";
				this.displayname_warning.setAttribute("aria-invalid", "true");
				this.displayname_warning.style.display = "";
				console.log("displayname already taken");
			}
		} catch (error) {
			console.error('Error selecting displayname:', error);
		}
	}

	handleHidingDisplaynameTakenWarning() {
		this.displayname_warning.style.display = "none";
		this.displayname_warning.innerHTML = "";
		this.displayname_warning.setAttribute("aria-invalid", "false");
	}
	

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="displayNameForm">
					<h3 class="text-center text-white mb-3">We need additional information</h3>

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
					<div class="form-text text-white-50">Other users can see this name</div>
					<div id="displayNameWarning" class="form-text text-danger" style="display: none;"></div>
					
					<button type="submit" class="btn btn-custom w-100" id="displayNameSubmitButton" form="displayNameForm">submit</button>

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