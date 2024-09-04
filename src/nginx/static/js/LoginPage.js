// Update the LoginPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	constructor() {
		super();
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('loginForm').addEventListener('submit', this.login.bind(this));
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
                    <p class="text-white-50 small m-0">No account yet? <a href="/signup" id="loginGoToSignup" class="text-decoration-none text-white">Sign up</a> here!</p>
                    <button type="submit" class="btn btn-custom w-100" form="loginForm">Log in</button>
                    <div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </form>
            </div>
        `;
		return template;
	}

	async login(event) {
		event.preventDefault();
		const loginButton = this.shadowRoot.querySelector('button[type="submit"]');
		const loginSpinner = this.shadowRoot.getElementById('loginSpinner');
		loginButton.disabled = true;
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
			window.app.userData.username = username;
			window.app.userData.email = username;

			// Redirect to the home page or another page
			app.router.go('/');
		} catch (error) {
			console.error('Error during login:', error);
		} finally {
			loginButton.disabled = false;
			loginSpinner.style.display = 'none';
		}
	}
}

customElements.define('login-page', LoginPage);