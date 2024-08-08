import { ComponentBaseClass } from "./componentBaseClass.js";

export class PlayMenuHomePage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div>
				<button type="button" class="btn btn-secondary w-100 mb-2">Multiplayer</button>
				<button type="button" class="btn btn-secondary w-100">Tournament</button>
			</div>
		`;
		return template;
	}
}

customElements.define('play-menu-home-page', PlayMenuHomePage);