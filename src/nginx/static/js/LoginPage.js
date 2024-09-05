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
                    <input name="email" id="loginEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="loginEmailHelp">
                    <div class="form-text text-white-50 mb-3" id="loginEmailHelp">We'll never share your email with a third party.....</div>
                    <label for="loginPassword" class="form-label text-white-50">Password</label>
                    <input name="password" id="loginPassword" type="password" class="form-control mb-3">
                    <p class="text-white-50 small m-0">No account yet? <a href="/signup" class="text-decoration-none text-white">Sign up</a> here!</p>
                    <button type="submit" class="btn btn-secondary w-100" form="loginForm" disabled>Log in</button>
                    <div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div id="loginError" class="alert alert-danger mt-3" style="display: none;">Couldn't login with provided data</div>
                    <div id="emailWarning" class="alert alert-danger mt-3" style="display: none;">Invalid email address</div>
                </form>
            </div>
        `;
		return template;
	}

	validateEmail() {
		const email = this.shadowRoot.getElementById('loginEmail').value;
		const emailWarning = this.shadowRoot.getElementById('emailWarning');
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

		if (!emailPattern.test(email)) {
			emailWarning.style.display = 'block';
			return false;
		} else {
			emailWarning.style.display = 'none';
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
		const loginError = this.shadowRoot.getElementById('loginError');
		const emailWarning = this.shadowRoot.getElementById('emailWarning');
		loginButton.style.display = 'none';
		loginSpinner.style.display = 'inline-block';
		loginError.style.display = 'none';

		const username = this.shadowRoot.getElementById('loginEmail').value;
		const password = this.shadowRoot.getElementById('loginPassword').value;

		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(username)) {
			emailWarning.style.display = 'block';
			loginButton.style.display = 'block';
			loginSpinner.style.display = 'none';
			return;
		}

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
			window.app.userData.username = username;
			window.app.userData.email = username;

			// Redirect to the home page or another page
			app.router.go('/');
		} catch (error) {
			console.error('Error during login:', error);
			loginError.style.display = 'block';
			loginButton.style.display = 'block';
		} finally {
			loginSpinner.style.display = 'none';
		}
	}
}

customElements.define('login-page', LoginPage);