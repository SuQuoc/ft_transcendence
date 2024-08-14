import { ComponentBaseClass } from "./componentBaseClass.js";

export class TournamentLobbyPage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div>Tournament Lobby<div>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-page', TournamentLobbyPage);