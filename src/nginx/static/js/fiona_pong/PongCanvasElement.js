import { Ball } from './ballClass.js';
import { Player } from './playerClass.js';
import { Background } from './backgroundClass.js';

export class PongCanvasElement extends HTMLElement {
	constructor() {
		super();

		// Binds the method to this class instance so it can be used in the event listener
		this.handleCanvasResize_var = this.handleCanvasResize.bind(this);
		this.handleBackgroundCanvasResize_var = this.handleBackgroundCanvasResize.bind(this);
		this.handlePlayerMoveKey_var = this.handlePlayerMoveKey.bind(this);
		this.handlePlayerMoveTouch_var = this.handlePlayerMoveTouch.bind(this);
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
		
		console.log('canvas.width: ', this.canvas.width);
		console.log('canvas.height: ', this.canvas.height);

		// add event listeners
		// maybe should be this or this.canvas not window !!??
		window.addEventListener('resize', this.handleCanvasResize_var);
		window.addEventListener('resize', this.handleBackgroundCanvasResize_var);
		window.addEventListener('keydown', this.handlePlayerMoveKey_var);
		this.addEventListener('touchmove', this.handlePlayerMoveTouch_var);
		this.addEventListener('touchstart', this.handlePlayerMoveTouch_var);
	}

	disconnectedCallback() {
		// remove event listeners
		window.removeEventListener('resize', this.handleCanvasResize_var);
		window.removeEventListener('resize', this.handleBackgroundCanvasResize_var);
		window.removeEventListener('keydown', this.handlePlayerMoveKey_var);
		this.removeEventListener('touchmove', this.handlePlayerMoveTouch_var);
		this.removeEventListener('touchstart', this.handlePlayerMoveTouch_var);
	}


	/// ----- Methods ----- ///
	/** Initializes the canvases and other objects */
	init() {
		let player_x = 10;
		let player_y = 0;
		let player_width = 10;
		let player_height = 60;
		let player_speed = 10;
		let player_color = 'white';
		let ball_size = 10;

		this.container =		this.querySelector('#pongCanvasContainer');
		this.bg_canvas = 		this.querySelector('#pongBackgroundCanvas');
		this.canvas =			this.querySelector('#pongGameCanvas');
		this.bg_ctx = 			this.bg_canvas.getContext('2d');
		this.ctx =				this.canvas.getContext('2d');
		this.scale =			1;
		this.ratio =			0.6;
		this.width_unscaled =	1000;
		this.height_unscaled =	this.width_unscaled * this.ratio;

		this.player_left =	new Player(player_x, player_y, player_width, player_height, player_speed, player_color);
		this.player_right =	new Player(this.width_unscaled - player_x - player_width,
										player_y, player_width, player_height, player_speed, player_color);
		this.ball =			new Ball((this.width_unscaled / 2) - (ball_size / 2), (this.height_unscaled / 2) - (ball_size / 2), ball_size, ball_size);
		this.background = 	new Background(this.width_unscaled, this.height_unscaled, 50, 'grey', '50px Arial');
	}

	scaleCanvas(ctx, canvas_width, canvas_width_unscaled) {
		const scale = canvas_width / canvas_width_unscaled;
		this.scale = scale;
	
		ctx.scale(scale, scale);
	}
	

	/// ----- Event Handlers ----- ///

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
		this.player_left.draw(this.ctx);
		this.player_right.draw(this.ctx);
		this.ball.draw(this.ctx, 'white');
	}
	
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
		this.background.drawBackground(this.bg_ctx, '0', '0');
	}
	
	handlePlayerMoveKey(event) {
		const keys = new Set(['ArrowUp', 'ArrowDown', 'w', 's']);
	
		if (keys.has(event.key)) {
			switch (event.key) {
				case 'ArrowUp':
					this.player_right.moveUp(this.ctx);
					break;
				case 'ArrowDown':
					this.player_right.moveDown(this.ctx, this.height_unscaled);
					break;
				case 'w':
					this.player_left.moveUp(this.ctx);
					break;
				case 's':
					this.player_left.moveDown(this.ctx, this.height_unscaled);
					break
			}
		}
	}
	handlePlayerMoveTouch(event) {
		let touch_y = event.touches[0].clientY;
		let player_middle = this.player_right.height * this.scale / 2;
		let y_min = this.canvas.offsetTop + player_middle;
		let y_max = this.canvas.offsetTop + this.canvas.height - player_middle;

		
		this.player_right.clear(this.ctx);
		if (touch_y < y_min)
			this.player_right.draw(this.ctx, 0);
		else if (touch_y > y_max)
			this.player_right.draw(this.ctx, this.height_unscaled - this.player_right.height);
		else 
			this.player_right.draw(this.ctx, (touch_y - y_min) / this.scale);
	}


	getElementHTML() {
		const template = document.createElement('template');
		template.classList.add("w-100", "h-100");
		template.innerHTML = `
			<div id="pongCanvasContainer" class="canvas-container d-flex justify-content-center align-items-center w-100 h-100">
				<canvas id="pongBackgroundCanvas" class="position-absolute bg-dark shadow" width="1000" height="600"></canvas>
				<canvas id="pongGameCanvas" class="position-absolute" width="1000" height="600"></canvas>
			</div>
		`;
		return template;
	}
}

customElements.define('pong-canvas-element', PongCanvasElement);