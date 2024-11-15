// Update the SignupPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class SignupPage extends ComponentBaseClass {
	constructor() {
		super(false); // false because the componentBaseClass makes event listeners for a tags (links) and we don't want to add /signup to the history
		this.otpRequestCooldown = 60;
		this.otpRequestTimer = null;
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('signupForm').addEventListener('submit', this.signup.bind(this));
		this.shadowRoot.getElementById('signupPassword1').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('signupPassword2').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('signupEmail').addEventListener('input', this.validateForm.bind(this));
		this.shadowRoot.getElementById('otpCode').addEventListener('input', this.handleOTPInput.bind(this));
		this.shadowRoot.getElementById('requestOtpButton').addEventListener('click', this.requestNewOtp.bind(this));
		this.shadowRoot.getElementById('changeUsernameButton').addEventListener('click', this.toggleUsername.bind(this));
    	this.shadowRoot.getElementById('changePassword1Button').addEventListener('click', this.togglePassword.bind(this, 'signupPassword1'));
		this.shadowRoot.getElementById('changePassword2Button').addEventListener('click', this.togglePassword.bind(this, 'signupPassword2'));
	}

	// !!!! id of button requestOTP should be signupRequestOTP
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark" style="max-width: 300px;">
            	<h3 class="text-center text-white">Signup</h3>
            	<form id="42SignupForm" method="post" enctype="application/x-www-form-urlencoded" target="_self" action="/registration/oauthtwo_send_authorization_request">
            		<input type="hidden" name="next_step" value="signup">
					<label for="loginWith42" class="form-label text-white-50">Only for 42 students</label>
					<button id="loginWith42" class="btn btn-custom w-100 mb-3" type="submit">Sign up with 42</button>
				</form>
            	<hr class="text-white-50">
                <form id="signupForm">
                    <div id="emailSection">
                    	<label for="signupEmail" class="form-label text-white-50">Email address</label>
						<div class="input-group mb-3">
							<input name="email"
								id="signupEmail"
								type="email"
								class="form-control rounded-end"
								placeholder="name@example.com"
								aria-required="true"
								aria-describedby="errorMessageEmail"
								required
							/>
							<button id="changeUsernameButton" class="btn btn-custom d-none" type="button">Change</button>
						</div>
					</div>
                    <span id="errorMessageEmail" class="text-danger mb-3" style="display:block;"></span>
                    <div id="passwordSection">
						<label for="signupPassword1" class="form-label text-white-50">Password</label>
                    	<div class="input-group">
							<input name="password"
								id="signupPassword1"
								type="password"
								class="form-control rounded-end"
								aria-required="true"
								aria-describedby="errorMessagePassword"
								minlength="8"
								maxlength="120"
								pattern="^(?=.*[a-zA-Z])[a-zA-Z0-9]{8,120}$"
								required
							/>
							<button id="changePassword1Button" class="btn btn-custom d-none" type="button">Change</button>
						</div>
						<label for="signupPassword2" class="form-label text-white-50">Repeat password</label>
						<div class="input-group mb-3">
							<input name="password2"
								id="signupPassword2"
								type="password"
								class="form-control rounded-end"
								aria-required="true"
								aria-describedby="errorMessagePassword"
								minlength="8"
								maxlength="120"
								pattern="^(?=.*[a-zA-Z])[a-zA-Z0-9]{8,120}$"
								required
							/>
							<button id="changePassword2Button" class="btn btn-custom d-none" type="button">Change</button>
						</div>
                    	<span id="errorMessagePassword" class="text-danger mb-3"></span>
					</div>
                    <div id="otpSection" style="display: none;">
                    	<label for="otpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                    	<div class="input-group mb-3">
                    		<input name="otp" id="otpCode" type="text" class="form-control" aria-required="true" pattern="[A-Za-z0-9]{16}" minlength="16" maxlength="16">
                    		<button id="requestOtpButton" class="btn btn-custom" type="button" disabled>New OTP</button>
                    	</div>
                    	<span id="otpErrorMessage" class="text-danger"></span>
                    </div>
                    <p class="text-white-50 small m-0">Already signed up?
                        <a href="/login" id="signupGoToLogin" class="text-decoration-none text-white">
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
		const signupButton = this.shadowRoot.getElementById('signupSubmitButton');
		const emailWarning = this.shadowRoot.getElementById('errorMessageEmail');
		const passwordWarning = this.shadowRoot.getElementById('errorMessagePassword');

		const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
		const passwordValid = /^(?=.*[a-zA-Z])[a-zA-Z0-9]{8,120}$/.test(password1);
		const passwordsMatch = password1 === password2;
		const otpSection = this.shadowRoot.getElementById('otpSection');

		console.log(emailValid, passwordValid, passwordsMatch, password1, password2, email);
		if (emailValid && passwordsMatch && passwordValid) {
			emailWarning.textContent = '';
			passwordWarning.textContent = '';
			if (otpSection.style.display === 'block' && this.shadowRoot.getElementById('otpCode').value.length !== 0) {
				this.handleOTPInput();
			} else {
				signupButton.removeAttribute("disabled");
			}
		} else {
			signupButton.setAttribute("disabled", "");
			if (!emailValid) {
				this.shadowRoot.getElementById('signupEmail').setAttribute('aria-invalid', 'true');
				emailWarning.textContent = 'Invalid email address';
			} else {
				this.shadowRoot.getElementById('signupEmail').removeAttribute('aria-invalid');
				emailWarning.textContent = '';
			}
			if ((!passwordsMatch || !passwordValid) && password1.length > 0) {
				this.shadowRoot.getElementById('signupPassword1').setAttribute('aria-invalid', 'true');
				this.shadowRoot.getElementById('signupPassword2').setAttribute('aria-invalid', 'true');
				if (!passwordValid) {
					passwordWarning.textContent = 'Password must be at least 8 characters long and contain at least one letter';
				} else {
					passwordWarning.textContent = "Passwords don't match";
				}
			} else {
				this.shadowRoot.getElementById('signupPassword1').removeAttribute('aria-invalid');
				this.shadowRoot.getElementById('signupPassword2').removeAttribute('aria-invalid');
				passwordWarning.textContent = '';
			}
		}
	}

	handleOTPInput() {
		const otp = this.shadowRoot.getElementById('otpCode').value;
		const errorMessage = this.shadowRoot.getElementById('otpErrorMessage');
		const otpPattern = /^[A-Za-z0-9]{16}$/;

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
		const signupButton = this.shadowRoot.getElementById('signupSubmitButton');
		const otpPattern = /^[A-Z0-9]{16}$/;

		if (email && password1 && password2 && otpPattern.test(otp)) {
			signupButton.removeAttribute('disabled');
		} else {
			signupButton.setAttribute('disabled', "");
		}
	}

	async signup(event) {
		event.preventDefault();
		const signupButton = this.shadowRoot.getElementById('signupSubmitButton');
		const signupError = this.shadowRoot.getElementById('signupError');
		signupButton.setAttribute('disabled', "");
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
				this.shadowRoot.getElementById('signupEmail').setAttribute('disabled', '');
				this.shadowRoot.getElementById('signupPassword1').setAttribute('disabled', '');
				this.shadowRoot.getElementById('signupPassword2').setAttribute('disabled', '');
				this.startOtpRequestCooldown();
				this.shadowRoot.getElementById('changeUsernameButton').classList.remove('d-none');
				this.shadowRoot.getElementById("signupEmail").classList.remove('rounded-end');
				this.shadowRoot.getElementById('changePassword1Button').classList.remove('d-none');
				this.shadowRoot.getElementById("signupPassword1").classList.remove('rounded-end');
				this.shadowRoot.getElementById('changePassword2Button').classList.remove('d-none');
				this.shadowRoot.getElementById("signupPassword2").classList.remove('rounded-end');
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
					throw new Error('Signup failed');
				}
				window.app.userData.email = email;
				app.router.go('/displayname', false);
			} catch (error) {
				console.error('Error during signup:', error);
				signupError.style.display = 'block';
			} finally {
				signupButton.removeAttribute('disabled');
			}
		}
	}

	async requestNewOtp() {
		const email = this.shadowRoot.getElementById('signupEmail').value;
		const password = this.shadowRoot.getElementById('signupPassword1').value;

		try {
			const response = await fetch('/registration/basic_signup_change_password', {
				method: 'POST',
				headers: {
				'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username: email, new_password: password })
			});

			if (!response.ok) {
				const responseData = await response.json();
				const errorMessage = Object.values(responseData)[0] || 'An unknown error occurred';
				throw new Error(errorMessage);
			}
			this.startOtpRequestCooldown();
		} catch (error) {
			this.shadowRoot.getElementById('otpErrorMessage').textContent = error;
		}
	}

	startOtpRequestCooldown() {
		const requestOtpButton = this.shadowRoot.getElementById('requestOtpButton');
		requestOtpButton.setAttribute('disabled', '');
		let remainingTime = this.otpRequestCooldown;

		this.otpRequestTimer = setInterval(() => {
			if (remainingTime > 0) {
				requestOtpButton.textContent = `${remainingTime}s`;
				remainingTime--;
			} else {
				clearInterval(this.otpRequestTimer);
				requestOtpButton.removeAttribute('disabled');
				requestOtpButton.textContent = 'New OTP';
			}
		}, 1000);
	}

	togglePassword(inputId) {
		const password1 = this.shadowRoot.getElementById('signupPassword1');
		const password2 = this.shadowRoot.getElementById('signupPassword2');
		const password1Button = this.shadowRoot.getElementById('changePassword1Button');
		const password2Button = this.shadowRoot.getElementById('changePassword2Button');

		if (password1.disabled && password2.disabled) {
			password1.disabled = false;
			password2.disabled = false;
			password1Button.textContent = 'Save';
			password2Button.textContent = 'Save';
		} else {
			if (inputId === 'signupPassword1') {
				password2.value = password1.value;
			} else {
				password1.value = password2.value;
			}
			this.savePassword();
			password1.disabled = true;
			password2.disabled = true;
			password1Button.textContent = 'Change';
			password2Button.textContent = 'Change';
			this.validateForm();
		}
	}

	toggleUsername() {
		const email = this.shadowRoot.getElementById('signupEmail');
		const button = this.shadowRoot.getElementById('changeUsernameButton');
		if (email.disabled) {
			this.currentUsername = email.value;
			email.disabled = false;
			button.textContent = 'Save';
		} else {
			this.saveUsername();
			email.disabled = true;
			button.textContent = 'Change';
			this.validateForm();
		}
	}

	async savePassword() {
		const password1 = this.shadowRoot.getElementById('signupPassword1').value;
		const email = this.shadowRoot.getElementById('signupEmail').value;
		try {
		  const response = await fetch('/registration/basic_signup_change_password', {
			method: 'POST',
			headers: {
			  'Content-Type': 'application/json'
			},
			body: JSON.stringify({ username: email, new_password: password1 })
		  });
		  if (!response.ok) {
			  const responseData = await response.json();
			  const errorMessage = Object.values(responseData)[0] || 'An unknown error occurred';
			  throw new Error(errorMessage);
		  }
		} catch (error) {
		  this.shadowRoot.getElementById('signupError').textContent = error;
		  this.shadowRoot.getElementById('signupError').style.display = 'block';
		}
	}

	async saveUsername() {
		const email = this.shadowRoot.getElementById('signupEmail').value;
		try {
		  const response = await fetch('/registration/basic_signup_change_username', {
			method: 'POST',
			headers: {
			  'Content-Type': 'application/json'
			},
			body: JSON.stringify({ current_username: this.currentUsername, new_username: email })
		  });
		  if (!response.ok) {
			  const responseData = await response.json();
			  const errorMessage = Object.values(responseData)[0] || 'An unknown error occurred';
			  throw new Error(errorMessage);
		  }
		  this.currentUsername = email;
		} catch (error) {
		  this.shadowRoot.getElementById('signupError').textContent = error;
		  this.shadowRoot.getElementById('signupError').style.display = 'block';
		}
	}
}

customElements.define('signup-page', SignupPage);