class Ball {
	/** Creates a new ball with the given width and height.
	 * @param {number} x - The x coordinate of the left upper corner of the ball.
	 * @param {number} y - The y coordinate of the left upper corner of the ball.
	 * @param {number} width - The width of the ball.
	 * @param {number} height - The height of the ball.
	*/
	constructor(x, y, width, height) {
		this.x = x;
		this.y = y;
		this.width = width;
		this.height = height;
	}

	/** Draws the ball on the passed canvas context. X and y are the coordinates of the left upper corner.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	 * @param {string} fill_style - The color of the ball.
	 * @param {number} x - (optional: The x-coordinate of the left upper corner. Overwrites the current position)
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	draw(ctx, fill_style, x = this.x, y = this.y) {
		this.x = x;
		this.y = y;

		ctx.fillStyle = fill_style;
		ctx.fillRect(x, y, this.width, this.height);
	}

	/** Clears the ball on the passed canvas context. The position is the last that was drawn.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	clear(ctx) {
		ctx.clearRect(this.x - 1, this.y - 1, this.width + 2, this.height + 2);
		// The -1 and +2 are needed, because the canvas makes lines smother by putting less saturated pixels next to them if they aren't an int.
		// Even if the numbers are ints here they will still have this line, because we scale the canvas.
	}
}

export { Ball };