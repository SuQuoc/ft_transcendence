// should be in different file!!!
export class ScriptsAndStyles extends HTMLElement {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
	};
	
	// when the component is attached to the DOM
	connectedCallback() {
		const template = document.getElementById("scripts-and-styles-template");
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);
	}
}

customElements.define('scripts-and-styles', ScriptsAndStyles);



export class PlayMenu extends HTMLElement {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
		
		// create a shadow DOM(?) 
		this.root = this.attachShadow({mode: "open"}); // open mode allows us to access the shadow DOM from outside
	};

	// when the component is attached to the DOM
	connectedCallback() {
		const template = document.getElementById("play-menu-template");
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.root.appendChild(content); // this.root ensures that the content is appended to shadow DOM
	}
}

customElements.define('play-menu', PlayMenu);