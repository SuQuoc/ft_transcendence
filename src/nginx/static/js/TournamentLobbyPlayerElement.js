export class TournamentLobbyPlayerElement extends HTMLElement {
	// when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<div name="lobby_player_name" class="text-white">name</div>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-player-element', TournamentLobbyPlayerElement);