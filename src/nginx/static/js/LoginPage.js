// Update the LoginPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	constructor() {
		super();
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('loginForm').addEventListener('submit', this.login.bind(this));
		this.shadowRoot.getElementById('loginEmail').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('loginPassword').addEventListener('input', this.validateForm.bind(this));
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
                <form id="loginForm">
                    <h3 class="text-center text-white">Login</h3>
                    <label for="loginEmail" class="form-label text-white-50">Email address</label>
                    <input name="email" id="loginEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="errorMessage" aria-required="true">
                    <label for="loginPassword" class="form-label text-white-50">Password</label>
                    <input name="password" id="loginPassword" type="password" class="form-control mb-3" aria-describedby="errorMessage" aria-required="true">
                    <span id="errorMessage" class="text-danger"></span>
                    <p class="text-white-50 small m-0">No account yet? <a href="/signup" class="text-decoration-none text-white">Sign up</a> here!</p>
                    <button type="submit" class="btn btn-custom w-100" form="loginForm" disabled>Log in</button>
                    <div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </form>
            </div>
        `;
		return template;
	}

	validateEmail() {
		const email = this.shadowRoot.getElementById('loginEmail').value;
		const emailWarning = this.shadowRoot.getElementById('errorMessage');
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

		if (!emailPattern.test(email)) {
			emailWarning.textContent = 'Invalid email address';
			this.shadowRoot.getElementById('loginEmail').setAttribute('aria-invalid', 'true');
			return false;
		} else {
			emailWarning.textContent = '';
			this.shadowRoot.getElementById('loginEmail').removeAttribute('aria-invalid');
			return true;
		}
	}

	validateForm() {
		const email = this.shadowRoot.getElementById('loginEmail').value;
		const password = this.shadowRoot.getElementById('loginPassword').value;
		const loginButton = this.shadowRoot.querySelector('button[type="submit"]');

		const emailValid = this.validateEmail();

		if (emailValid && password.length > 0) {
			loginButton.disabled = false;
		} else {
			loginButton.disabled = true;
		}
	}

	async login(event) {
		event.preventDefault();
		const loginButton = this.shadowRoot.querySelector('button[type="submit"]');
		const loginSpinner = this.shadowRoot.getElementById('loginSpinner');
		const loginError = this.shadowRoot.getElementById('errorMessage');
		loginButton.style.display = 'none';
		loginSpinner.style.display = 'inline-block';

		const username = this.shadowRoot.getElementById('loginEmail').value;
		const password = this.shadowRoot.getElementById('loginPassword').value;

		try {
			const response = await fetch('/registration/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!response.ok) {
				throw new Error('Login failed');
			}
			window.app.userData = window.app.userData || {};
			window.app.userData.email = username;

			// Redirect to the home page or another page
			app.router.go('/');
		} catch (error) {
			console.error('Error during login:', error);
			loginError.textContent = 'Could not log in';
			this.shadowRoot.getElementById('loginEmail').setAttribute('aria-invalid', 'true');
			this.shadowRoot.getElementById('loginPassword').setAttribute('aria-invalid', 'true');
			loginButton.style.display = 'block';
		} finally {
			loginSpinner.style.display = 'none';
		}
	}
}

customElements.define('login-page', LoginPage);