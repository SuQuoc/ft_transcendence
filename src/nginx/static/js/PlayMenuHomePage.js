import { ComponentBaseClass } from "./componentBaseClass.js";

export class PlayMenuHomePage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div>
				<a href="/" type="button" class="btn btn-secondary w-100 mb-2">Multiplayer</a>
				<a href="/tournament" type="button" class="btn btn-secondary w-100">Tournament</a>
			</div>
		`;
		return template;
	}
}

customElements.define('play-menu-home-page', PlayMenuHomePage);