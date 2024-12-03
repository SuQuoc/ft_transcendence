import { Background } from "./backgroundClass.js";

export class canvasBaseClass extends HTMLElement {
	constructor() {
		super();

		// Binds the method to this class instance so it can be used in the event listener
		this.handleCanvasResize_var = this.handleCanvasResize.bind(this);
		this.handleBackgroundCanvasResize_var =
		this.handleBackgroundCanvasResize.bind(this);
	}

	connectedCallback() {
		const template = this.getElementHTML();
		const content = template.content.cloneNode(true); // true so it makes a deep copy/clone (clones other templates inside this one)
		this.appendChild(content);

		this.init(); // needs to happen after we got the html elements (which is why it is here and not in the constructor)

		// waiting for the canvas to be rendered (https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame)
		requestAnimationFrame(() => {
			this.handleCanvasResize();
			this.handleBackgroundCanvasResize();
		});

		// add event listeners
		// maybe should be this or this.canvas not window !!??
		window.addEventListener("resize", this.handleCanvasResize_var);
		window.addEventListener("resize", this.handleBackgroundCanvasResize_var);
	}

	disconnectedCallback() {
		// remove event listeners
		window.removeEventListener("resize", this.handleCanvasResize_var);
		window.removeEventListener("resize", this.handleBackgroundCanvasResize_var);
	}

	/// ----- Methods ----- ///
	/** Initializes the canvases and other objects */
	init() {
		this.player_names =		this.querySelector("#pongPlayerNames");
		this.container =		this.querySelector("#pongCanvasContainer");

		this.bg_canvas =		this.querySelector("#pongBackgroundCanvas");
		this.canvas =			this.querySelector("#pongGameCanvas");
		this.bg_ctx =			this.bg_canvas.getContext("2d");
		this.ctx =				this.canvas.getContext("2d");

		this.scale =			1;
		this.ratio =			0.6;
		this.width_unscaled =	1000;
		this.height_unscaled =	this.width_unscaled * this.ratio;

		this.background = new Background(this.width_unscaled,
										this.height_unscaled,
										50,
										"grey",
										this.bg_ctx);
	}

	/** Scales the canvas depending on the screensize and sets this.scale to the new scale. */
	scaleCanvas(ctx, canvas_width, canvas_width_unscaled) {
		this.scale = canvas_width / canvas_width_unscaled;

		ctx.scale(this.scale, this.scale);
	}

	/** Writes text on the foreground canvas.
	 * @param {string} text - The text to write on the canvas.
	 * @param {string} font - (optional: The font of the text. Default: 50px Arial)
	 * @param {string} color - (optional: The color of the text. Default: white)
	 */
	writeTextForeground(text, font = "50px Arial", color = "white") {
		this.ctx.fillStyle = color;
		this.ctx.font = font;
		this.ctx.textAlign = "center";
		this.ctx.textBaseline = "middle"; // Center text vertically
		this.ctx.fillText(text, this.width_unscaled / 2, this.height_unscaled / 2);
	}

	/** Clears the foreground canvas except for the players. (30px padding on the left and right) */
	clearTextForeground() {
		this.ctx.clearRect(30, 0, this.width_unscaled - 60, this.height_unscaled);
	}

	setNamesPosition() {
		console.log("names: ", this.player_names);
		this.player_names.style.bottom = `${this.bg_canvas.style.top}`;
		console.log("names: ", this.player_names.style.bottom);
		console.log("bg canvas: ", this.bg_canvas.style.top);
		console.log("bg canvas: ", this.bg_canvas);
	}

	/// ----- Event Handlers ----- ///

	/** Resizes the (foreground) Canvas depending on the screensize. */
	handleCanvasResize() {
		const container_width = this.container.clientWidth;
		const container_height = this.container.clientHeight;

		this.canvas.width = container_width;
		this.canvas.height = this.canvas.width * this.ratio;
		if (this.canvas.height > container_height) {
			this.canvas.height = container_height;
			this.canvas.width = this.canvas.height / this.ratio;
		}

		this.scaleCanvas(this.ctx, this.canvas.width, this.width_unscaled);
		this.player_left.draw();
		this.player_right.draw();
		this.ball.draw();
	}

	/** Resizes the background Canvas depending on the screensize. */
	handleBackgroundCanvasResize() {
		const container_width = this.container.clientWidth;
		const container_height = this.container.clientHeight;

		this.bg_canvas.width = container_width;
		this.bg_canvas.height = this.bg_canvas.width * this.ratio;
		if (this.bg_canvas.height > container_height) {
			this.bg_canvas.height = container_height;
			this.bg_canvas.width = this.bg_canvas.height / this.ratio;
		}

		this.scaleCanvas(this.bg_ctx, this.bg_canvas.width, this.width_unscaled);
		this.background.drawBackground(this.player_left.score, this.player_right.score);
		this.setNamesPosition();
	}

	getElementHTML() {
		const template = document.createElement("template");
		template.classList.add("d-flex", "flex-column", "w-100", "h-100"); // needed ??!! does this even do anything or is the match page and tournamentLobbyPage overwriting it??
		template.innerHTML = `
				<scripts-and-styles></scripts-and-styles>
				
				<div id="pongCanvasContainer" class="canvas-container d-flex justify-content-center align-items-center w-100 h-100">
					<div id="pongPlayerNames" class="d-flex w-100 bg-danger">
						<span id="pongPlayerLeft" class="text-white lh-1 bg-warning">displayname left</span>
						<span id="pongPlayerRight" class="text-white lh-1 ms-auto bg-dark">displayname right</span>
					</div>
					<canvas id="pongBackgroundCanvas" class="position-absolute bg-dark shadow" width="1000" height="600"></canvas>
					<canvas id="pongGameCanvas" class="position-absolute" width="1000" height="600"></canvas>
				</div>
			`;
		return template;
	}
}
