import { ComponentBaseClass } from './componentBaseClass.js';

export class PlayMenuHomePage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div>
				<a href="/match" type="button" id="playMenuGoToFindOpponent" class="btn btn-custom w-100 mb-2">Match</a>
				<a href="/tournament" type="button" id="playMenuGoToTournament" class="btn btn-custom w-100">Tournament</a>
			</div>
		`;
		return template;
	}
}

customElements.define('play-menu-home-page', PlayMenuHomePage);
