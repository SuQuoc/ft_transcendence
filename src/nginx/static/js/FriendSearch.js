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
        .friend-status {
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          position: absolute;
          bottom: 0;
          right: 0;
        }
        .list-group-item {
          display: flex;
          align-items: center;
        }
        .online {
          background-color: green;
        }
        .offline {
          background-color: lightgray;
          border: 1px solid gray;
        }
        .friend-img-container {
          width: 40px;
          height: 40px;
          margin-right: 10px;
          position: relative;
        }
        .friend-img {
          width: 40px;
          height: 40px;
          border-radius: 50%;
        }
        .list-group-item > .btn {
          margin-right: 0.25rem;
          width: 30px;
          height: 30px;
          aspect-ratio: 1 / 1;
        }
        .list-group-item {
          min-height: 58px;
        }
        .search-container {
        width: 100%;
        max-width: 400px;
        margin: 0 auto;
      }
      </style>
      <div class="search-container p-3 rounded-3 bg-dark">
        <div class="input-group mb-3" role="search">
            <input type="text" class="form-control search-input" placeholder="Search for users..." aria-label="Search">
            <button class="btn btn-primary search-button">🔍</button>
        </div>
        <ul class="search-results list-group bg-dark"></ul>
      </div>
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
            const item = document.createElement('li');
            item.innerHTML = `
            ${user.relationship === 'friend' ? '<button class="btn btn-danger btn-sm">X</button>' : ''}
            ${user.relationship === 'requested' ? '<button class="btn btn-primary btn-sm disabled">+</button>' : ''}
            ${user.relationship === 'received' ? '<button class="btn btn-success btn-sm">✓</button><button class="btn btn-danger btn-sm">X</button>' : ''}
            ${user.relationship === 'stranger' && user.displayname !== window.app.userData.username ? '<button class="btn btn-primary btn-sm">+</button>' : ''}
            <span class="text-white">${user.displayname}</span>
          `;
            item.classList.add('list-group-item', 'd-flex', 'justify-content-start', 'w-100', 'bg-dark');

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
        const response = await this.apiFetch(`/um/friends/answer`, { method: "POST", body: JSON.stringify({ friend_request_id: fid, action: newStatus }) });
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
        const response = await this.apiFetch(`/um/friends/send`, { method: "POST", body: JSON.stringify({ receiver: displayname}) });
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