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
		this.shadowRoot.getElementById('otpCode').addEventListener('input', this.handleOTPInput.bind(this));
		this.shadowRoot.getElementById('signupWith42').addEventListener('click', this.signupWith42.bind(this));
	}

	// !!!! id of button requestOTP should be signupRequestOTP
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
            	<h3 class="text-center text-white">Signup</h3>
            	<label for="signupWith42" class="form-label text-white-50">Only for 42 students</label>
            	<button id="signupWith42" class="btn btn-custom w-100 mb-3">Signup with 42</button>
            	<hr class="text-white-50">
                <form id="signupForm">
                    <div id="emailSection">
                    	<label for="signupEmail" class="form-label text-white-50">Email address</label>
						<input name="email"
							id="signupEmail"
							type="email"
							class="form-control"
							placeholder="name@example.com"
							aria-required="true"
							aria-describedby="errorMessageEmail"
						/>
					</div>
                    <span id="errorMessageEmail" class="text-danger mb-3" style="display:block;"></span>
                    <div id="passwordSection">
						<label for="signupPassword1" class="form-label text-white-50">Password</label>
						<input name="password"
							id="signupPassword1"
							type="password"
							class="form-control mb-1"
							aria-required="true"
							aria-describedby="errorMessagePassword"
						/>
						<label for="signupPassword2" class="form-label text-white-50">Password again</label>
						<input name="password2"
							id="signupPassword2"
							type="password"
							class="form-control mb-3"
							aria-required="true"
							aria-describedby="errorMessagePassword"
						/>
                    	<span id="errorMessagePassword" class="text-danger mb-3"></span>
					</div>
                    <div id="otpSection" style="display: none;">
                    	<label for="otpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                    	<input name="otp" id="otpCode" type="text" class="form-control mb-3" aria-required="true" pattern="[A-Z0-9]{16}" minlength="16" maxlength="16">
                    	<span id="otpErrorMessage" class="text-danger"></span>
                    </div>
                    <p class="text-white-50 small m-0">Already signed up?
                        <a href="/login" class="text-decoration-none text-white">
                            Log in
                        </a>
                        here!
                    </p>
                    <p class="text-white-50 small m-0"><a href="/forgot-password" class="text-decoration-none text-white" id="forgotPassword">Forgot Password?</a></p>
                    <button type="submit" class="btn btn-custom w-100" form="signupForm" id="signupSubmitButton" disabled>Sign up</button>
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
		const otpSection = this.shadowRoot.getElementById('otpSection');

		if (emailValid && passwordsMatch) {
			if (otpSection.style.display === 'block') {
				this.handleOTPInput();
			} else {
				signupButton.disabled = false;
				emailWarning.textContent = '';
				passwordWarning.textContent = '';
			}
		} else {
			otpSection.style.display = 'none';
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

	async requestOTP(event) {
		event.preventDefault();
		const requestOTPButton = this.shadowRoot.getElementById('requestOTP');
		if (requestOTPButton.disabled) return;

		const email = this.shadowRoot.getElementById('signupEmail').value;
		const errorMessage = this.shadowRoot.getElementById('errorMessageEmail');
		const password = this.shadowRoot.getElementById('signupPassword1').value;

		requestOTPButton.disabled = true;

		try {
			const response = await fetch('/registration/basic_signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ "username": email, password })
			});

			if (!response.ok) {
				throw new Error('Requesting OTP failed');
			}
			this.shadowRoot.getElementById('otpSection').style.display = 'block';
		} catch (error) {
			console.error('Error during OTP request:', error);
			errorMessage.textContent = 'Could not send OTP';
			this.shadowRoot.getElementById('signupEmail').setAttribute('aria-invalid', 'true');
			requestOTPButton.disabled = false;
		}
	}

	handleOTPInput() {
		const otp = this.shadowRoot.getElementById('otpCode').value;
		const errorMessage = this.shadowRoot.getElementById('otpErrorMessage');
		const otpPattern = /^[A-Z0-9]{16}$/;

		if (otpPattern.test(otp)) {
			errorMessage.textContent = '';
			this.shadowRoot.getElementById('otpCode').removeAttribute('aria-invalid');
		} else {
			errorMessage.textContent = 'Invalid OTP';
			this.shadowRoot.getElementById('otpCode').setAttribute('aria-invalid', 'true');
		}
		this.updateSignupButtonState();
	}

	updateSignupButtonState() {
		const email = this.shadowRoot.getElementById('signupEmail').value;
		const password1 = this.shadowRoot.getElementById('signupPassword1').value;
		const password2 = this.shadowRoot.getElementById('signupPassword2').value;
		const otp = this.shadowRoot.getElementById('otpCode').value;
		const signupButton = this.shadowRoot.querySelector('button[type="submit"]');
		const otpPattern = /^[A-Z0-9]{16}$/;

		if (email && password1 && password2 && otpPattern.test(otp)) {
			signupButton.disabled = false;
		} else {
			signupButton.disabled = true;
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
		const otp = this.shadowRoot.getElementById('otpCode').value;
		const otpSection = this.shadowRoot.getElementById('otpSection');

		if (otpSection.style.display === 'none') {
			try {
				const response = await fetch('/registration/basic_signup', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ username: email, password })
				});

				if (!response.ok) {
					throw new Error('Requesting OTP failed');
				}
				otpSection.style.display = 'block';
				this.shadowRoot.getElementById('signupEmail').disabled = true;
				this.shadowRoot.getElementById('signupPassword1').disabled = true;
				this.shadowRoot.getElementById('signupPassword2').disabled = true;
				this.shadowRoot.getElementById('otpCode').focus();
			} catch (error) {
				console.error('Error during OTP request:', error);
				this.shadowRoot.getElementById('errorMessageEmail').textContent = 'Could not send OTP';
				this.shadowRoot.getElementById('signupEmail').setAttribute('aria-invalid', 'true');
			}
		} else {
			try {
				const response = await fetch('/registration/basic_signup', {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({ username: email, password, otp })
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

	async signupWith42(event) {
		event.preventDefault();
		try {
			const response = await fetch('/registration/signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				throw new Error('Signup with 42 failed');
			}

			const data = await response.json();
			// Handle successful login with 42, e.g., redirect to home page
			await app.router.go("/", false);
		} catch (error) {
			console.error('Error during signup with 42:', error);
			this.shadowRoot.getElementById('errorMessage').textContent = 'Could not sign up with 42';
		}
	}
}

customElements.define('signup-page', SignupPage);