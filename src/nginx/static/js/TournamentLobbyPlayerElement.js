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
			<div class="d-flex align-items-center gap-2">
				<img src="https://i.pravatar.cc/150?img=52"
					alt="Profile image"
					class="rounded-circle lobby-player-avatar"
					name="lobby_player_avatar"
				>
				<span name="lobby_player_name">name</span>
			</div>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-player-element', TournamentLobbyPlayerElement);