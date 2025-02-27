class Player {
	/** Creates a new Player with the given width and height on the specified x. All of the numbers should be positive or there will be problems.
	 * @param {number} x - The x-coordinate of the left upper corner.
	 * @param {number} y - The y-coordinate of the left upper corner.
	 * @param {number} width - The width of the rectangle.
	 * @param {number} height - The height of the rectangle.
	 * @param {number} speed - The speed of the player.
	 * @param {string} fill_style - The color of the Player.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	constructor(x, y, width, height, speed, fill_style, ctx) {
		this.x = x;
		this.y = y;
		this.width = width;
		this.height = height;
		this.speed = speed;
		this.fill_style = fill_style;
		this.ctx = ctx;
		
		this.score = 0;
	}

	/** Draws the rectangle and sets the new y. Y is the height of the left upper corner of the rectangle.
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	draw(y = this.y) {
		this.y = y;

		this.ctx.fillStyle = this.fill_style;
		this.ctx.fillRect(this.x, y, this.width, this.height);
	}

	/** Clears the rectangle on the last positon it was drawn.*/
	clear() {
		this.ctx.clearRect(this.x - 5, this.y - 5, this.width + 10, this.height + 10); // the -5 and +10 are because there was a border left (the smaller the canvas the higher these numbers have to be)
	}

	/** Clears and then draws the rectangle. Y is the height of the left upper corner of the rectangle.
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	redraw(y = this.y) {
		this.clear();
		this.draw(y);
	}

	/** Moves the player up by the speed variable set in the constructor.*/
	moveUp() {
		if (this.y - this.speed < 0) {
			this.y = 0;
			this.clear();
			this.draw(this.y, this.fill_style);
			return;
		}
		this.clear();
		this.draw(this.y - this.speed, this.fill_style);
	}

	/** Moves the player down by the speed variable set in the constructor.
	 * @param {number} canvas_height - The height of the **unscaled** canvas.
	*/
	moveDown(canvas_height) {
		canvas_height -= this.height; // because the player is drawn from the top left corner

		if (this.y + this.speed > canvas_height) {
			this.y = canvas_height;
			this.clear();
			this.draw(this.y, this.fill_style);
			return;
		}
		this.clear();
		this.draw(this.y + this.speed, this.fill_style);
	}
}

export { Player };