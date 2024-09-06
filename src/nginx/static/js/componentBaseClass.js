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
			console.log("added event listener ComponentBaseClass");
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
			console.log("removed event listener ComponentBaseClass");
		});
	};


	/// ----- Event Handlers ----- ///
	
	// triggers a custom event when a link is clicked inside the shadow DOM,
	// the router listens for the custom event
	handleLinkClick(event) {
		event.preventDefault();
		console.log("link clicked in shadow DOM");

		const url = event.target.getAttribute("href");
		window.app.router.go(url, this.addToHistory);
	};


	// the method where the HTML of the component is defined, must be overridden
	getElementHTML() {
		throw new Error("Must override method getElementHTML");
	}
}