
class Player
{
    constructor(id, y, x, width, height, name)
    {
        this.id = id;
        this.y = y;
        this.x = x;
        this.width = width;
        this.height = height;
        this.name = name;
    }

    update(game_area, color="red")
    {
        let ctx = game_area.context;
        ctx.fillStyle = color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}