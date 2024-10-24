import { Ball } from './ballClass.js';
import { Player } from './playerClass.js';
import { Background } from './backgroundClass.js';

export class PongCanvasElement extends HTMLElement {
	constructor() {
		super();

		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);
		this.handleCanvasResize_var = this.handleCanvasResize.bind(this);
		this.handleBackgroundCanvasResize_var = this.handleBackgroundCanvasResize.bind(this);

		this.handlePlayerMoveKeyDown_var = this.handlePlayerMoveKeyDown.bind(this);
		//this.handlePlayerMoveTouch_var = this.handlePlayerMoveTouch.bind(this);
		//this.handlePlayerMoveTouchStart_var = this.handlePlayerMoveTouchStart.bind(this);
		this.handlePlayerMoveEnd_var = this.handlePlayerMoveEnd.bind(this);
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
		window.app.pong_socket.addEventListener("message", this.handleReceivedMessage_var);
		// maybe should be this or this.canvas not window !!??
		window.addEventListener('resize', this.handleCanvasResize_var);
		window.addEventListener('resize', this.handleBackgroundCanvasResize_var);

		window.addEventListener('keydown', this.handlePlayerMoveKeyDown_var);
		window.addEventListener('keyup', this.handlePlayerMoveEnd_var);
		//this.addEventListener('touchmove', this.handlePlayerMoveTouch_var);
		//this.addEventListener('touchstart', this.handlePlayerMoveTouchStart_var);
		//this.addEventListener('touchend', this.handlePlayerMoveEnd_var);
	}

	disconnectedCallback() {
		// remove event listeners
		window.app.pong_socket.addEventListener("message", this.handleReceivedMessage_var);
		window.removeEventListener('resize', this.handleCanvasResize_var);
		window.removeEventListener('resize', this.handleBackgroundCanvasResize_var);

		window.removeEventListener('keydown', this.handlePlayerMoveKeyDown_var);
		window.removeEventListener('keyup', this.handlePlayerMoveEnd_var);
		//this.removeEventListener('touchmove', this.handlePlayerMoveTouch_var);
		//this.removeEventListener('touchstart', this.handlePlayerMoveTouchStart_var);
		//this.removeEventListener('touchend', this.handlePlayerMoveEnd_var);

		clearInterval(this.interval_id);
	}


	/// ----- Methods ----- ///
	/** Initializes the canvases and other objects */
	init() {
		let player_x = 10;
		let player_y = 0;
		let player_width = 10;
		let player_height = 60;
		let player_speed = 10; // server is 10
		let player_color = 'white';
		let ball_size = 10;
		let ball_speed = 8; // server is 8

		this.container =		this.querySelector('#pongCanvasContainer');
		this.bg_canvas = 		this.querySelector('#pongBackgroundCanvas');
		this.canvas =			this.querySelector('#pongGameCanvas');
		this.bg_ctx = 			this.bg_canvas.getContext('2d');
		this.ctx =				this.canvas.getContext('2d');
		this.scale =			1;
		this.ratio =			0.6;
		this.width_unscaled =	1000;
		this.height_unscaled =	this.width_unscaled * this.ratio;

		this.interval_id =	null;
		this.move_to_y = 		0; // used to move the player

		this.player_left =	new Player(player_x,
										player_y,
										player_width,
										player_height,
										player_speed,
										player_color,
										this.ctx);
		this.player_right =	new Player(this.width_unscaled - player_x - player_width,
										player_y,
										player_width,
										player_height,
										player_speed,
										player_color,
										this.ctx);
		this.ball =			new Ball((this.width_unscaled / 2) - (ball_size / 2),
									(this.height_unscaled / 2) - (ball_size / 2),
									ball_size,
									ball_speed,
									'white',
									this.ctx);
		this.background = 	new Background(this.width_unscaled,
											this.height_unscaled,
											50,
											'grey',
											'50px Arial',
											this.bg_ctx);

		// states
		this.curr_state = {} // current state
		this.next_state = {}
		this.sent_state = {}
	}

	/** Scales the canvas depending on the screensize and sets this.scale to the new scale. */
	scaleCanvas(ctx, canvas_width, canvas_width_unscaled) {
		this.scale = canvas_width / canvas_width_unscaled;
	
		ctx.scale(this.scale, this.scale);
	}

	renderForeground(state) {
		this.ball.redraw(state.ball_pos_x, state.ball_pos_y);
		this.player_left.redraw(state.player_l_y);
		this.player_right.redraw(state.player_r_y);
	}

	async updateGame(state) {
		this.sent_state = state;

		// rendering
		this.renderForeground(this.curr_state);
		if (this.player_left.old_score !== state.score_l || this.player_right.old_score !== state.score_r) {
			this.player_left.old_score = state.score_l;
			this.player_right.old_score = state.score_r;
			this.background.drawBackground(this.curr_state.score_l, this.curr_state.score_r);
		}

		// making a frame between the states sent by the server
		setTimeout(() => {
			let state = {
				ball_pos_x : this.curr_state.ball_pos_x + (this.next_state.ball_pos_x - this.curr_state.ball_pos_x) / 2,
				ball_pos_y : this.curr_state.ball_pos_y + (this.next_state.ball_pos_y - this.curr_state.ball_pos_y) / 2,
				player_l_y : this.curr_state.player_l_y + (this.next_state.player_l_y - this.curr_state.player_l_y) / 2,
				player_r_y : this.curr_state.player_r_y + (this.next_state.player_r_y - this.curr_state.player_r_y) / 2
			}
			this.renderForeground(state);
			this.curr_state = this.next_state;
			this.next_state = this.sent_state;
		}, 15);
	}






	/** Moves the right player up or down depending on this.move_to_y. */
/* 	movePlayer() {
		//this.move_to_y -= this.canvas.offsetTop;
		console.log('move_to_y: ', this.move_to_y);
		let player_middle = this.player_right.height * this.scale / 2;
		let current_y = (this.player_right.y * this.scale) + player_middle;

		if (current_y >= this.move_to_y -5 && current_y <= this.move_to_y + 5)
			return;
		if (current_y <= this.move_to_y)
			this.player_right.moveDown(this.ctx, this.height_unscaled);
		else if (current_y >= this.move_to_y)
			this.player_right.moveUp(this.ctx);
	} */


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
		this.background.drawBackground(this.player_left.score, this.player_right.score)
	}
	
	/** Starts an interval that calls movePlayer and sets this.interval_id depending on the key pressed. */
	/* handlePlayerMoveKeyDown(event) {
		if (this.interval_id) {
			//clearInterval(this.interval_id); // if you clear the player stops in the middle of the canvas !!
			return;
		}

		if (event.key === 'ArrowUp') {
			this.move_to_y = 0;
		} else if (event.key === 'ArrowDown') {
			this.move_to_y = this.canvas.offsetTop + this.canvas.height;
		}

		this.interval_id = setInterval(() => { // the => is needed to keep the context of this
			this.movePlayer();
		}, 20);
	} */

	/** Sets a new goal for the player to move to (this.move_to_y) */
	/* handlePlayerMoveTouch(event) {
		console.log('touchmove');
		this.move_to_y = event.touches[0].clientY - this.canvas.offsetTop;
	} */

	/** Starts an interval that calls movePlayer */
	/* handlePlayerMoveTouchStart(event) {
		console.log('touchstart');

		if (this.interval_id) {
			clearInterval(this.interval_id);
			this.interval_id = null;
		}

		this.move_to_y = event.touches[0].clientY - this.canvas.offsetTop;
		this.interval_id = setInterval(() => { // the => is needed to keep the context of this
			this.movePlayer();
		}, 20);
	} */

	/** Ends movement of Player.
	 * 
	 * Clears the interval (clearIneterval) and assigns null to this.interval */
	/* handlePlayerMoveEnd(event) {
		clearInterval(this.interval_id);
		this.interval_id = null;
	} */

	handlePlayerMoveKeyDown(event) {
		if (this.move_to_y !== "stop")
			return;

		if (event.key === 'ArrowUp') {
			window.app.pong_socket.send(JSON.stringify({"type": "up"}));
			this.move_to_y = "up";
		} else if (event.key === 'ArrowDown') {
			window.app.pong_socket.send(JSON.stringify({"type": "down"}));
			this.move_to_y = "down";
		}
	}

	handlePlayerMoveEnd(event) {
		if (event.key !== 'ArrowUp' && event.key !== 'ArrowDown' || this.move_to_y === "stop")
			return;
		window.app.pong_socket.send(JSON.stringify({"type": "stop"}));
		this.move_to_y = "stop";
	}

	async handleReceivedMessage(event) {
		const data = JSON.parse(event.data);
		//console.log("Received message: ", data);
		/* if (data.type === "your_side") {
			console.log("Your side: ", data.side);
			if (data.side === "left") {
				this.me = this.player_left;
				this.rival = this.player_right;
			} else {
				this.me = this.player_left;
				this.rival = this.player_right;
			}
			//this.game_loop();
		} */
		if (data.type === "state_update") {
			await this.updateGame(data.game_state);
		}
		else if (data.type === "initial_state") {
			this.curr_state = data.game_state;
			this.next_state = data.game_state;
		}
		else if (data.type === "game_end") {
			console.log("game_end");
			clearInterval(this.interval_id);
		}
		else {
			console.error("Unknown message type: ", data.type);
		}
			
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