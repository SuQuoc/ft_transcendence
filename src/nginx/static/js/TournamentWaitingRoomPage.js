import { ComponentBaseClass } from './componentBaseClass.js';

// TODO: add a loading screen instead of text (not important)

// The function that sets the route to this page also makes an event listener that listens for a message from the game server
// that redirects the client to the tournament lobby or the joinTournament page.
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
