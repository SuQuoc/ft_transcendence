import { ComponentBaseClass } from "./componentBaseClass.js";
import { PongCanvasElement } from "./pong/PongCanvasElement.js";

export class MatchPage extends ComponentBaseClass {
	constructor() {
		super();

		this.timeout_id = -1;

		// Binds the method to this class instance so it can be used in the event listener
		this.handleGameEnd_var = this.handleGameEnd.bind(this);
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
	}

	connectedCallback() {
		super.connectedCallback();

		// adding classes
		this.classList.add("d-flex", "w-100", "h-100");

		// getting elements
		this.canvas = this.root.querySelector("pong-canvas-element");
		console.log("MatchPage connectedCallback");
		
		// add event listeners
		this.canvas.addEventListener("gameend", this.handleGameEnd_var);
		if (window.app.match_socket)
			window.app.match_socket.addEventListener("message", this.handleReceivedMessage.bind(this));
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		if (this.timeout_id > 0)
			clearTimeout(this.timeout_id);

		// remove event listeners
		this.canvas.removeEventListener("gameend", this.handleGameEnd_var);
		if (window.app.match_socket)
			window.app.match_socket.removeEventListener("message", this.handleReceivedMessage_var);
	}


	/// ----- Event Handlers ----- ///

	handleGameEnd() {
		this.timeout_id = setTimeout(() => {
			this.timeout_id = -1;
			window.app.router.go("/");
		}, 20000);
	}

	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		console.log("MatchPage: handleReceivedMessage: ", data);
				
		if (data.type === "match_found") {
			if (window.app.pong_socket)
			window.app.pong_socket.send(JSON.stringify({type: "connect_to_match", match_id: data.match_id}));
		}
		else if (data.type === "error") {
			console.error("Error: handleReceivedMessage: ", data.error);
		}
		else {
			console.error("Error: handleReceivedMessage: unknown type: ", data.type);
		}
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