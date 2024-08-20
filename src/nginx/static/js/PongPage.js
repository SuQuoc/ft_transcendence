import { ComponentBaseClass } from "./componentBaseClass.js";

export class PongPage extends ComponentBaseClass {
	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<h1>Pong<h1>
		`;
		return template;
	}
}

customElements.define('pong-page', PongPage);