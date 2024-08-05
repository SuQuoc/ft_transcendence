export class SignupPage extends HTMLElement {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
		
		// create a shadow DOM(?) 
		this.root = this.attachShadow({mode: "open"}); // open mode allows us to access the shadow DOM from outside
	};

	// get's called when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.root.appendChild(content); // this.root ensures that the content is appended to shadow DOM
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div class="p-3 rounded-3 bg-dark">
				<form id="signupForm">
					<h3 class="text-center text-white">Signup</h3>
					<!-- Username -->
					<label for="signupUser" class="form-label text-white-50">Username</label>
					<input name="username"
						id="signupUser"
						type="text"
						class="form-control mb-3"
					/>
					<!-- Email -->
					<label for="signupEmail" class="form-label text-white-50">Email adress</label>
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
						<a href="/login" class="text-decoration-none">
							<span class="text-white">Log in</span> 
						</a>
						here!
					</p>
					<button type="submit" class="btn btn-secondary w-100">Sign up</button>
				</form>
			</div>
		`;
		return template;
	}
}

customElements.define('signup-page', SignupPage);