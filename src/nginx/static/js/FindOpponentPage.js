import { ComponentBaseClass } from "./componentBaseClass.js";

export class FindOpponentPage extends ComponentBaseClass {
	connectedCallback() {
		super.connectedCallback();
		
		// add event listeners
		window.app.socket.addEventListener("message", this.handleSocketMessageStartPong, {once: true});
	}


	/// ----- Event Handlers ----- ///

	handleSocketMessageStartPong(event) {
		const data = JSON.parse(event.data);

		console.log("startPong event");
		console.log("data: ", data);
		if (data.type === "startPong") {
			window.app.router.go("/pong", false);
		}
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<h1>Looking for opponent<h1>
		`;
		return template;
	}
}

customElements.define('find-opponent-page', FindOpponentPage);