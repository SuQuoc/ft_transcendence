export class ErrorToastElement extends HTMLElement {
	/**	The toast should be put in a toast container (with the classes toast-container d-flex flex-column gap-1 position-fixed bottom-0 end-0 p-3)
	 *  for proper positioning and in order to work with other toasts.
	 * @param {string} error_message - The error message displayed in the toast body. */
	constructor(error_message) {
		super();
		this.error_message = error_message;

		// Binds the method to this class instance so it can be used in the event listener
		this.handleDismiss_var = this.handleDismiss.bind(this);
	}

	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);

		this.querySelector('.toast-body').textContent = this.error_message;

		// creating a new bootstrap toast
		const toast = this.querySelector('.toast');
		this.toast = new bootstrap.Toast(toast);

		// adding event listeners
		this.querySelector('button').addEventListener('click', this.handleDismiss_var);
	}

	disconnectedCallback() {
		// removing event listeners
		this.querySelector('button').removeEventListener('click', this.handleDismiss_var);
	}


	/// ----- Methods ----- ///

	show() {
		this.toast.show();
	}


	/// ----- Event Handlers ----- ///

	handleDismiss() { // couldn't get data-bs-dismiss="toast" to work
		this.toast.hide();
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<div class="toast align-items-center error-toast" data-bs-delay="7000" role="alert" aria-live="assertive" aria-atomic="true">
				<div class="d-flex">
					<div class="toast-body"></div>
					<button type="button" class="btn-close me-2 m-auto text-danger" data-bs-dismiss="toast" aria-label="Close"></button>
				</div>
			</div>
		`;
		return template;
	}
}

customElements.define('error-toast-element', ErrorToastElement);