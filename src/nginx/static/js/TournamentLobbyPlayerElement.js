export class TournamentLobbyPlayerElement extends HTMLElement {
	// when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);
		this.classList.add("d-flex", "align-items-center", "w-100", "gap-2");

		// getting elements
		this.name = this.querySelector("[name='lobby_player_name']");
        this.wins = this.querySelector("[name='lobby_wins']");
	}

	/// ----- Methods ----- ///

	makeNameBold() {
		this.name.classList.add("fw-bold");
	}

	greyOutPlayer() {
		this.name.classList.add("text-white-50");
		this.wins.classList.add("text-white-50");
	}

	incrementWins() {
		let wins = parseInt(this.wins.innerText, 10);
        wins += 1;
        this.wins.innerText = wins; 
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<img src="/media_url/profile_images/default_avatar.png"
				onerror='this.src = src="/media_url/profile_images/default_avatar.png"'
				alt="Profile image"
				class="extra-small-profile-image m-0"
				name="lobby_player_avatar"
			>
			<span name="lobby_player_name" class="text-break lh-1">name</span>
			<div class="d-flex flex-column align-items-center ms-auto lh-1">
				<span class="text-white-50 extra-small">wins</span>
				<span name="lobby_wins" class="fs-5">0</span>
			</div>
		`;
		return template;
	}
}

customElements.define('tournament-lobby-player-element', TournamentLobbyPlayerElement);