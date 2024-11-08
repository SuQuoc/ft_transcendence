import { Player } from './playerClass.js';

class Ball {
	/** Creates a new ball with the given width and height.
	 * @param {number} x - The x coordinate of the left upper corner of the ball.
	 * @param {number} y - The y coordinate of the left upper corner of the ball.
	 * @param {number} size - The width and height of the ball (it's a sqare).
	 * @param {number} speed - The speed of the ball.
	 * @param {string} fill_style - The color of the ball.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	constructor(x, y, size, speed, fill_style, ctx) {
		this.pos = { x: x, y: y };
		//this.vel = { x: speed, y: speed };
		this.size = size;
		this.fill_style = fill_style;
		this.ctx = ctx;
	}

	/** Draws the ball and sets the new pos. X and y are the coordinates of the left upper corner.
	 * @param {number} x - (optional: The x-coordinate of the left upper corner. Overwrites the current position)
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	draw(x = this.pos.x, y = this.pos.y) {
		this.pos.x = x;
		this.pos.y = y;
		
		this.ctx.fillStyle = this.fill_style;
		this.ctx.fillRect(x, y, this.size, this.size);
	}

	/** Clears the last position that was drawn.*/
	clear() {
		this.ctx.clearRect(this.pos.x - 2, this.pos.y - 2, this.size + 5, this.size + 5);
		// The -2 and +5 are needed, because the canvas makes lines smoother by putting less saturated pixels next to them if they aren't an int.
		// Even if the numbers are ints here they will still have this line, because we scale the canvas.
	}

	/** Clears and then draws the ball. X and y are the coordinates of the left upper corner.
	 * @param {number} x - (optional: The x-coordinate of the left upper corner. Overwrites the current position)
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	redraw(x = this.pos.x, y = this.pos.y) {
		this.clear();
		this.draw(x, y);
	}


	/** Moves the ball by the velocity. */
/* 	move() {
		this.pos.x += this.vel.x
		this.pos.y += this.vel.y
	} */


	/** Reflect ball if it hits the top or bottom of canvas
	 * @param {number} canvas_height - The height of the **unscaled** canvas.
	*/
/* 	check_wall_collision(canvas_height) {
		if (this.pos.y <= 0) {
			this.pos.y = 0
			this.vel.y *= -1
		}
		if (this.pos.y + this.size >= canvas_height) {
			this.pos.y = canvas_height - this.size
			this.vel.y *= -1
		}
	} */
		

	/** reflect ball if it hits a player
	 * @param {Player} player_l - The left player.
	 * @param {Player} player_r - The right player.
	 */
/* 	check_player_collision(player_l, player_r) {

		if (this.pos.x <= player_l.x + player_l.width) {
			if (this.pos.y + this.size > player_l.y && this.pos.y < player_l.y + player_l.height) {
				this.pos.x = player_l.x + player_l.width
				this.vel.x *= -1
			}
		}
		else if (this.pos.x + this.size >= player_r.x) {
			if (this.pos.y + this.size > player_r.y && this.pos.y < player_r.y + player_r.height) {
				this.pos.x = player_r.x - this.size
				this.vel.x *= -1
			}
		}
	} */

}

export { Ball };