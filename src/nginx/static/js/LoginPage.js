// Update the LoginPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	constructor() {
		super(false); // false because the componentBaseClass makes event listeners for a tags (links) and we don't want to add /login to the history
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('loginSubmitButton').addEventListener('click', this.login.bind(this));
		this.shadowRoot.getElementById('requestOTP').addEventListener('click', this.requestOTP.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('submit', this.login.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('keydown', this.handleEmailEnter.bind(this));
		this.shadowRoot.getElementById('loginForm').addEventListener('input', this.validateForm.bind(this));

		//this.shadowRoot.getElementById('loginEmail').addEventListener('input', this.validateForm.bind(this));
		//this.shadowRoot.getElementById('loginPassword').addEventListener('input', this.validateForm.bind(this));
		//this.shadowRoot.getElementById('otpCode').addEventListener('input', this.handleOTPInput.bind(this));
	}

	getElementHTML(){
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
                <form id="loginForm">
                    <h3 class="text-center text-white">Login</h3>
                    <label for="loginEmail" class="form-label text-white-50">Email address</label>
                    <div class="input-group mb-3">
                    	<input name="email" id="loginEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="errorMessage" aria-required="true">
                    	<button class="btn btn-custom" type="button" id="requestOTP" style="min-width: 100px;" disabled>Send OTP</button>
                    </div>
                    <div id="otpSection" style="display: none;">
                    	<label for="otpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                    	<input name="otp" id="otpCode" type="text" class="form-control mb-3" aria-required="true" pattern="[A-Z0-9]{16}" minlength="16" maxlength="16">
                    	<span id="otpErrorMessage" class="text-danger"></span>
                    </div>
                    <label for="loginPassword" class="form-label text-white-50">Password</label>
                    <input name="password" id="loginPassword" type="password" class="form-control mb-3" aria-describedby="errorMessage" aria-required="true">
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
			if (!otpSectionVisible) {
				await this.requestOTP(event);
			} else if (otpSectionVisible && loginButton.disabled === false) {
				await this.login(event);
			}
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
		const otpPattern = /^[A-Z0-9]{16}$/;
		const emailValid = this.validateEmail();
		const otpButton = this.shadowRoot.getElementById('requestOTP');

		if (otpButton.disabled && emailValid && password.length > 0) {
			otpButton.disabled = false;
		}

		loginButton.disabled = !(emailValid && password.length > 0 && otpPattern.test(otp));
	}

	async requestOTP(event) {
		event.preventDefault();
		const requestOTPButton = this.shadowRoot.getElementById('requestOTP');
		if (requestOTPButton.disabled) return;

		const email = this.shadowRoot.getElementById('loginEmail').value;
		const errorMessage = this.shadowRoot.getElementById('errorMessage');
		const password = this.shadowRoot.getElementById('loginPassword').value;

		requestOTPButton.disabled = true;

		try {
			//TODO: integrate send OTP endpoint when it is finished
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
			this.startTimer(60, requestOTPButton);
			this.shadowRoot.getElementById('otpSection').style.display = 'block';
		} catch (error) {
			console.error('Error during OTP request:', error);
			errorMessage.textContent = 'Could not send OTP';
			this.shadowRoot.getElementById('loginEmail').setAttribute('aria-invalid', 'true');
			requestOTPButton.disabled = false;
		}
	}

	startTimer(duration, button) {
		let timer = duration, minutes, seconds;
		this.timer = setInterval(() => {
			minutes = parseInt(timer / 60, 10);
			seconds = parseInt(timer % 60, 10);

			minutes = minutes < 10 ? '0' + minutes : minutes;
			seconds = seconds < 10 ? '0' + seconds : seconds;

			button.textContent = `${minutes}:${seconds}`;

			if (--timer < 0) {
				clearInterval(this.timer);
				button.textContent = 'Send OTP';
				button.disabled = false;
			}
		}, 1000);
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
			const displaynameResponse = await fetch ('/um/profile', {
				method: 'GET',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
			if (!displaynameResponse.ok) {
				await app.router.go('/displayname', false);
				console.log('displayname not ok:', displaynameResponse);
			} else {
				const responseData = await displaynameResponse.json();
				window.app.userData.username = responseData.displayname;
				if (responseData.image) {
					window.app.userData.profileImage = responseData.image;
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

customElements.define('login-page', LoginPage);