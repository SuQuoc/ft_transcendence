import { ComponentBaseClass } from "./componentBaseClass.js";

export class FriendSearch extends ComponentBaseClass {
    constructor() {
        super();
        this.results = [];
    }

    getElementHTML() {
        const template = document.createElement('template');
        template.innerHTML = `
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
      <style>
        .search-container {
          display: flex;
          align-items: center;
          margin-bottom: 1rem;
        }
        .search-input {
          flex-grow: 1;
          margin-right: 0.5rem;
        }
        .search-results {
          list-style: none;
          padding: 0;
        }
        .search-results li {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0.5rem;
          border-bottom: 1px solid #ccc;
          color:white;
        }
      </style>
      <div class="search-container">
        <input type="text" class="form-control search-input" placeholder="Search for friends...">
        <button class="btn btn-primary search-button">🔍</button>
      </div>
      <ul class="search-results"></ul>
    `;
        return template;
    }

    connectedCallback() {
        super.connectedCallback();
        this.shadowRoot.querySelector('.search-button').addEventListener('click', () => this.performSearch());
        this.shadowRoot.querySelector('.search-input').addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                this.performSearch();
            }
        });
    }

    async performSearch() {
        const query = this.shadowRoot.querySelector('.search-input').value;
        if (!query) return;

        try {
            this.results = [];
            this.results = await this.apiFetch(`/um/search?term=${query}`, { method: "GET", cache: "no-store" });
            this.updateResults();
        } catch (e) {
            console.error('Error fetching search results:', e.message);
        }
    }

    updateResults() {
        const resultsElement = this.shadowRoot.querySelector('.search-results');
        resultsElement.innerHTML = '';

        this.results.forEach(user => {
            console.log("User: ", user);
            const item = document.createElement('li');
            item.innerHTML = `
            <span>${user.displayname}</span>
            <div>
              ${user.relationship === 'friend' ? '<button class="btn btn-danger btn-sm">X</button>' : ''}
              ${user.relationship === 'requested' ? '<span>Request Sent</span>' : ''}
              ${user.relationship === 'received' ? '<button class="btn btn-success btn-sm">✓</button><button class="btn btn-danger btn-sm">X</button>' : ''}
              ${user.relationship === 'stranger' && user.displayname !== window.app.userData.username ? '<button class="btn btn-primary btn-sm">+</button>' : ''}
            </div>
          `;

        if (user.relationship === 'friend') {
            item.querySelector('.btn-danger').addEventListener('click', () => this.changeFriendRequest(user.friend_request_id, 'unfriend'));
        } else if (user.relationship === 'received') {
            item.querySelector('.btn-success').addEventListener('click', () => this.changeFriendRequest(user.friend_request_id, 'accept'));
            item.querySelector('.btn-danger').addEventListener('click', () => this.changeFriendRequest(user.friend_request_id, 'decline'));
        } else if (user.relationship === 'stranger' && user.displayname !== window.app.userData.username) {
            item.querySelector('.btn-primary').addEventListener('click', () => this.sendFriendRequest(user.displayname));
        }
        resultsElement.appendChild(item);
        });
    }

    async changeFriendRequest(fid, newStatus) {
        const response = await this.apiFetch(`/um/friends/answer/`, { method: "POST", body: JSON.stringify({ friend_request_id: fid, action: newStatus }) });
        if (response.error) {
            console.error('Error changing friend request:', response.error);
            return;
        }
        for (const user of this.results) {
            if (user.friend_request_id === fid) {
                if (newStatus === 'decline' || newStatus === 'unfriend') {
                    user.relationship = 'stranger';
                } else if (newStatus === 'accept') {
                    user.relationship = 'friend';
                }
            }
        }
        this.updateResults();
    }

    async sendFriendRequest(displayname) {
        const response = await this.apiFetch(`/um/friends/send/`, { method: "POST", body: JSON.stringify({ receiver: displayname}) });
        if (response.error) {
            console.error('Error sending friend request:', response.error);
            return;
        }
        for (const user of this.results) {
            if (user.displayname === displayname) {
                user.relationship = 'requested';
            }
        }
        this.updateResults();
    }
}

customElements.define('friend-search', FriendSearch);