import { ComponentBaseClass } from "./componentBaseClass.js";

export class PlayMenu extends ComponentBaseClass {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
	};

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<div>
				<button type="submit" class="btn btn-secondary w-100 mb-2">Multiplayer</button>
				<button type="submit" class="btn btn-secondary w-100">Tournament</button>
			</div>
		`;
		return template;
	}
}

customElements.define('play-menu', PlayMenu);