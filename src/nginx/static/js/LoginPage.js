// Update the LoginPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	constructor() {
		super(false); // false because the componentBaseClass makes event listeners for a tags (links) and we don't want to add /login to the history
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('loginSubmitButton').addEventListener('click', this.login.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('submit', this.login.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('keydown', this.handleEmailEnter.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('input', this.validateForm.bind(this));
	}

	getElementHTML(){
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
				<h3 class="text-center text-white">Login</h3>
            	<form id="42LoginForm" method="post" enctype="application/x-www-form-urlencoded" target="_self" action="/registration/oauthtwo_send_authorization_request">
            		<input type="hidden" name="next_step" value="login">
					<label for="loginWith42" class="form-label text-white-50">Only for 42 students</label>
					<button id="loginWith42" class="btn btn-custom w-100 mb-3" type="submit">Login with 42</button>
				</form>
            	<hr class="text-white-50">
                <form id="loginForm">
                    <label for="loginEmail" class="form-label text-white-50">Email address</label>
                    <input name="email" id="loginEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="errorMessage" aria-required="true">
                    <label for="loginPassword" class="form-label text-white-50">Password</label>
                    <input name="password" id="loginPassword" type="password" class="form-control mb-3" aria-describedby="errorMessage" aria-required="true">
                    <div id="otpSection" style="display: none;">
                    	<label for="otpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                    	<input name="otp" id="otpCode" type="text" class="form-control mb-3" aria-required="true" pattern="[A-Za-z0-9]{16}" minlength="16" maxlength="16">
                    	<span id="otpErrorMessage" class="text-danger"></span>
                    </div>
                    <span id="errorMessage" class="text-danger"></span>
                    <p class="text-white-50 small m-0">No account yet? <a href="/signup" class="text-decoration-none text-white" id="loginGoToSignup">Sign up</a> here!</p>
                    <p class="text-white-50 small m-0"><a href="/forgot-password" class="text-decoration-none text-white" id="forgotPassword">Forgot Password?</a></p>
                    <button type="submit" class="btn btn-custom w-100" form="loginForm" disabled id="loginSubmitButton">Log in</button>
                    <div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </form>
            </div>
        `;
		return template;
	}

	async handleEmailEnter(event) {
		if (event.key === 'Enter') {
			event.preventDefault();

			const otpSectionVisible = this.shadowRoot.getElementById('otpSection').style.display !== 'none';
			const loginButton = this.shadowRoot.getElementById('loginSubmitButton');
			await this.login(event);
		}
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
		const password = this.shadowRoot.getElementById('loginPassword').value;
		const otp = this.shadowRoot.getElementById('otpCode').value;
		const loginButton = this.shadowRoot.getElementById('loginSubmitButton');
		const otpPattern = /^[A-Za-z0-9]{16}$/;
		const emailValid = this.validateEmail();

		if (this.shadowRoot.getElementById('otpSection').style.display === 'none') {
			loginButton.disabled = !(emailValid && password.length > 0);
			return;
		}
		loginButton.disabled = !(emailValid && password.length > 0 && otpPattern.test(otp));
	}

	async login(event) {
		event.preventDefault();
		const loginButton = this.shadowRoot.getElementById('loginSubmitButton');
		const loginSpinner = this.shadowRoot.getElementById('loginSpinner');
		const loginError = this.shadowRoot.getElementById('errorMessage');
		loginButton.style.display = 'none';
		loginSpinner.style.display = 'inline-block';

		const email = this.shadowRoot.getElementById('loginEmail').value;
		const password = this.shadowRoot.getElementById('loginPassword').value;
		const otp = this.shadowRoot.getElementById('otpCode').value;

		if (this.shadowRoot.getElementById('otpSection').style.display === 'none') {
			try {
				const loginResponse = await fetch('/registration/basic_login', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ "username": email, password })
				});

				if (!loginResponse.ok) {
					throw new Error('Requesting OTP failed');
				}
				this.shadowRoot.getElementById('otpSection').style.display = 'block';
				this.shadowRoot.getElementById('otpCode').focus();
			} catch (error) {
				console.error('Error during OTP request:', error);
				loginError.textContent = 'Could not send OTP, check your credentials';
				this.shadowRoot.getElementById('loginEmail').setAttribute('aria-invalid', 'true');
				loginButton.style.display = 'block';
			} finally {
				loginButton.style.display = 'block';
				loginSpinner.style.display = 'none';
			}
		} else {
			try {
				const loginResponse = await fetch('/registration/basic_login', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ "username": email, password, otp })
				});

				if (!loginResponse.ok) {
					throw new Error('Login failed');
				}
				window.app.userData = window.app.userData || {};
				window.app.userData.email = email;

				// Check if the user already has a displayname
				const displaynameResponse = await fetch('/um/profile', {
					method: 'GET',
					headers: {
						'Content-Type': 'application/json'
					}
				});

				const displaynameData = await displaynameResponse.json();
				// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
				if (!displaynameResponse.ok || displaynameData.displayname === "") {
					await app.router.go('/displayname', false);
					console.log('displayname not ok:', displaynameResponse);
				} else {
					window.app.userData.username = displaynameData.displayname;
					if (displaynameData.image) {
						window.app.userData.profileImage = displaynameData.image;
					}
					await app.router.go("/", false);
				}
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
}

customElements.define('login-page', LoginPage);