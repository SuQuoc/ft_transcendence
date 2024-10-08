class Player {
	/** Creates a new Player with the given width and height on the specified x. All of the numbers should be positive or there will be problems.
	 * @param {number} x - The x-coordinate of the left upper corner.
	 * @param {number} width - The width of the rectangle.
	 * @param {number} height - The height of the rectangle.
	 * @param {number} speed - The speed of the player.
	 * @param {string} fill_style - The color of the Player.
	*/
	constructor(x, y, width, height, speed, fill_style) {
		this.x = x;
		this.y = y;
		this.width = width;
		this.height = height;
		this.speed = speed;
		this.fill_style = fill_style;
	}

	/** Draws the rectangle on the passed canvas context. Y is the height of the left upper corner of the rectangle.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	 * @param {number} y - (optional: The y-coordinate of the left upper corner. Overwrites the current position)
	*/
	draw(ctx, y = this.y) {
		this.y = y;

		ctx.fillStyle = this.fill_style;
		ctx.fillRect(this.x, y, this.width, this.height);
	}

	/** Clears the rectangle on the passed canvas context. The position is the last that was drawn.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	clear(ctx) {
		ctx.clearRect(this.x - 2, this.y - 2, this.width + 5, this.height + 5); // the -1 and +2 are because there was a border left (the smaller the canvas the higher these numbers have to be)
	}

	/** Moves the player up by the speed variable set in the constructor.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	*/
	moveUp(ctx) { // can be optimized by only clearing the part that is needed !!! (tried it and it didn't seem to be better. maybe it can be though)
		if (this.y - this.speed < 0) { // maybe protect against negative values!!??
			this.y = 0;
			this.clear(ctx);
			this.draw(ctx, this.y, this.fill_style);
			return;
		}
		
		/* this.y -= this.speed;
		ctx.clearRect(this.x - 1, this.y + this.height - 1, this.width + 2, this.speed + 2);
		ctx.fillRect(this.x, this.y, this.width, this.speed); */
		this.clear(ctx);
		this.draw(ctx, this.y - this.speed, this.fill_style);
	}

	/** Moves the player down by the speed variable set in the constructor.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	 * @param {number} canvas_height - The height of the **unscaled** canvas.
	*/
	moveDown(ctx, canvas_height) { // can be optimized by only clearing the part that is needed !!!
		canvas_height -= this.height; // because the player is drawn from the top left corner

		if (this.y + this.speed > canvas_height) { // maybe protect against negative values!!??
			this.y = canvas_height;
			this.clear(ctx);
			this.draw(ctx, this.y, this.fill_style);
			return;
		}
		
		this.clear(ctx);
		this.draw(ctx, this.y + this.speed, this.fill_style);
	}
}

export { Player };