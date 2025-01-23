export class StatisticTournamentElement extends HTMLElement {
	constructor(loser_name, winner_name, loser_score, winner_score, date) {
		super();

		// getting template of the element
		const template = this.getElementHTML();
		this.content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)

		// adding the info
		this.content.querySelector("[name='stats_loser_name']").innerText = loser_name;
		this.content.querySelector("[name='stats_loser_score']").innerText = loser_score;
		this.content.querySelector("[name='stats_winner_score']").innerText = winner_score;
		this.content.querySelector("[name='stats_winner_name']").innerText = winner_name;
		this.content.querySelector("[name='stats_date']").innerText = date;
	}

	// when the component is attached to the DOM
	connectedCallback() {
		this.appendChild(this.content);
	}


	/// ----- Methods ----- ///
	
	highlightUser() {
		let loser_name = this.content.querySelector("[name='stats_loser_name']");
		let winner_name = this.content.querySelector("[name='stats_winner_name']");

		if (loser_name.innerText === window.app.userData.username)
			loser_name.classList.add("fw-bold");
		else
			winner_name.classList.add("fw-bold");
	}


	// the element with the info of the tournament and a button to join it
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<div class="d-flex flex-column">
				<div class="d-flex align-items-center justify-content-between bg-dark rounded-3 gap-3 p-2">
					<div class="d-flex flex-column lh-1 text-break">
						<span name="stats_loser_name" class="text-white">displayname</span>
						<span class="text-nowrap text-secondary small">loser</span>
					</div>
					
					<div class="d-flex">
						<span name="stats_loser_score" class="text-white fs-4">1</span>
						<span class="text-secondary fs-4">/</span>
						<span name="stats_winner_score" class="text-white fs-4">5</span>
					</div>
					
					<div class="d-flex flex-column lh-1 text-break">
						<span name="stats_winner_name" class=" ms-auto text-white">displayname</span>
						<span class="text-nowrap text-secondary ms-auto small">winner</span>
					</div>
				</div>
				<span name="stats_date" class="text-secondary ms-2 small">2024-11-17</span>
			</div>
		`;
		return template;
	}
}

customElements.define('stat-tournament-element', StatisticTournamentElement);
