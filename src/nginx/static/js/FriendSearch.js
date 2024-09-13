import { ComponentBaseClass } from './componentBaseClass.js'

export class FriendSearch extends ComponentBaseClass {
    constructor() {
        super()
        this.results = new Map()
    }

    getElementHTML() {
        const template = document.createElement('template')
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
        }
      </style>
      <div class="search-container">
        <input type="text" class="form-control search-input" placeholder="Search for friends...">
        <button class="btn btn-primary search-button">🔍</button>
      </div>
      <ul class="search-results"></ul>
    `
        return template
    }

    connectedCallback() {
        super.connectedCallback()
        this.shadowRoot
            .querySelector('.search-button')
            .addEventListener('click', () => this.performSearch())
        this.shadowRoot
            .querySelector('.search-input')
            .addEventListener('keypress', (event) => {
                if (event.key === 'Enter') {
                    this.performSearch()
                }
            })
    }

    async performSearch() {
        const query = this.shadowRoot.querySelector('.search-input').value
        if (!query) return

        try {
            //TODO: Add API call to search for users, no-store prevents caching https://developer.mozilla.org/en-US/docs/Web/API/Request/cache
            const response = await this.apiFetch(`/um/search?query=${query}`, {
                method: 'GET',
                cache: 'no-store',
            })
            //const response = await fetch(`./js/friends.json`, { cache : "no-store" });
            console.log(response)
            this.results.clear()
            response.forEach((user) => this.results.set(user.user_id, user))
            this.updateResults()
        } catch (e) {
            console.error('Error fetching search results:', e.message)
        }
    }

    updateResults() {
        const resultsElement = this.shadowRoot.querySelector('.search-results')
        resultsElement.innerHTML = ''

        this.results.forEach((user) => {
            const item = document.createElement('li')
            item.innerHTML = `
        <span>${user.displayname}</span>
        <div>
          ${user.relationship === 'friend' ? '<button class="btn btn-danger btn-sm">X</button>' : ''}
          ${user.relationship === 'requested' ? '<button class="btn btn-danger btn-sm">X</button>' : ''}
          ${user.relationship === 'received' ? '<button class="btn btn-success btn-sm">✓</button><button class="btn btn-danger btn-sm">X</button>' : ''}
          ${user.relationship === 'stranger' ? '<button class="btn btn-primary btn-sm">+</button>' : ''}
        </div>
      `

            if (user.relationship === 'friend') {
                item.querySelector('.btn-danger').addEventListener(
                    'click',
                    () => this.removeFriend(user.uid)
                )
            } else if (user.relationship === 'requested') {
                item.querySelector('.btn-danger').addEventListener(
                    'click',
                    () => this.removeFriendRequest(user.uid)
                )
            } else if (user.relationship === 'received') {
                item.querySelector('.btn-success').addEventListener(
                    'click',
                    () => this.acceptFriendRequest(user.uid)
                )
                item.querySelector('.btn-danger').addEventListener(
                    'click',
                    () => this.declineFriendRequest(user.uid)
                )
            } else {
                item.querySelector('.btn-primary').addEventListener(
                    'click',
                    () => this.sendFriendRequest(user.uid)
                )
            }

            resultsElement.appendChild(item)
        })
    }

    async removeFriend(uid) {
        // TODO: Add API call to remove friend
        this.results.delete(uid)
        this.updateResults()
    }

    async removeFriendRequest(uid) {
        // TODO: Add API call to remove friend request
        this.results.delete(uid)
        this.updateResults()
    }

    async acceptFriendRequest(uid) {
        // TODO: Add API call to accept friend request
        this.results.delete(uid)
        this.updateResults()
    }

    async declineFriendRequest(uid) {
        // TODO: Add API call to decline friend request
        this.results.delete(uid)
        this.updateResults()
    }

    async sendFriendRequest(uid) {
        // TODO: Add API call to send friend request
        this.results.delete(uid)
        this.updateResults()
    }
}

customElements.define('friend-search', FriendSearch)
