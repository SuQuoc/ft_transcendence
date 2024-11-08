import { ComponentBaseClass } from "./componentBaseClass.js";
import { PongCanvasElement } from "./pong/PongCanvasElement.js";

export class MatchPage extends ComponentBaseClass {
	constructor(tournament_name) {
		super();

		// Binds the method to this class instance so it can be used in the event listener
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
		this.canvas.addEventListener("dblclick", this.handlePongFullScreen_var);
		// protection if too fast ??!!
		window.app.match_socket.addEventListener("message", this.handleReceivedMessage_var);
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// remove event listeners
		this.canvas.removeEventListener("dblclick", this.handlePongFullScreen_var);
		window.app.match_socket.removeEventListener("message", this.handleReceivedMessage_var);
	}


	/// ----- Event Handlers ----- ///

	handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		console.log("MatchPage: handleReceivedMessage: ", data);
				
		if (data.type === "match_found") {
			// protection if too fast and or if socket open ??!!
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