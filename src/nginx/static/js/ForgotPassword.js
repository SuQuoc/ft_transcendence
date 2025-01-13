// src/nginx/static/js/ForgotPassword.js
import { ComponentBaseClass } from "./componentBaseClass.js";

export class ForgotPassword extends ComponentBaseClass {
    constructor() {
        super(false);
    }

    connectedCallback() {
        super.connectedCallback();

        const formElements = this.shadowRoot.querySelectorAll('#forgotPasswordForm input, #forgotPasswordForm button[type="submit"]');
        formElements.forEach(element => {
            element.addEventListener('keydown', this.handleKeyDown.bind(this));
        });
        this.shadowRoot.getElementById('resetSubmitButton').addEventListener('click', this.resetPassword.bind(this));
        this.shadowRoot.getElementById('resetRequestOTP').addEventListener('click', this.requestOTP.bind(this));
        this.shadowRoot.getElementById('forgotPasswordForm').addEventListener('input', this.validateForm.bind(this));
        this.shadowRoot.getElementById('resetEmail').focus();
    }

    handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();

            if (this.validateForm()) {
                this.resetPassword(event);
            } else {
                this.requestOTP(event);
            }
        }
    }

    getElementHTML() {
        const template = document.createElement('template');
        template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
				<form id="forgotPasswordForm" class="d-flex flex-column needs-validation gap-3">
					<h3 class="text-center text-white mb-0">Forgot Password</h3>

					<div>
						<label for="resetEmail" class="form-label text-white-50">Email address</label>
						<input name="email" id="resetEmail" type="email" class="form-control mb-1" placeholder="name@example.com" aria-describedby="resetErrorMessage" aria-required="true" autocomplete="email" required>
						<div class="invalid-feedback mb-1">Please enter your email</div>
					</div>
					
					<div id="resetOtpSection" style="display: none;">
						<label for="resetOtpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
						<div class="input-group mb-1">
							<input name="otp" id="resetOtpCode" type="text" class="form-control" aria-required="true" pattern="[A-Z0-9]{16}" minlength="16" maxlength="16" autocomplete="one-time-code">
							<button class="btn btn-custom" type="button" id="resetRequestOTP" disabled>Send OTP</button>
							<div class="invalid-feedback mb-1">Please enter a valid OTP code</div>
						</div>
						<label for="resetNewPassword1" class="form-label text-white-50 mt-2">New Password</label>
						<input name="password1" id="resetNewPassword1" type="password" class="form-control mb-1" aria-required="true" autocomplete="new-password">
						<div class="invalid-feedback mb-1">Please enter a valid password</div>
						<label for="resetNewPassword2" class="form-label text-white-50">Confirm New Password</label>
						<input name="password2" id="resetNewPassword2" type="password" class="form-control mb-1" aria-required="true" autocomplete="new-password">
						<div class="invalid-feedback mb-1">Please enter a valid password</div>
						<span id="resetErrorMessage" class="text-danger mt-3"></span>
					</div>

					<div>
						<p class="text-white-50 small mb-1">
							Back to <a href="/login" class="text-decoration-none text-white" id="forgotPasswordGoToLogin">Log in</a>
							or <a href="/signup" class="text-decoration-none text-white" id="forgotPasswordGoToSignup">Sign up</a>
						</p>
						<button type="submit" class="btn btn-custom w-100" form="forgotPasswordForm" id="resetSubmitButton" disabled>Reset Password</button>
						<div class="spinner-border text-light" role="status" id="resetSpinner" style="display: none;">
							<span class="visually-hidden">Loading...</span>
						</div>
					</div>
				</form>
			</div>
        `;
        return template;
    }

    validateEmail(email) {
		const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

		if (!emailPattern.test(email.value)) {
			email.setAttribute('aria-invalid', 'true');
			return false;
		} else {
			email.removeAttribute('aria-invalid');
			return true;
		}
	}

    validateForm() {
		const email = this.shadowRoot.getElementById('resetEmail');
		const otpSection = this.shadowRoot.getElementById('resetOtpSection');
		const loginButton = this.shadowRoot.getElementById('resetSubmitButton');

		const otpPattern = /^[A-Za-z0-9]{16}$/;
		const emailValid = this.validateEmail(email);

		let isValid = true;

		if (!email.value || !emailValid) {
        	email.classList.add('is-invalid');
        	email.nextElementSibling.textContent = 'Email is required';
			email.nextElementSibling.classList.add('invalid-feedback');
            isValid = false;
    	} else {
        	email.classList.remove('is-invalid');
        	email.nextElementSibling.textContent = '';
			email.nextElementSibling.classList.remove('invalid-feedback');
    	}
        if (otpSection.style.display === 'none') {
            loginButton.disabled = !isValid;
            return isValid;
        }

        const otpCode = this.shadowRoot.getElementById('resetOtpCode');
        const password1 = this.shadowRoot.getElementById('resetNewPassword1');
        const password2 = this.shadowRoot.getElementById('resetNewPassword2');

        if (!otpCode.value || !otpPattern.test(otpCode.value)) {
            otpCode.classList.add('is-invalid');
            otpCode.parentElement.querySelector('.invalid-feedback').textContent = 'OTP is required';
            isValid = false;
        } else {
            otpCode.classList.remove('is-invalid');
            otpCode.parentElement.querySelector('.invalid-feedback').textContent = '';
        }

    	if (!password1.value) {
        	password1.classList.add('is-invalid');
        	password1.nextElementSibling.textContent = 'Password is required';
        	isValid = false;
    	} else {
        	password1.classList.remove('is-invalid');
        	password1.nextElementSibling.textContent = '';
    	}

        if (!password2.value) {
        	password2.classList.add('is-invalid');
        	password2.nextElementSibling.textContent = 'Password is required';
        	isValid = false;
    	} else {
        	password2.classList.remove('is-invalid');
        	password2.nextElementSibling.textContent = '';
    	}

        if ((password1.value && password2.value) && password1.value !== password2.value) {
            password1.classList.add('is-invalid');
            password2.classList.add('is-invalid');
            password1.nextElementSibling.textContent = 'Passwords do not match';
            password2.nextElementSibling.textContent = 'Passwords do not match';
            isValid = false;
        }

		loginButton.disabled = !isValid;
		return isValid;
	}

    async requestOTP(event) {
        event.preventDefault();
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const resetButton = this.shadowRoot.getElementById('resetRequestOTP');
        const resetSpinner = this.shadowRoot.getElementById('resetSpinner');
        const resetError = this.shadowRoot.getElementById('resetErrorMessage');
        const otpSection = this.shadowRoot.getElementById('resetOtpSection');
        const submitButton = this.shadowRoot.getElementById('resetSubmitButton');
        if (otpSection.style.display !== 'none' && resetButton.disabled && submitButton.disabled) return;

        resetButton.disabled = true;
        resetSpinner.style.display = 'inline-block';
        this.shadowRoot.getElementById('resetErrorMessage').textContent = '';

        try {
            this.apiFetch('/registration/basic_forgot_password', {method: 'POST', body: JSON.stringify({ "username": email })}, 'application/json', false);
            this.startTimer(60, resetButton);
            this.handleEmailInput();
        } catch (error) {
            resetError.textContent = error;
            this.shadowRoot.getElementById('resetEmail').setAttribute('aria-invalid', 'true');
            resetButton.disabled = false;
        } finally {
            resetSpinner.style.display = 'none';
            this.shadowRoot.getElementById('resetOtpCode').focus();
        }
    }

    async resetPassword(event) {
        event.preventDefault();
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const resetSpinner = this.shadowRoot.getElementById('resetSpinner');
        const resetError = this.shadowRoot.getElementById('resetErrorMessage');
        const otpSection = this.shadowRoot.getElementById('resetOtpSection');
        if (resetButton.disabled) return;

        resetButton.disabled = true;
        resetSpinner.style.display = 'inline-block';
        resetError.textContent = '';

        if (otpSection.style.display === 'none') {
            this.requestOTP(event);
            return;
        } else {
            const password2 = this.shadowRoot.getElementById('resetNewPassword2').value;
            const password1 = this.shadowRoot.getElementById('resetNewPassword1').value;
            if (password1 !== password2) {
                resetButton.disabled = false;
                resetSpinner.style.display = 'none';
                return;
            }
            const email = this.shadowRoot.getElementById('resetEmail').value;
            const otp = this.shadowRoot.getElementById('resetOtpCode').value;
            try {
                await this.apiFetch('/registration/basic_forgot_password', {method: 'POST', body: JSON.stringify({ "username": email, otp, "new_password": password1 })}, 'application/json', false);
                resetError.classList.remove('text-danger');
                resetError.classList.add('text-success');
                resetError.textContent = 'Success! Redirecting to login page...';
                setTimeout(app.router.go, 3000, '/login', false);
                //app.router.go('/login', false);
            } catch (error) {
                resetError.textContent = error;
                this.shadowRoot.getElementById('resetEmail').setAttribute('aria-invalid', 'true');
                resetButton.disabled = false;
            } finally {
                resetSpinner.style.display = 'none';
            }
        }
    }

    handleEmailInput() {
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const otpSection = this.shadowRoot.getElementById('resetOtpSection');
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        if (email) {
            otpSection.style.display = '';
            resetButton.disabled = true;
        } else {
            otpSection.style.display = 'none';
            resetButton.disabled = true;
        }
    }

    startTimer(duration, button) {
        let timer = duration, minutes, seconds;
        this.timer = setInterval(() => {
            minutes = parseInt(timer / 60, 10);
            seconds = parseInt(timer % 60, 10);

            minutes = minutes < 10 ? "0" + minutes : minutes;
            seconds = seconds < 10 ? "0" + seconds : seconds;

            button.textContent = `${minutes}:${seconds}`;

            if (--timer < 0) {
                clearInterval(this.timer);
                button.textContent = 'Send OTP';
                button.disabled = false;
            }
        }, 1000);
    }
}

customElements.define('forgot-password', ForgotPassword);