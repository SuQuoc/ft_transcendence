/**
 * Adds event listeners for links (a tags) within the shadow DOM that dispach a custom event that the router listens for.
 * You can pass a boolean to the constructor to determine if the component should add the URL to the history.
 * The default is true.
 * 
 * Makes a shadow DOM and appends the content of the template from getElementHTML() to it.
 * 
 * getElementHTML() must be overridden.
 * 
 * If you want bootstrap and custom styles, you need to add the \<scripts-and-styles\> tag to the template.
 */
export class ComponentBaseClass extends HTMLElement {
	constructor(addToHistory = true) {
		super(); // always call super() (it calls the constructor of the parent class)
		
		// adding addToHistory to the class
		this.addToHistory = addToHistory;

		// create a shadow DOM
		this.root = this.attachShadow({mode: "open"}); // open mode allows us to access the shadow DOM from outside
		this.handleLinkClick_var = this.handleLinkClick.bind(this); // bind the event handler to this instance of the class
	};

	// get's called when the component is attached to the DOM
	connectedCallback() { // HTMLElement doesn't have connectedCallback
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.root.appendChild(content); // this.root ensures that the content is appended to shadow DOM
		
		// Add event listeners to links within the shadow DOM, if there are any
		const links = this.root.querySelectorAll("a");
		if (links.length === 0)
			return;
		links.forEach(a => {
			a.addEventListener("click", this.handleLinkClick_var);
		});
	};

	// get's called when the component is removed from the DOM
	disconnectedCallback() { // HTMLElement doesn't have disconnectedCallback
		// remove event listeners (not sure if necessary), if there are any
		const links = this.root.querySelectorAll("a");
		if (links.length === 0)
			return;
		links.forEach(a => {
			a.removeEventListener("click", this.handleLinkClick_var);
		});
	};


	/// ----- Event Handlers ----- ///
	
	// triggers a custom event when a link is clicked inside the shadow DOM,
	// the router listens for the custom event
	handleLinkClick(event) {
		event.preventDefault();

		const url = event.target.getAttribute("href");
		window.app.router.go(url, this.addToHistory);
	};


	// the method where the HTML of the component is defined, must be overridden
	getElementHTML() {
		throw new Error("Must override method getElementHTML");
	};

	/**
	 * Validates the token and refreshes it if necessary.
	 * @returns {Promise<boolean>}
	 */
	async validateToken() {
		try {
			const response = await fetch("/registration/verify_token", {
				method: "GET",
				headers: {
					"Content-Type": "application/json"
				},
				credentials: "include"
			});

			if (response.status !== 200) {
				throw new Error("Token is invalid");
			}

			return true;
		} catch (error) {
			console.error("Error validating token, trying to refresh: ", error.message);
			try {
				const refreshResponse = await fetch("/registration/refresh_token", {
					method: "GET",
					headers: {
						"Content-Type": "application/json"
					},
					credentials: "include"
				});

				if (refreshResponse.status !== 200) {
					throw new Error("Error refreshing token");
				}
				return true;
			} catch (refreshError) {
				console.error("Error refreshing token:", refreshError.message);
				return false;
			}
		}
	};

	/**
	 * Makes an API call with the given URL and options.
	 * important: please only use if you have a valid token, otherwise use regular fetch
	 *
	 * @param {string} url - The URL to make the API call to.
	 * @param {object} options - The options for the fetch call, e.g. method (GET, POST), body.
	 * @param {string} type - The content type of the request.
	 * @returns {object} - The response from the API call.
	 */
	async apiFetch(url, options = {}, type = "application/json") {
		// Validate the token before making the API call
		const tokenValid = await this.validateToken();
		if (!tokenValid) {
			throw new Error("Unable to refresh token");
		}

		// Set headers conditionally
		const headers = {
			...options.headers,
		};
		if (!(options.body instanceof FormData)) {
			headers["Content-Type"] = type;
		}

		// Make the API call
		const response = await fetch(url, {
			...options,
			credentials: "include", // Ensure cookies are sent with the request
			headers: headers
		});

		// Handle response
		if (!response.ok) {
			throw new Error(`API call failed: ${response.statusText}`);
		}

		return response.json();
	};

	/*
	async apiFetch(url, options = {}, type = "application/json") {
		// Validate the token before making the API call
		const tokenValid = await this.validateToken();
		if (!tokenValid) {
			throw new Error("Unable to refresh token");
		}

		// Make the API call
		const response = await fetch(url, {
			...options,
			credentials: "include", // Ensure cookies are sent with the request
			headers: {
				...options.headers,
				"Content-Type": type
			}
		});

		// Handle response
		if (!response.ok) {
			throw new Error(`API call failed: ${response.statusText}`);
		}

		return response.json();
	};
	 */


}