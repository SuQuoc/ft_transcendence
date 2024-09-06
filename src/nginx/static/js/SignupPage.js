// Update the SignupPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class SignupPage extends ComponentBaseClass {
	constructor() {
		super(false); // false because the componentBaseClass makes event listeners for a tags (links) and we don't want to add /signup to the history
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('signupForm').addEventListener('submit', this.signup.bind(this));
		this.shadowRoot.getElementById('signupPassword1').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('signupPassword2').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('signupEmail').addEventListener('input', this.validateForm.bind(this));
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
                <form id="signupForm">
                    <h3 class="text-center text-white">Signup</h3>
                    <!-- Email -->
                    <label for="signupEmail" class="form-label text-white-50">Email address</label>
                    <input name="email"
                        id="signupEmail"
                        type="email"
                        class="form-control"
                        placeholder="name@example.com"
                        aria-required="true"
                        aria-describedby="errorMessageEmail"
                    />
                    <span id="errorMessageEmail" class="text-danger" style="display:block;"></span>
                    <!-- first Password -->
                    <label for="signupPassword1" class="form-label text-white-50">Password</label>
                    <input name="password"
                        id="signupPassword1"
                        type="password"
                        class="form-control mb-1"
                        aria-required="true"
                        aria-describedby="errorMessagePassword"
                    />
                    <!-- second Password -->
                    <label for="signupPassword2" class="form-label text-white-50">Password again</label>
                    <input name="password2"
                        id="signupPassword2"
                        type="password"
                        class="form-control mb-3"
                        aria-required="true"
                        aria-describedby="errorMessagePassword"
                    />
                    <span id="errorMessagePassword" class="text-danger"></span>
                    <!-- change to login page -->
                    <p class="text-white-50 small m-0">Already signed up?
                        <a href="/login" class="text-decoration-none text-white">
                            Log in
                        </a>
                        here!
                    </p>
                    <button type="submit" class="btn btn-custom w-100" form="signupForm">Sign up</button>
                    <div id="passwordWarning" class="alert alert-danger mt-3" style="display: none;">Passwords do not match</div>
                    <div id="emailWarning" class="alert alert-danger mt-3" style="display: none;">Invalid email address</div>
                    <div id="signupError" class="alert alert-danger mt-3" style="display: none;">Couldn't signup with provided data</div>
                </form>
            </div>
        `;
		return template;
	}

	validateForm() {
		const email = this.shadowRoot.getElementById('signupEmail').value;
		const password1 = this.shadowRoot.getElementById('signupPassword1').value;
		const password2 = this.shadowRoot.getElementById('signupPassword2').value;
		const signupButton = this.shadowRoot.querySelector('button[type="submit"]');
		const emailWarning = this.shadowRoot.getElementById('errorMessageEmail');
		const passwordWarning = this.shadowRoot.getElementById('errorMessagePassword');

		const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
		const passwordsMatch = password1 === password2;

		if (emailValid && passwordsMatch) {
			signupButton.disabled = false;
			emailWarning.textContent = '';
			passwordWarning.textContent = '';
		} else {
			signupButton.disabled = true;
			if (!emailValid) {
				this.shadowRoot.getElementById('signupEmail').setAttribute('aria-invalid', 'true');
				emailWarning.textContent = 'Invalid email address';
			} else {
				this.shadowRoot.getElementById('signupEmail').removeAttribute('aria-invalid');
				emailWarning.textContent = '';
			}
			if (!passwordsMatch) {
				this.shadowRoot.getElementById('signupPassword1').setAttribute('aria-invalid', 'true');
				this.shadowRoot.getElementById('signupPassword2').setAttribute('aria-invalid', 'true');
				passwordWarning.textContent = "Passwords don't match";
			} else {
				this.shadowRoot.getElementById('signupPassword1').removeAttribute('aria-invalid');
				this.shadowRoot.getElementById('signupPassword2').removeAttribute('aria-invalid');
				passwordWarning.textContent = '';
			}
		}
	}

	async signup(event) {
		event.preventDefault();
		const signupButton = this.shadowRoot.querySelector('button[type="submit"]');
		const signupError = this.shadowRoot.getElementById('signupError');
		signupButton.disabled = true;
		signupError.style.display = 'none';

		const email = this.shadowRoot.getElementById('signupEmail').value;
		const password = this.shadowRoot.getElementById('signupPassword1').value;
		const password2 = this.shadowRoot.getElementById('signupPassword2').value;

		if (password !== password2) {
			console.error('Passwords do not match');
			signupButton.disabled = false;
			return;
		}

		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
			console.error('Invalid email address');
			signupButton.disabled = false;
			return;
		}

		try {
			const response = await fetch('/registration/signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username: email, password })
			});

			if (!response.ok) {
				console.log(response);
				throw new Error('Signup failed');
			}
			window.app.userData.email = email;

			app.router.go('/displayname', false);
		} catch (error) {
			console.error('Error during signup:', error);
			signupError.style.display = 'block';
		} finally {
			signupButton.disabled = false;
		}
	}
}

customElements.define('signup-page', SignupPage);