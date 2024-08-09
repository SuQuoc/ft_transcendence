export class ScriptsAndStyles extends HTMLElement {
	constructor() {
		super(); // always call super() (it calls the constructor of the parent class)
	};
	
	// when the component is attached to the DOM
	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);
	}

	getElementHTML() {
		const template = document.createElement('template');
		template.innerHTML = `
			<!-- Bootstrap CSS -->
				<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
				rel="stylesheet"
				integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
				crossorigin="anonymous"/>
			<!-- Custom CSS -->
				<link href="../css/template.css" rel="stylesheet"/>
				
			<!-- Bootstrap Bundle with Popper -->
				<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
					integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
					crossorigin="anonymous"
					defer></script>
			<!-- Custom js -->
			<!-- The 'type="module"' means that the file will be loaded as a module.
				This means every variables we define within that file will not be a global variable for the whole page. Just for that file. And that file can export and import other things as well.-->
				<script src="../app.js" defer type="module"></script>
		`;
		return template;
	}
}

customElements.define('scripts-and-styles', ScriptsAndStyles);
