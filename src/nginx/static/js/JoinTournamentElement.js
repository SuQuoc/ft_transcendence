export class JoinTournamentElement extends HTMLElement {
	// should not be needed!!!
	/* constructor() {
		super();

		this.handleJoinTournamentVar = this.handleJoinTournament.bind(this);
	} */
	// when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);

		// should not be needed!!!
	/* 	this.join_tournament_button = this.querySelector("[name='join_tournament_button']");

		// add event listeners
		this.join_tournament_button.addEventListener("click", this.handleJoinTournamentVar); */
	}

	// should not be needed!!!
	/* disconnectedCallback() {
		// remove event listeners
		this.join_tournament_button.removeEventListener("click", this.handleJoinTournamentVar);
	} */


	/// ----- Event Handlers ----- ///

	// should not be needed!!!
	/** Reroutes to the tournament lobby page */
/* 	handleJoinTournament(event) {
		console.log('join tournament handler in JoinTournamentElement');
		let tournament_name = event.target.parentElement.querySelector("[name='join_name']").innerHTML; // can be simplified because i am saving the tournament name in the parent div as well as a name
		
		//window.app.socket.send(JSON.stringify({"type": "join_tournament", "room_name": tournament_name}));
		window.app.router.go("/tournament-lobby", false, tournament_name); // false means it doesn't get added to the history
	} */

	
	// the element with the info of the tournament and a button to join it
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<div class="bg-dark d-flex flex-row align-items-center rounded-3 gap-3 p-2">
				<div class="d-flex flex-column lh-1 text-break">
					<span name="join_name" class="text-white">tournament name</span>
					<span name="join_creator" class="text-white-50 small">creator name</span>
				</div>
				<div class="d-flex flex-column align-items-center ms-auto lh-1">
					<span class="text-white-50 extra-small">PTW</span>
					<span name="join_points_to_win" class="text-white fs-5">5</span>
				</div>
				
				<div class="d-flex">
					<span name="join_current_player_num" class="text-white fs-4">1</span>
					<span class="text-white-50 fs-4">/</span>
					<span name="join_max_player_num" class="text-white fs-4">4</span>
				</div>
				<button type="button" name="join_tournament_button" class="btn btn-custom py-1 px-3">Join</button>
			</div>
		`;
		return template;
	}
}

customElements.define('join-tournament-element', JoinTournamentElement);
