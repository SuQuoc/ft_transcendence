import { ComponentBaseClass } from "./componentBaseClass.js";
import { PongCanvasElement } from "./pong/PongCanvasElement.js";

export class MatchPage extends ComponentBaseClass {
	constructor() {
		super();

		this.handlePongFullScreen_var = this.handlePongFullScreen.bind(this);
	}

	connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "w-100", "h-100");

		// getting elements
		this.canvas = this.root.querySelector("pong-canvas-element");
		console.log("MatchPage connectedCallback");
		
		// add event listeners
		this.canvas.addEventListener("dblclick", this.handlePongFullScreen_var);
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// remove event listeners
		this.canvas.removeEventListener("dblclick", this.handlePongFullScreen_var);
	}



	/// ----- Event Handlers ----- ///

	handlePongFullScreen() {
		if (this.canvas.requestFullscreen) {
			this.canvas.requestFullscreen();
		} else if (this.canvas.mozRequestFullScreen) { // Firefox
			this.canvas.mozRequestFullScreen();
		} else if (this.canvas.webkitRequestFullscreen) { // Chrome, Safari and Opera
			this.canvas.webkitRequestFullscreen();
		} else if (this.canvas.msRequestFullscreen) { // IE/Edge
			this.canvas.msRequestFullscreen();
		}

		this.canvas.handleCanvasResize();
		this.canvas.handleBackgroundCanvasResize();
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<pong-canvas-element class="d-flex flex-grow-1 bg-custom w-100 h-100 p-lg-4 p-md-3 p-1"></pong-canvas-element>
		`;
		return template;
	}
}

customElements.define('match-page', MatchPage);