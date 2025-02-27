import { Ball } from './ballClass.js';
import { Player } from './playerClass.js';
import { canvasBaseClass } from "./canvasBaseClass.js";

export class PongCanvasElement extends canvasBaseClass {
	constructor() {
		super();

		// Binds the method to this class instance so it can be used in the event listener
		this.handleReceivedMessage_var = this.handleReceivedMessage.bind(this);

		this.handlePlayerMoveKey_var = this.handlePlayerMoveKey.bind(this);
		this.handlePlayerMoveTouch_var = this.handlePlayerMoveTouch.bind(this);
		this.handlePlayerMoveEnd_var = this.handlePlayerMoveEnd.bind(this);

		this.handleDoubleTap_var = this.handleDoubleTap.bind(this);
		this.handleDoubleClick_var = this.handleDoubleClick.bind(this);
	}

	connectedCallback() {
		super.connectedCallback();

		this.init();

		// add event listeners
		window.app.pong_socket.addEventListener("message", this.handleReceivedMessage_var);

		window.addEventListener('keydown', this.handlePlayerMoveKey_var);
		window.addEventListener('keyup', this.handlePlayerMoveEnd_var);
		this.addEventListener('touchmove', this.handlePlayerMoveTouch_var);
		this.addEventListener('touchstart', this.handlePlayerMoveTouch_var);
		this.addEventListener('touchend', this.handlePlayerMoveEnd_var);

		this.canvas.addEventListener("touchend", this.handleDoubleTap_var);
		this.canvas.addEventListener("dblclick", this.handleDoubleClick_var);
	}

	disconnectedCallback() {
		super.disconnectedCallback();

		// remove event listeners
		if (window.app.pong_socket)
		window.app.pong_socket.removeEventListener("message", this.handleReceivedMessage_var);

		window.removeEventListener('keydown', this.handlePlayerMoveKey_var);
		window.removeEventListener('keyup', this.handlePlayerMoveEnd_var);
		this.removeEventListener('touchmove', this.handlePlayerMoveTouch_var);
		this.removeEventListener('touchstart', this.handlePlayerMoveTouch_var);
		this.removeEventListener('touchend', this.handlePlayerMoveEnd_var);

		this.canvas.removeEventListener("touchend", this.handleDoubleTap_var);
		this.canvas.removeEventListener("dblclick", this.handleDoubleClick_var);

		clearTimeout(this.timeout_id);
	}


	/// ----- Methods ----- ///
	/** Initializes the canvases and other objects */
	init() {
		super.init();

		this.last_tap = new Date().getTime(); // used to mesure if the user double taps

		let player_x = 10;
		let player_width = 10;
		let player_height = 60;
		let player_speed = 10; // server is 10
		let player_color = 'white';
		let ball_size = 10;
		let ball_speed = 8; // server is 8

		this.timeout_id =	null;
		this.move_to = 	-1; // saves the y-coordinate the player should move to

		this.player_left =	new Player(player_x,
										(this.height_unscaled - player_height) / 2,
										player_width,
										player_height,
										player_speed,
										player_color,
										this.ctx);
		this.player_right =	new Player(this.width_unscaled - player_x - player_width,
										(this.height_unscaled - player_height) / 2,
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

		// states used in updateGame() 
		this.curr_state = {} // current state (the state that is currently displayed)
		this.next_state = {} // the next state that will be displayed
		this.sent_state = {} // the state that was sent by the server (is needed because setTimeout doesn't have the passed state)
	}

	makeFullScreen() {
		if (document.fullscreenElement) {
			return;
		}
	
		const requestFullscreen = this.requestFullscreen;
	
		if (requestFullscreen) {
			requestFullscreen.call(this).then(() => {
				this.handleCanvasResize();
				this.handleBackgroundCanvasResize();
			}).catch((err) => {
				console.error("Error: could not enter fullscreen: ", err);
			});
		} else {
			console.error("Error: Fullscreen API is not supported in this browser.");
		}
	}

	renderForeground(state) {
		requestAnimationFrame(() => {
			this.ball.redraw(state.ball_pos_x, state.ball_pos_y);
			this.player_left.redraw(state.player_l_y);
			this.player_right.redraw(state.player_r_y);
		});
	}

	async updateGame(state) {
		this.sent_state = state;
		if (this.curr_state === null) {
			this.curr_state = state;
			this.next_state = state;
		}

		// rendering
		this.renderForeground(this.curr_state);
		if (this.player_left.old_score !== state.score_l || this.player_right.old_score !== state.score_r) {
			this.player_left.old_score = state.score_l;
			this.player_right.old_score = state.score_r;
			this.background.drawBackground(state.score_l, state.score_r);
		}

		// making a frame between the states sent by the server
		this.timeout_id = setTimeout(() => {
			let state = {
				ball_pos_x : this.curr_state.ball_pos_x + (this.next_state.ball_pos_x - this.curr_state.ball_pos_x) / 2,
				ball_pos_y : this.curr_state.ball_pos_y + (this.next_state.ball_pos_y - this.curr_state.ball_pos_y) / 2,
				player_l_y : this.curr_state.player_l_y + (this.next_state.player_l_y - this.curr_state.player_l_y) / 2,
				player_r_y : this.curr_state.player_r_y + (this.next_state.player_r_y - this.curr_state.player_r_y) / 2
			}
			this.renderForeground(state);
			this.curr_state = this.next_state;
			this.next_state = this.sent_state;
			this.timeout_id = null;
		}, 15);
	}


	/// ----- Event Handlers ----- ///

	handleDoubleTap() {
		const current_time = new Date().getTime();
        const tap_length = current_time - this.last_tap;
        if (tap_length < 400 && tap_length > 0) {
			this.makeFullScreen();
        }
        this.last_tap = current_time;

	}
	
	handleDoubleClick() {
		this.makeFullScreen();
	}

	/** Sets a new goal for the player to move to (this.move_to) */
	handlePlayerMoveTouch(event) {
		event.preventDefault();
		let new_y = ((event.touches[0].clientY - this.canvas.offsetTop) / this.scale) - (this.player_right.height / 2);

		if (new_y < 0)
			new_y = 0;
		else if (new_y > this.height_unscaled)
			new_y = this.height_unscaled;
		// sending only if the position changed
		if (new_y !== this.move_to) {
			this.move_to = new_y;
			window.app.pong_socket.send(JSON.stringify({"type": "move", "move_to": this.move_to}));
		}
	}

	handlePlayerMoveKey(event) {
		if (this.move_to !== -1)
			return;

		if (event.key === 'ArrowUp')
			this.move_to = 0;
		else if (event.key === 'ArrowDown')
			this.move_to = this.height_unscaled;
		else
			return;
		window.app.pong_socket.send(JSON.stringify({"type": "move", "move_to": this.move_to}));
	}

	handlePlayerMoveEnd(event) {
		if (event.target.id === 'pongGameCanvas' || event.target.id === 'pongCanvasContainer'
				|| event.key === 'ArrowUp' || event.key === 'ArrowDown' && this.move_to !== -1) {
			this.move_to = -1;
			window.app.pong_socket.send(JSON.stringify({"type": "move", "move_to": this.move_to}));
		};
	}

	async handleReceivedMessage(event) {
		const data = JSON.parse(event.data);

		if (data.type === "state_update") {
			await this.updateGame(data.game_state);
		}
		else if (data.type === "count_down") {
			this.clearTextForeground();
			this.writeTextForeground(data.count);
		}
		else if (data.type === "initial_state") {
			this.background.setNames(data.left_player, data.right_player);
			this.clearTextForeground();
			this.curr_state = data.game_state;
			this.next_state = data.game_state;
			await this.renderForeground(data.game_state);
		}
		else if (data.type === "game_end") {
			clearTimeout(this.timeout_id);
			this.clearTextForeground();
			this.writeTextForeground("You " + data.status + "!");
			this.dispatchEvent(new CustomEvent("gameend", {bubbles: true})); // dispatching a custom event when the game is over so the page it's on can do something
		}
		else {
			console.error("Unknown message type: ", data.type, ": ", data);
		}
	}

	// getElementHTML() is in the canvasBaseClass
}

customElements.define('pong-canvas-element', PongCanvasElement);