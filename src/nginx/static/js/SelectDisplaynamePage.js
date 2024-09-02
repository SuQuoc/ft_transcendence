import { ComponentBaseClass } from "./componentBaseClass.js";

export class SelectDisplaynamePage extends ComponentBaseClass {

	constructor() {
		super();

		this.handleSubmitDisplaynameVar = this.handleSubmitDisplayname.bind(this);
	}

	connectedCallback() {
		super.connectedCallback();

		console.log("SelectDisplaynamePage connectedCallback");
		// getting elements
		this.displayname_form = this.shadowRoot.getElementById("displayNameForm")
		
		// adding event listeners
		this.displayname_form.addEventListener("submit", this.handleSubmitDisplaynameVar);	
	}
	
	disconnectedCallback() {
		super.disconnectedCallback();

		// removind event listeners
		this.displayname_form.removeEventListener("submit", this.handleSubmitDisplaynameVar);
	}
	

	/// ----- Event Handlers ----- ///
	
	async handleSubmitDisplayname(event) {
		event.preventDefault();
		
		const displayname = event.target.displayname.value;
		console.log("displayname:", displayname);

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
				console.log("displayname ok");

				window.app.userData.username = displayname;
				window.app.router.go("/");
			} else {
				// if displayname is already taken
				//this.popover(event.target.displayname, "Displayname already taken");
				console.log("displayname already taken");
			}
		} catch (error) {
			console.error('Error selecting displayname:', error);
		}
	}
	

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="displayNameForm">
					<h3 class="text-center text-white">Select a unique Displayname</h3>

					<input name="displayname" id="displayName" type="text" class="form-control" placeholder="displayname" aria-describedby="displayNameHelp">
					<div class="form-text text-white-50 mb-3" id="displayNameHelp">Please enter a unique displayname</div>
					
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