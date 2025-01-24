export class JoinTournamentElement extends HTMLElement {
	// when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);
	}

	
	// the element with the info of the tournament and a button to join it
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<div class="bg-dark d-flex flex-row align-items-center rounded-3 gap-3 p-2">
				<div class="d-flex flex-column lh-1 text-break">
					<span name="join_name" class="text-white">tournament name</span>
					<span name="join_creator" class="text-secondary small">creator name</span>
				</div>
				<div class="d-flex flex-column align-items-center ms-auto lh-1">
					<span class="text-secondary extra-small">PTW</span>
					<span name="join_points_to_win" class="text-white fs-5">5</span>
				</div>
				
				<div class="d-flex">
					<span name="join_current_player_num" class="text-white fs-4">1</span>
					<span class="text-secondary fs-4">/</span>
					<span name="join_max_player_num" class="text-white fs-4">4</span>
				</div>
				<button type="button" name="join_tournament_button" class="btn btn-custom py-1 px-3">Join</button>
			</div>
		`;
		return template;
	}
}

customElements.define('join-tournament-element', JoinTournamentElement);
