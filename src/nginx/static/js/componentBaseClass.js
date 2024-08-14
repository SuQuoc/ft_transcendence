/**
 * Adds event listeners for links (a) within the shadow DOM that dispach a custom event that the router listens for.
 * 
 * Makes a shadow DOM and appends the content of the template from getElementHTML() to it.
 * 
 * getElementHTML() must be overridden.
 * 
 * If you want bootstrap and custom styles, you need to add the \<scripts-and-styles\> tag to the template.
 */
export class ComponentBaseClass extends HTMLElement {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
		
		// create a shadow DOM
		this.root = this.attachShadow({mode: "open"}); // open mode allows us to access the shadow DOM from outside
	};

	// get's called when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.root.appendChild(content); // this.root ensures that the content is appended to shadow DOM
		
		// Add event listeners to links within the shadow DOM, if there are any
		const links = this.root.querySelectorAll("a");
		if (links.length === 0)
			return;
		links.forEach(a => {
			a.addEventListener("click", this.handleLinkClick);
			console.log("added event listener ComponentBaseClass");
		});
	};

	// get's called when the component is removed from the DOM
	disconnectedCallback() {
		// remove event listeners (not sure if necessary), if there are any
		const links = this.root.querySelectorAll("a");
		if (links.length === 0)
			return;
		links.forEach(a => {
			a.removeEventListener("click", this.handleLinkClick);
			console.log("removed event listener ComponentBaseClass");
		});
	};

	// triggers a custom event when a link is clicked inside the shadow DOM,
	// the router listens for the custom event
	handleLinkClick(event) {
		event.preventDefault();
		console.log("link clicked in shadow DOM");

		const url = event.target.getAttribute("href");
		console.log("url: ", url);
		console.log("event: ", event);
		console.log("target: ", event.target);
		this.dispatchEvent(new CustomEvent("change-route-custom-event", { // the router listens for this event
			bubbles: true,
			composed: true,
			detail: { url }
		}));
	};

	// the method where the HTML of the component is defined, must be overridden
	getElementHTML() {
		throw new Error("Must override method getElementHTML");
	}
}