// Update the SignupPage class
import { ComponentBaseClass } from "./componentBaseClass.js";

export class SignupPage extends ComponentBaseClass {
	constructor() {
		super();
	}

	connectedCallback() {
		super.connectedCallback();
		this.shadowRoot.getElementById('signupForm').addEventListener('submit', this.signup.bind(this));
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
            <scripts-and-styles></scripts-and-styles>
            <div class="p-3 rounded-3 bg-dark">
                <form id="signupForm">
                    <h3 class="text-center text-white">Signup</h3>
                    <!-- Email -->
                    <label for="signupEmail" class="form-label text-white-50">Email address</label>
                    <input name="email"
                        id="signupEmail"
                        type="email"
                        class="form-control"
                        placeholder="name@example.com"
                        aria-describedby="signupEmailHelp"
                    />
                    <div class="form-text text-white-50 mb-3" id="signupEmailHelp">
                        We'll never share your email with a third party .....probably
                    </div>
                    <!-- first Password -->
                    <label for="signupPassword1" class="form-label text-white-50">Password</label>
                    <input name="password"
                        id="signupPassword1"
                        type="password"
                        class="form-control mb-1"
                    />
                    <!-- second Password -->
                    <label for="signupPassword2" class="form-label text-white-50">Password again</label>
                    <input name="password2"
                        id="signupPassword2"
                        type="password"
                        class="form-control mb-3"
                    />
                    <!-- change to login page -->
                    <p class="text-white-50 small m-0">Already signed up?
                        <a href="/login" class="text-decoration-none text-white">
                            Log in
                        </a>
                        here!
                    </p>
                    <button type="submit" class="btn btn-secondary w-100" form="signupForm">Sign up</button>
                </form>
            </div>
        `;
		return template;
	}

	async signup(event) {
		event.preventDefault();
		const signupButton = this.shadowRoot.querySelector('button[type="submit"]');
		signupButton.disabled = true;

		const email = this.shadowRoot.getElementById('signupEmail').value;
		const password = this.shadowRoot.getElementById('signupPassword1').value;
		const password2 = this.shadowRoot.getElementById('signupPassword2').value;

		if (password !== password2) {
			console.error('Passwords do not match');
			signupButton.disabled = false;
			return;
		}

		try {
			const response = await fetch('/registration/signup', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username: email, password })
			});

			if (!response.ok) {
				throw new Error('Signup failed');
			}
			window.app.userData.username = email;
			window.app.userData.email = email;

			app.router.go('/');
		} catch (error) {
			console.error('Error during signup:', error);
		} finally {
			signupButton.disabled = false;
		}
	}
}

customElements.define('signup-page', SignupPage);