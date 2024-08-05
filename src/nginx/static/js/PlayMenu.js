export class PlayMenu extends HTMLElement {
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
			<div>
				<button type="submit" class="btn btn-secondary w-100 mb-2">Multiplayer</button>
				<button type="submit" class="btn btn-secondary w-100">Tournament</button>
			</div>
		`;
		return template;
	}
}

customElements.define('play-menu', PlayMenu);