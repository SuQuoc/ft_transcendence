// create the game area
// add player in constructor
class GameArea {

    constructor()
    {
        this.canvas = document.createElement("canvas");
    }
    
    // use the start function
    // specify game area/canvas size
    // set the refresh rate. How often the game gets rebuild.
    start(player1, player2, ball, width=800, height=600, refresh_rate=50)
    {
        this.player1 = player1;
        this.player2 = player2;
        this.ball = ball;
        this.canvas.width = width;
        this.canvas.height = height;
        this.context = this.canvas.getContext("2d");
        document.body.insertBefore(this.canvas, document.body.childNodes[0]);
        this.frameNo = 0;
        this.interval = setInterval(updateGameArea, refresh_rate, this);
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
}