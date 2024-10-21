class Background {
	/** To make a pong background.
	 * @param {number} canvas_width - The width of the **unscaled** canvas.
	 * @param {number} canvas_height - The height of the **unscaled** canvas.
	 * @param {number} y_score - Where the score is on the y axis.
	 * @param {string} color - The color of the score and dashed line.
	 * @param {string} font - The size of the font and font of the score.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	 */
	constructor(canvas_width, canvas_height, y_score, color, font, ctx) {
		this.canvas_height = canvas_height;
		this.canvas_middle = canvas_width / 2;
		
		this.score = {};
		this.score.x_left = canvas_width / 4; // the x coordinate of the left score
		this.score.x_right = this.score.x_left * 3; // the x coordinate of the right score
		this.score.y = y_score;

		this.color = color;
		this.font = font;
		this.ctx = ctx;
	}

	/** Clears the old score and draws the new one.
	 * @param {string} score - The new score.
	 */
	drawLeftScore(score) {
		// clearing the old score
		this.ctx.clearRect(this.score.x_left - 50, this.score.y - 50, 100, 50);

		this.ctx.fillStyle = this.color;
		this.ctx.font = this.font;
		this.ctx.textAlign = "center"; // Center the text horizontally
		this.ctx.fillText(score, this.score.x_left, this.score.y);
	}

	/** Clears the old score and draws the new one.
	 * @param {string} score - The new score.
	 */
	drawRightScore(score) {
		// clearing the old score
		this.ctx.clearRect(this.score.x_right - 50, this.score.y - 50, 100, 50);

		this.ctx.fillStyle = this.color;
		this.ctx.font = this.font;
		this.ctx.textAlign = "center"; // Center the text horizontally
		this.ctx.fillText(score, this.score.x_right, this.score.y);
	}

	/** Draws a dashed line in the middle. */
	drawMiddleLine() {
		this.ctx.strokeStyle = this.color;
		this.ctx.beginPath();
		this.ctx.setLineDash([8, 8]);
		this.ctx.moveTo(this.canvas_middle, 0);
		this.ctx.lineTo(this.canvas_middle, this.canvas_height);
		this.ctx.stroke();
	}

	/** Draws the left score, the right score and the line in the middle.
	 * @param {string} left_score - The new score on the left.
	 * @param {string} right_score - The new score no the right.
	 */
	drawBackground(left_score, right_score) {
		this.drawMiddleLine();
		this.drawLeftScore(left_score);
		this.drawRightScore(right_score);
	}
}

export { Background };