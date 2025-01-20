// Update the LoginPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	constructor() {
		super(false); // false because the componentBaseClass makes event listeners for a tags (links) and we don't want to add /login to the history
		this.otpRequestTimer = null;
		this.otpRequestCooldown = 60;
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById("loginEmail").focus();
		this.shadowRoot
			.getElementById("loginSubmitButton")
			.addEventListener("click", this.login.bind(this));
		this.shadowRoot
			.getElementById("loginForm")
			.addEventListener("submit", this.login.bind(this));
		this.shadowRoot
			.getElementById("loginForm")
			.addEventListener("input", this.validateForm.bind(this));
		this.shadowRoot
			.getElementById("requestOtpButton")
			.addEventListener("click", this.requestNewOtp.bind(this));
		this.shadowRoot
			.getElementById("loginSwitchBackupCode")
			.addEventListener("change", (event) => {
				const loginBackupSection = this.shadowRoot.getElementById(
					"loginBackupSection"
				);
				const loginOTPSection = this.shadowRoot.getElementById("loginOtpSection");
				loginBackupSection.style.display = event.target.checked
					? "block"
					: "none";
				loginOTPSection.style.display = event.target.checked
					? "none"
					: "block";
				this.validateForm();
			});
		const formFields = this.root.querySelectorAll("#loginForm > input");
		if (formFields.length === 0) return;
		for (const inputField of formFields) {
			inputField.addEventListener("keydown", (event) => {
				if (event.key === "Enter") {
					this.login(event);
				}
			});
		}
	}

	getElementHTML() {
		const template = document.createElement("template");
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark" style="max-width: 300px;">
				<h3 class="text-center text-white">Login</h3>
				<form id="42LoginForm" method="post" enctype="application/x-www-form-urlencoded" target="_self" action="/registration/oauthtwo_send_authorization_request">
					<input type="hidden" name="next_step" value="login">
					<label for="loginWith42" class="form-label text-white-50">Only for 42 students</label>
					<button id="loginWith42" class="btn btn-custom w-100 mb-3" type="submit">Login with 42</button>
				</form>
				<hr class="text-white-50">
				<form id="loginForm" class="d-flex flex-column needs-validation gap-3">
					<div>
						<label for="loginEmail" class="form-label text-white-50">Email address</label>
						<input name="email" id="loginEmail" type="email" class="form-control" placeholder="name@example.com" aria-describedby="errorMessage" aria-required="true" required>
						<div class="invalid-feedback mb-1">Please enter your email</div>
					</div>
					<div>
						<label for="loginPassword" class="form-label text-white-50">Password</label>
						<input name="password" id="loginPassword" type="password" class="form-control" aria-describedby="errorMessage" aria-required="true" required>
						<div class="invalid-feedback mb-1">Please enter your password</div>
					</div>
					<div class="form-check form-switch" id="backupCodeSwitch" style="display: none;">
  						<input class="form-check-input" type="checkbox" role="switch" id="loginSwitchBackupCode">
  						<label class="form-check-label text-white" for="loginSwitchBackupCode">Login with backup code</label>
					</div>
					<div id="loginOtpSection" style="display: none;">
						<label for='loginOtpCode' class="form-label text-white-50">OTP Code sent to your E-Mail</label>
						<div class="input-group">
							<input name="otp" id='loginOtpCode' type="text" class="form-control" aria-required="true" pattern="[A-Za-z0-9]{16}" minlength="16" maxlength="16">
							<button id="requestOtpButton" class="btn btn-custom" type="button">New OTP</button>
						</div>
						<span id="otpErrorMessage" class="text-danger"></span>
					</div>
					<div id="loginBackupSection" style="display: none;">
						<div class="mb-2">
							<span class="text-warning">What's this?</span><br>
							<span class="text-white">If you have lost access to your Email address, you can log in with one of your backup codes.</span>
						</div>
						<label for='loginBackupCode' class="form-label text-white-50">Your backup code</label>
						<input name="backup_code" id='loginBackupCode' type="text" class="form-control" aria-required="true" pattern="[A-Za-z0-9]{32}" minlength="32" maxlength="32">
						<span id="BackupErrorMessage" class="text-danger"></span>
					</div>
					<div>
						<span id="errorMessage" class="text-danger d-block mb-2"></span>
						<p class="text-white-50 small m-0"><a href="/forgot-password" class="text-decoration-none text-white" id="forgotPassword">Forgot Password?</a></p>
						<p class="text-white-50 small mb-1">No account yet? <a href="/signup" class="text-decoration-none text-white" id="loginGoToSignup">Sign up</a> here!</p>
						<button type="submit" class="btn btn-custom w-100" form="loginForm" disabled id="loginSubmitButton">Log in</button>
						<div class="spinner-border text-light" role="status" id="loginSpinner" style="display: none;">
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
			email.setAttribute("aria-invalid", "true");
			return false;
		}
		email.removeAttribute("aria-invalid");
		return true;
	}

	validateForm() {
		const email = this.shadowRoot.getElementById("loginEmail");
		const password = this.shadowRoot.getElementById("loginPassword");
		const otpCode = this.shadowRoot.getElementById("loginOtpCode");
		const otpSection = this.shadowRoot.getElementById("loginOtpSection");
		const loginButton = this.shadowRoot.getElementById("loginSubmitButton");

		const otpPattern = /^[A-Za-z0-9]{16}$/;
		const emailValid = this.validateEmail(email);

		let isValid = true;

		if (!email.value || !emailValid) {
			email.classList.add("is-invalid");
			email.nextElementSibling.textContent = "Email is required";
			email.nextElementSibling.classList.add("invalid-feedback");
			isValid = false;
		} else {
			email.classList.remove("is-invalid");
			email.nextElementSibling.textContent = "";
			email.nextElementSibling.classList.remove("invalid-feedback");
		}

		if (!password.value) {
			password.classList.add("is-invalid");
			password.nextElementSibling.textContent = "Password is required";
			isValid = false;
		} else {
			password.classList.remove("is-invalid");
			password.nextElementSibling.textContent = "";
		}

		if (
			otpSection.style.display === "block" &&
			!otpPattern.test(otpCode.value)
		) {
			otpCode.classList.add("is-invalid");
			isValid = false;
		} else if (otpSection.style.display === "block") {
			otpCode.classList.remove("is-invalid");
		}

		loginButton.disabled = !isValid;
		return isValid;
	}

	async login(event) {
		event.preventDefault();
		if (!this.validateForm()) {
			return;
		}
		const loginButton = this.shadowRoot.getElementById("loginSubmitButton");
		const loginSpinner = this.shadowRoot.getElementById("loginSpinner");
		const loginError = this.shadowRoot.getElementById("errorMessage");
		loginButton.style.display = "none";
		loginSpinner.style.display = "inline-block";
		loginError.textContent = "";

		const email = this.shadowRoot.getElementById("loginEmail").value;
		const password = this.shadowRoot.getElementById("loginPassword").value;
		const backupCodeSwitch = this.shadowRoot.getElementById("backupCodeSwitch");

		if (backupCodeSwitch.style.display !== "none" && this.shadowRoot.getElementById("loginSwitchBackupCode").checked) {
			try {
				const backupCode = this.shadowRoot.getElementById("loginBackupCode").value;
				await this.apiFetch("/registration/backup_login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ username: email, password, backup_code: backupCode }),
				}, "application/json", false);
				await app.router.go("/", false);
				return;
			} catch (error) {
				loginError.textContent = error;
				this.shadowRoot
					.getElementById("loginEmail")
					.setAttribute("aria-invalid", "true");
				this.shadowRoot
					.getElementById("loginPassword")
					.setAttribute("aria-invalid", "true");
				loginButton.style.display = "block";
				loginSpinner.style.display = "none";
				return;
			}
		}

		if (
			this.shadowRoot.getElementById("loginOtpSection").style.display === "none"
		) {
			try {
				const loginResponse = await fetch("/registration/basic_login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ username: email, password }),
				});

				if (!loginResponse.ok) {
					const responseData = await loginResponse.text();
					const errorMessage = responseData
						? Object.values(JSON.parse(responseData))[0]
						: "An unknown error occurred";
					throw new Error(errorMessage);
				}
				this.shadowRoot.getElementById("loginOtpSection").style.display =
					"block";
				backupCodeSwitch.style.display = "block";
				this.startOtpRequestCooldown();
				this.shadowRoot.getElementById("loginOtpCode").focus();
			} catch (error) {
				loginError.textContent = error;
				this.shadowRoot
					.getElementById("loginEmail")
					.setAttribute("aria-invalid", "true");
				loginButton.style.display = "block";
				backupCodeSwitch.style.display = "none";
			} finally {
				loginButton.style.display = "block";
				loginSpinner.style.display = "none";
			}
		} else {
			try {
				const otp = this.shadowRoot.getElementById("loginOtpCode").value;
				const loginResponse = await fetch("/registration/basic_login", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ username: email, password, otp }),
				});

				if (!loginResponse.ok) {
					const responseData = await loginResponse.text();
					const errorMessage = responseData
						? Object.values(JSON.parse(responseData))[0]
						: "An unknown error occurred";
					throw new Error(errorMessage);
				}
				window.app.userData = window.app.userData || {};
				window.app.userData.email = email;

				// Check if the user already has a displayname
				const displaynameResponse = await fetch("/um/profile", {
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				});

				const displaynameData = await displaynameResponse.json();
				// Redirects to the home page if the user already has a displayname or to the select displayname page if they don't
				if (!displaynameResponse.ok || displaynameData.displayname === "") {
					await app.router.go("/displayname", false);
					console.log("displayname not ok:", displaynameResponse);
				} else {
					window.app.userData.username = displaynameData.displayname;
					if (displaynameData.image) {
						window.app.userData.profileImage = displaynameData.image;
					}
					await app.router.go("/", false);
				}
			} catch (error) {
				loginError.textContent = error;
				this.shadowRoot
					.getElementById("loginEmail")
					.setAttribute("aria-invalid", "true");
				this.shadowRoot
					.getElementById("loginPassword")
					.setAttribute("aria-invalid", "true");
				loginButton.style.display = "block";
			} finally {
				loginSpinner.style.display = "none";
			}
		}
	}

	async requestNewOtp() {
		const email = this.shadowRoot.getElementById("loginEmail").value;
		const password = this.shadowRoot.getElementById("loginPassword").value;

		try {
			const response = await fetch("/registration/basic_login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ username: email, password }),
			});

			if (!response.ok) {
				const responseData = await response.text();
				const errorMessage = responseData
					? Object.values(JSON.parse(responseData))[0]
					: "An unknown error occurred";
				throw new Error(errorMessage);
			}
			this.startOtpRequestCooldown();
		} catch (error) {
			this.shadowRoot.getElementById("otpErrorMessage").textContent = error;
		}
	}

	startOtpRequestCooldown() {
		const requestOtpButton = this.shadowRoot.getElementById("requestOtpButton");
		requestOtpButton.setAttribute("disabled", "");
		let remainingTime = this.otpRequestCooldown;

		this.otpRequestTimer = setInterval(() => {
			if (remainingTime > 0) {
				requestOtpButton.textContent = `${remainingTime}s`;
				remainingTime--;
			} else {
				clearInterval(this.otpRequestTimer);
				requestOtpButton.removeAttribute("disabled");
				requestOtpButton.textContent = "New OTP";
			}
		}, 1000);
	}
}

customElements.define("login-page", LoginPage);
