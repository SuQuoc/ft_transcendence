import { ComponentBaseClass } from "./componentBaseClass.js";

export class SelectDisplaynamePage extends ComponentBaseClass {

	constructor() {
		super();

		this.handleSubmitDisplaynameVar = this.handleSubmitDisplayname.bind(this);
		this.handleHidingDisplaynameTakenWarningVar = this.handleHidingDisplaynameTakenWarning.bind(this);
	}

	connectedCallback() {
		super.connectedCallback();

		// getting elements
		this.displayname_form = this.shadowRoot.getElementById("displayNameForm");
		this.input_field = this.shadowRoot.getElementById("displayName");
		this.displayname_taken_warning = this.shadowRoot.getElementById("displayNameTaken");
		this.displayname_enter_warning = this.shadowRoot.getElementById("displayNameEnter");
		this.displayname_whitespaces_warning = this.shadowRoot.getElementById("displayNameWhitespaces");
		
		// adding event listeners
		this.displayname_form.addEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.addEventListener("input", this.handleHidingDisplaynameTakenWarningVar);

		// setting focus on displayname input when the page is loaded 
		this.shadowRoot.getElementById("displayName").focus();
	}
	
	disconnectedCallback() {
		super.disconnectedCallback();

		// removind event listeners
		this.displayname_form.removeEventListener("submit", this.handleSubmitDisplaynameVar);
		this.input_field.removeEventListener("input", this.handleHidingDisplaynameTakenWarningVar);
	}
	

	/// ----- Methods ----- ///

	isDisplaynameValid(displayname) {
		if (displayname === "") {
			this.displayname_enter_warning.style.display = "";
			return false;
		}
		if (/\s/.test(displayname)) { // checks if the displayname has any whitespaces
			this.displayname_whitespaces_warning.style.display = "";
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

		try {
			const response = await fetch('/um/user-creation/', {
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
				this.displayname_taken_warning.style.display = "";
				console.log("displayname already taken");
			}
		} catch (error) {
			console.error('Error selecting displayname:', error);
		}
	}

	handleHidingDisplaynameTakenWarning() {
		this.displayname_taken_warning.style.display = "none";
		this.displayname_enter_warning.style.display = "none";
		this.displayname_whitespaces_warning.style.display = "none";
	}
	

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="displayNameForm">
					<h3 class="text-center text-white mb-3">Enter a unique Displayname</h3>

					<label for="displayName" id="displayNameTaken" class="form-label text-danger" style="display: none;">This displayname is already taken</label>
					<label for="displayName" id="displayNameEnter" class="form-label text-danger" style="display: none;">Please enter a displayname</label>
					<label for="displayName" id="displayNameWhitespaces" class="form-label text-danger" style="display: none;">Whitespaces are not allowed</label>

					<input name="displayname"
							id="displayName"
							type="text"
							class="form-control"
							maxlength="20"
							placeholder="displayname"
							aria-describedby="displayNameHelp"
					>
					<div class="form-text text-white-50 mb-3" id="displayNameHelp">Other users can see this name</div>
					
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