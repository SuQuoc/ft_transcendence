
class Player
{
    constructor(id, y, x, width, height, name)
    {
        this.id;
        this.y = y;
        this.x = x;
        this.width = width;
        this.height = height;
        this.name = name;
    }

    update(game_area)
    {
        let ctx = game_area.context;
        ctx.fillStyle = "red";
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}