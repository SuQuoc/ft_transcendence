class Background {
	/** To make a pong background.
	 * @param {number} canvas_width - The width of the **unscaled** canvas.
	 * @param {number} canvas_height - The height of the **unscaled** canvas.
	 * @param {number} y_score - Where the score is on the y axis.
	 * @param {string} color - The color of the score and dashed line.
	 * @param {CanvasRenderingContext2D} ctx - The canvas context to draw on.
	 */
	constructor(canvas_width, canvas_height, y_score, color, ctx) {
		this.canvas_width = canvas_width;
		this.canvas_height = canvas_height;
		this.canvas_middle = canvas_width / 2;
		
		this.score = {};
		this.score.x_left = canvas_width / 4; // the x coordinate of the left score
		this.score.x_right = this.score.x_left * 3; // the x coordinate of the right score
		this.score.y = y_score;

		this.color = color;
		this.ctx = ctx;

		this.left_player_name = "";
		this.right_player_name = "";
	}

	/** Setting the names of the players.
	 * 
	 * If you set them to "", then there will be no names. (It's also the initial value)
	 */
	setNames(left_player, right_player) {
		this.left_player_name = left_player;
		this.right_player_name = right_player;
	}

	/** Clears the old name and draws the new one. */
	drawLeftName() {
		// clearing the old name
		this.ctx.clearRect(this.score.x_left - 200, this.canvas_height - 150, 400, 150);

		this.ctx.fillStyle = this.color;
		this.ctx.font = '25px Arial';
		this.ctx.textAlign = "center"; // Center the text horizontally
		this.ctx.fillText(this.left_player_name, this.score.x_left, this.canvas_height - 15);
	}

	/** Clears the old name and draws the new one. */
	drawRightName() {
		// clearing the old name
		this.ctx.clearRect(this.score.x_right - 200, this.canvas_height - 150, 400, 150);

		this.ctx.fillStyle = this.color;
		this.ctx.font = '25px Arial';
		this.ctx.textAlign = "center"; // Center the text horizontally
		this.ctx.fillText(this.right_player_name, this.score.x_right, this.canvas_height - 15);
	}

	/** Clears the names of the players */
	clearNames() {
		this.ctx.clearRect(this.score.x_left - 200, this.canvas_height - 150, 400, 150);
		this.ctx.clearRect(this.score.x_right - 200, this.canvas_height - 150, 400, 150);
	}

	/** Clears the old score and draws the new one.
	 * @param {string} score - The new score.
	 */
	drawLeftScore(score) {
		// clearing the old score
		this.ctx.clearRect(this.score.x_left - 50, this.score.y - 50, 100, 50);

		this.ctx.fillStyle = this.color;
		this.ctx.font = '50px Arial';
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
		this.ctx.font = '50px Arial';
		this.ctx.textAlign = "center"; // Center the text horizontally
		this.ctx.fillText(score, this.score.x_right, this.score.y);
	}

	/** Clears and draws a dashed line in the middle */
	drawMiddleLine() {
		this.ctx.clearRect(this.canvas_middle - 5, 0, 10, this.canvas_height);

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
		this.drawLeftName("");
		this.drawRightName("");
	}
}

export { Background };