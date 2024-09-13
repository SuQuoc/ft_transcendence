export class Player {
    constructor(id, y, x, width, height, name) {
        this.id = id
        this.y = y
        this.x = x
        this.width = width
        this.height = height
        this.name = name
    }

    update(game_area, color = 'red') {
        let ctx = game_area.context
        ctx.fillStyle = color
        ctx.fillRect(this.x, this.y, this.width, this.height)
    }

    update_game_count(left, right) {
        if (left < 10) this.match_count_left = '0'.concat(left.toString())
        else this.match_count_left = left

        if (right < 10) this.match_count_right = '0'.concat(right.toString())
        else this.match_count_right = right
    }
}
