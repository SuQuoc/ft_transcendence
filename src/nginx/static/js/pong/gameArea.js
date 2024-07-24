// create the game area
// add player in constructor
class GameArea {

    constructor(width=800, height=600, refresh_rate=30)
    {
        this.canvas = document.createElement("canvas");
        this.refresh_rate = refresh_rate
        this.canvas.height = height;
        this.canvas.width = width;
    }

    // use the start function
    // specify game area/canvas size
    // set the refresh rate. How often the game gets rebuild.
    start(player1, player2, ball)
    {
        this.ball = ball;
        this.player1 = player1;
        this.player2 = player2;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.frameNo = 0;
        this.interval = setInterval(updateGameArea, this.refresh_rate, this);
    }

    // need to clear the canvas after every frame
    // just clear what is changed faster?
    clear()
    {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    // do i need this?
    stop()
    {
        clearInterval(this.interval);
    }

    draw_middle_line(color, line_width, line_height, space)
    {
        var y = 0;
        var x = this.canvas.width / 2 - line_width / 2;

        while(y < this.canvas.height)
        {
            let ctx = this.context;
            ctx.fillStyle = color;
            ctx.fillRect(x, y, line_width, line_height);
            y += line_height * space;
        }
    }
}
