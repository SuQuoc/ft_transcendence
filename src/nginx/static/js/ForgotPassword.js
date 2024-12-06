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
        this.shadowRoot.getElementById('resetOtpCode').addEventListener('input', this.handleOtpInput.bind(this));
        this.shadowRoot.getElementById('resetEmail').addEventListener('input', this.checkEmailInput.bind(this));
        this.shadowRoot.getElementById('resetNewPassword1').addEventListener('input', this.handlePasswordInput.bind(this));
        this.shadowRoot.getElementById('resetNewPassword2').addEventListener('input', this.handlePasswordInput.bind(this));
        this.shadowRoot.getElementById('resetEmail').focus();
    }

    handleKeyDown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const otpField = this.shadowRoot.getElementById('resetOtpCode');
            const password1 = this.shadowRoot.getElementById('resetNewPassword1');
            const password2 = this.shadowRoot.getElementById('resetNewPassword2');

            if (otpField.value && password1.value && password2.value) {
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
                <form id="forgotPasswordForm" class="needs-validation">
                    <h3 class="text-center text-white">Forgot Password</h3>
                    <label for="resetEmail" class="form-label text-white-50">Email address</label>
                    <input name="email" id="resetEmail" type="email" class="form-control mb-3" placeholder="name@example.com" aria-describedby="resetErrorMessage" aria-required="true" autocomplete="email" required>
                    <div class="invalid-feedback mb-1">Please enter your email</div>
                    <div class="mb-3" id="resetOtpSection" style="display: none;">
                        <label for="resetOtpCode" class="form-label text-white-50">OTP Code sent to your E-Mail</label>
                        <div class="input-group">
                            <input name="otp" id="resetOtpCode" type="text" class="form-control" aria-required="true" pattern="[A-Z0-9]{16}" minlength="16" maxlength="16" autocomplete="one-time-code">
                            <button class="btn btn-custom" type="button" id="resetRequestOTP" style="min-width: 100px;" disabled>Send OTP</button>
                        </div>
                    </div>
                    <span id="resetOtpErrorMessage" class="text-danger"></span>
                    <div id="resetPasswordSection" style="display: none;">
                        <label for="resetNewPassword1" class="form-label text-white-50">New Password</label>
                        <input name="password1" id="resetNewPassword1" type="password" class="form-control mb-3" aria-required="true" autocomplete="new-password">
                        <label for="resetNewPassword2" class="form-label text-white-50">Confirm New Password</label>
                        <input name="password2" id="resetNewPassword2" type="password" class="form-control mb-3" aria-required="true" autocomplete="new-password">
                        <span id="resetPasswordErrorMessage" class="text-danger"></span>
                    </div>
                    <span id="resetErrorMessage" class="text-danger mb-3"></span>
                    <p class="text-white-50 small m-0">
                        Back to <a href="/login" class="text-decoration-none text-white" id="forgotPasswordGoToLogin">Log in</a>
                        or <a href="/signup" class="text-decoration-none text-white" id="forgotPasswordGoToSignup">Sign up</a>
                    </p>
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
        }
    }

    async resetPassword(event) {
        event.preventDefault();
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const resetSpinner = this.shadowRoot.getElementById('resetSpinner');
        const resetError = this.shadowRoot.getElementById('resetErrorMessage');
        const otpSection = this.shadowRoot.getElementById('resetOtpSection');
        const passwordSection = this.shadowRoot.getElementById('resetPasswordSection');
        if (resetButton.disabled) return;

        resetButton.disabled = true;
        resetSpinner.style.display = 'inline-block';


        //TODO: check if passwords match in a different function, should be checked on input, not submit
       /*if (otp && password1 && password2 && password1 !== password2) {
            resetError.textContent = 'Passwords do not match';
            resetButton.disabled = false;
            resetSpinner.style.display = 'none';
            return;
        }*/

        if (otpSection.style.display === 'none') {
            this.requestOTP(event);
            return;
        } else if (passwordSection.style.display === 'none') {
            this.handleOtpInput();
            return;
        } else {
            this.handlePasswordInput();
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
                //TODO: show a success message and redirect to login page after a few seconds
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

    checkEmailInput() {
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const emailPattern = /^[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
        if (email && emailPattern.test(email)) {
            resetButton.disabled = false;
        } else {
            resetButton.disabled = true;
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

    handleOtpInput() {
        const otp = this.shadowRoot.getElementById('resetOtpCode').value;
        const passwordSection = this.shadowRoot.getElementById('resetPasswordSection');
        const otpError = this.shadowRoot.getElementById('resetOtpErrorMessage');
        const otpPattern = /^[A-Z0-9a-z]{16}/;

        if (otpPattern.test(otp)) {
            passwordSection.style.display = '';
            otpError.textContent = '';
        } else {
            passwordSection.style.display = 'none';
            otpError.textContent = 'Invalid OTP';
        }
        this.updateSubmitButtonState();
    }

    handlePasswordInput() {
        const password1 = this.shadowRoot.getElementById('resetNewPassword1').value;
        const password2 = this.shadowRoot.getElementById('resetNewPassword2').value;
        const passwordError = this.shadowRoot.getElementById('resetPasswordErrorMessage');
        if (password1 && password2) {
            if (password1 === password2) {
                passwordError.textContent = '';
            } else {
                passwordError.textContent = 'Passwords do not match';
            }
        } else {
            passwordError.textContent = 'New Passwords cannot be empty';
        }
        this.updateSubmitButtonState();
    }

    updateSubmitButtonState() {
        const email = this.shadowRoot.getElementById('resetEmail').value;
        const otp = this.shadowRoot.getElementById('resetOtpCode').value;
        const password1 = this.shadowRoot.getElementById('resetNewPassword1').value;
        const password2 = this.shadowRoot.getElementById('resetNewPassword2').value;
        const resetButton = this.shadowRoot.getElementById('resetSubmitButton');
        const otpPattern = /^[A-Z0-9a-z]{16}$/;

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