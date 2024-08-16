import { ComponentBaseClass } from "./componentBaseClass.js";

export class TournamentWaitingRoomPage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<h1>Tournament Waiting Room<h1>
		`;
		return template;
	}
}

customElements.define('tournament-waiting-room-page', TournamentWaitingRoomPage);