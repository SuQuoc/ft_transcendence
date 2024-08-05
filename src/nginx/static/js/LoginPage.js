export class LoginPage extends HTMLElement {
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
	};
	

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
						<a href="/signup" class="text-decoration-none">
							<span class="text-white">Sign up</span> 
						</a>
						here!
					</p>
					<button type="submit" class="btn btn-secondary w-100">Log in</button>
				</form>
			</div>
		`;
		return template;
	}
}

customElements.define('login-page', LoginPage);