import { ComponentBaseClass } from "./componentBaseClass.js";

export class LoginPage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="loginForm">
					<!-- Email -->
					<h3 class="text-center text-white">Login</h3>
					<label for="loginEmail" class="form-label text-white-50">Email adress</label>
					<input name="email"
						id="loginEmail"
						type="email"
						class="form-control"
						placeholder="name@example.com"
						aria-describedby="loginEmailHelp">
					<div class="form-text text-white-50 mb-3" id="loginEmailHelp">We'll never share your email with a
						third party.....</div>
					<!-- first Password -->
					<label for="loginPassword" class="form-label text-white-50">Password</label>
					<input name="password"
						id="loginPassword"
						type="password"
						class="form-control mb-3">
					<!-- change to signup page -->
					<p class="text-white-50 small m-0">No account yet? 
						<a href="/signup" class="text-decoration-none text-white">
							Sign up 
						</a>
						here!
					</p>
					<button type="submit" class="btn btn-secondary w-100" form="loginForm">Log in</button>
				</form>
			</div>
		`;
		return template;
	}
}

customElements.define('login-page', LoginPage);