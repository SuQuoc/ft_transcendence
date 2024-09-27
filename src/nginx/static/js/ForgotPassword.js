// src/nginx/static/js/ForgotPassword.js
import { ComponentBaseClass } from "./componentBaseClass.js";

export class ForgotPassword extends ComponentBaseClass {
    constructor() {
        super(false);
    }

    connectedCallback() {
        super.connectedCallback();

        this.shadowRoot.getElementById('resetSubmitButton').addEventListener('click', this.resetPassword.bind(this));
        this.shadowRoot.getElementById('requestOTP').addEventListener('click', this.requestOTP.bind(this));
        this.shadowRoot.getElementById('otpCode').addEventListener('input', this.handleOtpInput.bind(this));
        this.shadowRoot.getElementById('newPassword1').addEventListener('input', this.handlePasswordInput.bind(this));
        this.shadowRoot.getElementById('newPassword2').addEventListener('input', this.handlePasswordInput.bind(this));
        this.shadowRoot.getElementById('forgotPasswordForm').addEventListener('keydown', this.handleKeyDown.bind(this));
    }

    handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const otpSectionVisible = this.shadowRoot.getElementById('otpSection').style.display !== 'none';
            const passwordSectionVisible = this.shadowRoot.getElementById('passwordSection').style.display !== 'none';

            if (!otpSectionVisible) {
                this.requestOTP(event);
            } else if (otpSectionVisible && passwordSectionVisible) {
                this.resetPassword(event);
            }
        }
    }

    getElementHTML() {
        const template = document.createElement('template');
        template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
                <form id="forgotPasswordForm">
                    <h3 class="text-center text-white">Forgot Password</h3>
                    <label for="resetEmail" class="form-label text-white-50">Email address</label>
                    <div class="input-group mb-3">
                        <input name="email" id="resetEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="errorMessage" aria-required="true" autocomplete="email">
                        <button class="btn btn-custom" type="submit" id="requestOTP" style="min-width: 100px;">Send OTP</button>
                    </div>
                    <span id="errorMessage" class="text-danger"></span>
                    <div id="otpSection" style="display: none;">
                        <label for="otpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                        <input name="otp" id="otpCode" type="text" class="form-control mb-3" aria-required="true" pattern="[A-Z0-9]{16}" minlength="16" maxlength="16" autocomplete="one-time-code">
                        <span id="otpErrorMessage" class="text-danger"></span>
                    </div>
                    <div id="passwordSection" style="display: none;">
                        <label for="newPassword1" class="form-label text-white-50">New Password</label>
                        <input name="password1" id="newPassword1" type="password" class="form-control mb-3" aria-required="true" autocomplete="new-password">
                        <label for="newPassword2" class="form-label text-white-50">Confirm New Password</label>
                        <input name="password2" id="newPassword2" type="password" class="form-control mb-3" aria-required="true" autocomplete="new-password">
                        <span id="passwordErrorMessage" class="text-danger"></span>
                    </div>
                    <p class="text-white-50 small m-0">Back to <a href="/login" class="text-decoration-none text-white">Login</a> or <a href="/signup" class="text-decoration-none text-white">Sign-up</a></p>
                    <button type="submit" class="btn btn-custom w-100" form="forgotPasswordForm" id="resetSubmitButton" disabled>Reset Password</button>
                    <div class="spinner-border text-light" role="status" id="resetSpinner" style="display: none;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </form>
            </div>
        `;
        return template;
    }

    async requestOTP(event) {
        event.preventDefault();
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const resetButton = this.shadowRoot.getElementById('requestOTP');
        const resetSpinner = this.shadowRoot.getElementById('resetSpinner');
        const resetError = this.shadowRoot.getElementById('errorMessage');
        if (resetButton.disabled) return;

        resetButton.disabled = true;
        resetSpinner.style.display = 'inline-block';

        try {
            const response = await fetch('/registration/basic_forgot_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "username": email }),
            });
            if (!response.ok) {
                throw new Error('Could not send OTP');
            }
            this.startTimer(60, resetButton);
            this.handleEmailInput();
        } catch (error) {
            console.error('Error during OTP request:', error);
            resetError.textContent = 'Could not send OTP';
            this.shadowRoot.getElementById('resetEmail').setAttribute('aria-invalid', 'true');
            resetButton.disabled = false;
        } finally {
            resetSpinner.style.display = 'none';
        }
    }

    async resetPassword(event) {
        event.preventDefault();
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const resetSpinner = this.shadowRoot.getElementById('resetSpinner');
        const resetError = this.shadowRoot.getElementById('errorMessage');
        if (resetButton.disabled) return;

        resetButton.disabled = true;
        resetSpinner.style.display = 'inline-block';

        const email = this.shadowRoot.getElementById('resetEmail').value;
        const otp = this.shadowRoot.getElementById('otpCode').value;
        const password1 = this.shadowRoot.getElementById('newPassword1').value;
        const password2 = this.shadowRoot.getElementById('newPassword2').value;

        if (password1 !== password2) {
            resetError.textContent = 'Passwords do not match';
            resetButton.disabled = false;
            resetSpinner.style.display = 'none';
            return;
        }

        try {
            const response = await fetch('/registration/basic_forgot_password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "username": email, otp, "new_password": password1 }),
            });
            if (!response.ok) {
                throw new Error('Could not change password');
            }
            app.router.go('/login', false);
        } catch (error) {
            console.error('Error during password reset:', error);
            resetError.textContent = 'Could not reset password';
            this.shadowRoot.getElementById('resetEmail').setAttribute('aria-invalid', 'true');
            resetButton.disabled = false;
        } finally {
            resetSpinner.style.display = 'none';
        }
    }

    handleEmailInput() {
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const otpSection = this.shadowRoot.getElementById('otpSection');
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        if (email) {
            otpSection.style.display = 'block';
            resetButton.disabled = true;
        } else {
            otpSection.style.display = 'none';
            resetButton.disabled = true;
        }
    }

    handleOtpInput() {
        const otp = this.shadowRoot.getElementById('otpCode').value;
        const passwordSection = this.shadowRoot.getElementById('passwordSection');
        const otpError = this.shadowRoot.getElementById('otpErrorMessage');
        const otpPattern = /^[A-Z0-9]{16}/;

        if (otpPattern.test(otp)) {
            passwordSection.style.display = 'block';
            otpError.textContent = '';
        } else {
            passwordSection.style.display = 'none';
            otpError.textContent = 'Invalid OTP';
        }
        this.updateSubmitButtonState();
    }

    handlePasswordInput() {
        const password1 = this.shadowRoot.getElementById('newPassword1').value;
        const password2 = this.shadowRoot.getElementById('newPassword2').value;
        const passwordError = this.shadowRoot.getElementById('passwordErrorMessage');
        if (password1 && password2) {
            if (password1 === password2) {
                passwordError.textContent = '';
            } else {
                passwordError.textContent = 'Passwords do not match';
            }
        } else {
            passwordError.textContent = '';
        }
        this.updateSubmitButtonState();
    }

    updateSubmitButtonState() {
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const otp = this.shadowRoot.getElementById('otpCode').value;
        const password1 = this.shadowRoot.getElementById('newPassword1').value;
        const password2 = this.shadowRoot.getElementById('newPassword2').value;
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const otpPattern = /^[A-Z0-9]{16}$/;

        if (email && otpPattern.test(otp) && password1 && password2 && password1 === password2) {
            resetButton.disabled = false;
        } else {
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