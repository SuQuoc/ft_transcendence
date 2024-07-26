class FriendList extends HTMLElement {
    constructor() {
        super();

		//separates shadow DOM from rest of the DOM, but still being accessible from outside
		this.root = this.attachShadow({ mode: 'open' });
		console.log(this.root);
		const styles = document.createElement("style");
		this.root.appendChild(styles);

		async function loadCSS() {
			try {
				const request = await fetch("../css/userinfo.css");
				if (!request.ok) {
					throw new Error(`HTTP error! status: ${request.status}`);
				}
				styles.textContent = await request.text();
				console.log("CSS successfully loaded")
			} catch (error) {
				console.error('Error loading CSS:', error);
			}
		}
		loadCSS();
		
        this.friends = [];
        this.requested = [];
        this.defriended = [];
		
    }

    async fetchFriendList() {
        try {
			//substitute with endpoint instead of dummy JSON
            const response = await fetch('../prototypes/getfriendlist.json');
            const data = await response.json();
			console.log(data);
            this.friends = data[0].friends;
            this.requested = data[0].requested;
            this.defriended = data[0].defriended;
            this.render();
        } catch (error) {
            console.error('Error fetching friend list:', error);
        }
    }

    render() {
		
        this.root.innerHTML = `
            <div class="friend-list">
                <div class="friend-section">
                    <h3>Current Friends</h3>
                    ${this.friends.map(friend => `
                        <div class="friend-item">
                            <img class="avatar" src="${friend.img}" alt="Avatar">
                            <div class="details">
                                <div class="displayname">${friend.displayname}</div>
                                <div class="status">${friend.onlinestatus ? 'Online' : 'Offline'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="friend-section">
                    <h3>Requested Friends</h3>
                    ${this.requested.map(request => `
                        <div class="friend-item">
                            <div class="details">
                                <div class="displayname">${request.displayname}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="friend-section">
                    <h3>Former Friends</h3>
                    ${this.defriended.map(defriend => `
                        <div class="friend-item">
                            <div class="details">
                                <div class="displayname">${defriend.displayname}</div>
                            </div>
                            <button class="add-friend" data-displayname="${defriend.displayname}">Add Friend</button>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

		/*
        this.root.querySelectorAll('.add-friend').forEach(button => {
            button.addEventListener('click', (event) => {
                const displayname = event.target.getAttribute('data-displayname');
                this.dispatchEvent(new CustomEvent('add-friend', {
                    detail: { displayname },
                    bubbles: true,
                    composed: true
                }));
            });
        });
	
		// Clear existing content
        this.root.innerHTML = '';

        // Add styles again to ensure they are not removed
        const styles = document.createElement("style");
        this.root.appendChild(styles);

        // Render logic here
        const friendListContainer = document.createElement('div');
        friendListContainer.classList.add('friend-list');

        this.friends.forEach(friend => {
            const friendItem = document.createElement('div');
            friendItem.classList.add('friend-item');
            friendItem.textContent = friend.name; // Example content
            friendListContainer.appendChild(friendItem);
        });

        this.root.appendChild(friendListContainer);
		*/
    }

    connectedCallback() {
        this.fetchFriendList();
    }
}

customElements.define('friend-list', FriendList);