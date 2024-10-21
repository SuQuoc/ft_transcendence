class Ball {
	/** Creates a new ball with the given width and height.
	 * @param {number} x - The x coordinate of the left upper corner of the ball.
	 * @param {number} y - The y coordinate of the left upper corner of the ball.
	 * @param {number} size - The width and height of the ball (it's a sqare).
	 * @param {string} fill_style - The color of the ball.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	constructor(x, y, size, fill_style, ctx) {
		this.pos = { x: x, y: y };
		this.vel = { x: 5, y: 5 }; // should not be defined here!!!
		this.size = size;
		this.fill_style = fill_style;
		this.ctx = ctx;
	}

	/** Draws the ball. X and y are the coordinates of the left upper corner.
	 * @param {number} x - (optional: The x-coordinate of the left upper corner. Overwrites the current position)
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	draw(x = this.pos.x, y = this.pos.y) {
		this.pos.x = x;
		this.pos.y = y;

		this.ctx.fillStyle = this.fill_style;
		this.ctx.fillRect(x, y, this.size, this.size);
	}

	/** Clears the ball. The position is the last that was drawn.*/
	clear() {
		this.ctx.clearRect(this.pos.x - 1, this.pos.y - 1, this.size + 2, this.size + 2);
		// The -1 and +2 are needed, because the canvas makes lines smother by putting less saturated pixels next to them if they aren't an int.
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
}

export { Ball };