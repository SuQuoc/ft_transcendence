import { ComponentBaseClass } from './componentBaseClass.js'

import { startPong } from './pong/pong.js'

export class PongPage extends ComponentBaseClass {
    connectedCallback() {
        super.connectedCallback()

        startPong(window.app.socket)
    }
    getElementHTML() {
        const template = document.createElement('template')
        template.innerHTML = `
			<scripts-and-styles></scripts-and-styles>
			<h1>Pong<h1>
		`
        return template
    }
}

customElements.define('pong-page', PongPage)
