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

		const username = this.shadowRoot.getElementById('loginEmail').value; // why is it called username and not email?
		const password = this.shadowRoot.getElementById('loginPassword').value;

		try {
			const outhResponse = await fetch('/registration/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!outhResponse.ok) {
				throw new Error('Login failed');
			}
			window.app.userData.email = username; // and why is the email set to the username?
			
			// Check if the user already has a displayname
			const displaynameResponse = await fetch ('/um/profile/', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});
			
			// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
			if (!displaynameResponse.ok) {
				window.app.router.go('/displayname'); // maybe this should be set to false?
				console.log('displayname not ok:', displaynameResponse);
			} else {
				const responseData = await displaynameResponse.json();
				window.app.userData.username = responseData.displayname;
				//window.app.userData.<image?> = responseData.image;
				app.router.go('/');
			}
		} catch (error) {
			console.error('Error during login:', error);
		} finally {
			loginButton.disabled = false;
			loginSpinner.style.display = 'none';
		}
	}
}

customElements.define('login-page', LoginPage);