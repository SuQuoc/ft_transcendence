export class EventQueue {
	constructor() {
		this.event_queue = [];
		this.add = this.add.bind(this);
        this.get = this.get.bind(this);
	};


	/// ----- Methods ----- ///

	add(event) {
		this.event_queue.push(event);
	}

	get() {
        if (this.event_queue.length === 0)
			return (null)
		const event = this.event_queue.shift();
        return (event);
    }
}