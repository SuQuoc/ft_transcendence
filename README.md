# ft_transcendence

This is the final project of the 42 school curriculum (also known as common core). It is a full stack project that requires a group of three to five students.

https://github.com/user-attachments/assets/1dbf0eaa-4f61-472d-a9e9-cd9612718202

Students need to create a single page application without any frontend framework (only vanilla Javascript and Bootstrap) that allows users to sign up and play the classic game Pong against each other, either local or remote.

- [The project](#the-project)
  - [Team](#team)
  - [Architecture](#architecture)
  - [Technology Stack](#technology-stack)
    - [Frontend](#frontend)
    - [Backend](#backend)
    - [DevOps](#devops)
    - [Security Features](#security-features)
    - [Game Features](#game-features)
    - [Data Storage](#data-storage)
  - [Subject Requirements](#subject-requirements)
- [Technical documentation](#technical-documentation)
  - [API Documentation](#api-documentation)
  - [Configuration](#configuration)
  - [Installation Guide](#installation-guide)
    - [Prerequisites](#prerequisites)
    - [Setup Steps](#setup-steps)
    - [Testing](#testing)
    - [Common Makefile Commands](#common-makefile-commands)
    - [Configuration Location](#configuration-location)
    - [Required Variables](#required-variables)
    - [Recommended optional Variables](#recommended-optional-variables)
      - [User Management Service](#user-management-service)
      - [Registration Service](#registration-service)
      - [Server Configuration](#server-configuration)
      - [Security Keys](#security-keys)
    - [Important Considerations](#important-considerations)
    - [Notes](#notes)

## The project

###  Team

| Name                                       | Focus                                       |
|--------------------------------------------|---------------------------------------------|
| [**Fiona**](https://github.com/AnnaFiona)  | Frontend Game and Game Logic                |
| [**Annie**](https://github.com/AnnieG84)   | Backend Registration, Cybersecurity, DevOps |
| [**Quoc Su**](https://github.com/SuQuoc)   | Backend User Management and Game, DevOps    |
| [**Michael**](https://github.com/derfleck) | Frontend User Management and Registration   |

### Architecture
The project is built as a microservices architecture consisting of several containers:

- **Frontend**: Vanilla JavaScript SPA with Bootstrap
  - Single page application without framework
  - Bootstrap for styling
  - WebSocket integration for real-time features

- **Backend Services**:
  - User Management Service (Django)
  - Registration Service (Django)
  - Game Service (Django)
  - PostgreSQL databases (separate for each service)
  - Nginx as reverse proxy

### Technology Stack
#### Frontend
- Vanilla JavaScript
- Bootstrap 5.3
- WebSocket for real-time communication
- Custom web components

#### Backend
- Django REST Framework
- PostgreSQL
- WebSocket (for game/chat functionality)
- OAuth2 integration (through [42 API](https://api.intra.42.fr/apidoc))
- JWT for authentication
- Redis for caching and message broker

#### DevOps
- Docker & Docker Compose
- Nginx
- Environment variable management

#### Security Features
- Two-factor authentication (2FA)
- JWT-based authentication
- GDPR compliance with user data management
- Remote authentication support
- Backup codes for 2FA

#### Game Features
- Multiplayer Pong game
- Real-time gameplay using WebSockets
- Tournament system
- User statistics tracking
- Mobile support for gameplay

#### Data Storage
Each microservice has its own PostgreSQL database:
- User Management DB
- Registration DB
- Game DB

### Subject Requirements

The subject requires some mandatory technologies and features to be implemented. Additionally there's a choice of different modules, differentiated by their difficulty as major and minor. The project must have at least seven major modules. Two minor modules represent one major module.

| Module type                  | Description                                                                                       | Difficulty | Done |
|------------------------------|---------------------------------------------------------------------------------------------------|------------|------|
| Web                          | Use a Framework to build the backend.                                                             | Major      | ✅    |
| Web                          | Store the score of a tournament in the Blockchain.                                                | Major      | ❌    |
| Web                          | Use a framework or a toolkit to build the frontend.                                               | Minor      | ✅    |
| Web                          | Use a database for the backend.                                                                   | Minor      | ✅    |
| User management              | Standard user management, authentication, users across tournaments.                               | Major      | ✅    |
| User management              | Implementing a remote authentication.                                                             | Major      | ✅    |
| Gameplay and user experience | Remote players                                                                                    | Major      | ✅    |
| Gameplay and user experience | Multiplayers (more than 2 in the same game).                                                      | Major      | ✅    |
| Gameplay and user experience | Add Another Game with User History and Matchmaking.                                               | Major      | ❌    |
| Gameplay and user experience | Game Customization Options.                                                                       | Minor      | ❌    |
| Gameplay and user experience | Live chat.                                                                                        | Major      | ❌    |
| AI-Algo                      | Introduce an AI Opponent.                                                                         | Major      | ❌    |
| AI-Algo                      | User and Game Stats Dashboards                                                                    | Minor      | ❌    |
| Cybersecurity                | Implement WAF/ModSecurity with Hardened Configuration and HashiCorp Vault for Secrets Management. | Major      | ❌    |
| Cybersecurity                | GDPR Compliance Options with User Anonymization, Local Data Management, and Account Deletion.     | Minor      | ✅    |
| Cybersecurity                | Implement Two-Factor Authentication (2FA) and JWT.                                                | Major      | ✅    |
| Devops                       | Infrastructure Setup for Log Management.                                                          | Major      | ❌    |
| Devops                       | Monitoring system.                                                                                | Minor      | ❌    |
| Devops                       | Designing the Backend as Microservices.                                                           | Major      | ✅    |
| Graphics                     | Use of advanced 3D techniques.                                                                    | Major      | ❌    |
| Accessibility                | Support on all devices.                                                                           | Minor      | ✅    |
| Accessibility                | Expanding Browser Compatibility                                                                   | Minor      | ✅    |
| Accessibility                | Multiple language supports                                                                        | Minor      | ❌    |
| Accessibility                | Add accessibility for Visually Impaired Users.                                                    | Minor      | ✅    |
| Accessibility                | Server-Side Rendering (SSR) Integration.                                                          | Minor      | ❌    |
| Server-Side Pong             | Replacing Basic Pong with Server-Side Pong and Implementing an API.                               | Major      | ❌    |
| Server-Side Pong             | Enabling Pong Gameplay via CLI against Web Users with API Integration.                            | Major      | ❌    |

## Technical documentation
### API Documentation
API documentation is available in transcendence.yaml using OpenAPI 3.0.3 specification. It's currently not up to date and will be updated.

### Configuration
Environment variables are managed through `.env` files in the docker_compose_files directory. See Environment Variables Documentation for detailed setup instructions.

### Installation Guide

#### Prerequisites

- Docker and Docker Compose
- Git
- SMTP server credentials (e.g. Gmail)
- 42 API credentials (if using 42 authentication)

#### Setup Steps

1. **Clone the Repository**
```sh
git clone [repository-url]
cd ft_transcendence
```

2. **Configure Environment Variables**
```sh
# Create .env file in docker_compose_files directory
cd docker_compose_files
touch .env
```

3. **Set Required Environment Variables**
```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# 42 API Configuration
FT_CLIENT_ID=your-42-client-id
FT_CLIENT_SECRET=your-42-client-secret

# Basic Configuration
DOMAIN=localhost
SSL_PORT=8443
PLAIN_PORT=8080
```

4. **Generate SSL and JWT Keys**
```sh
make keys
```

5. **Build and Start Services**
```sh
# Build and start all containers
make build_up
```

6. **Access the Application**
- Open your browser and navigate to `https://localhost:8443`
- Accept the missing certificate warning if you have not imported the generated SSL root certificate in your browser. In Firefox you can import the certificate under Settings / Privacy & Security / View Certficates. Click on Import and then choose src/common_files/ssl_certs/root-ca.crt.

#### Testing

To run the test suite:
```sh
make test
```

#### Common Makefile Commands

```sh
# Start services
make up

# Stop services
make down

# Rebuild services
make re

# Clean up everything
make fclean
```

#### Configuration Location

Create your `.env` file in:
```
repo_root/docker_compose_files/.env
```

#### Required Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `EMAIL_HOST` | SMTP server address | smtp.gmail.com |
| `EMAIL_HOST_USER` | Email address for SMTP | - |
| `EMAIL_HOST_PASSWORD` | SMTP password/app password | - |
| `FT_CLIENT_ID` | 42 OAuth client ID | - |
| `FT_CLIENT_SECRET` | 42 OAuth client secret | - |

#### Recommended optional Variables

##### User Management Service
| Variable | Default | Purpose |
|----------|----------|----------|
| `POSTGRES_DB_MANAGEMENT` | default_db | Database name |
| `POSTGRES_USER_MANAGEMENT` | posty | Database user |
| `POSTGRES_PASSWORD_MANAGEMENT` | insecurepass | Database password |
| `POSTGRES_ACCESS_USER_MANAGEMENT` | accessy | Access user |
| `POSTGRES_ACCESS_PASSWORD_MANAGEMENT` | accesspass | Access password |

##### Registration Service
| Variable | Default | Purpose |
|----------|----------|----------|
| `POSTGRES_DB_REG` | reg_postgress_db | Database name |
| `POSTGRES_USER_REG` | reg_postgress_user | Database user |
| `POSTGRES_PASSWORD_REG` | reg_postgress_password | Database password |
| `POSTGRES_ACCESS_USER_REG` | reg_postgress_access_user | Access user |
| `POSTGRES_ACCESS_PASSWORD_REG` | reg_postgress_access_password | Access password |

##### Server Configuration
| Variable | Default | Purpose |
|----------|----------|----------|
| `SERVER_URL` | https://localhost:8443 | Server URL (must match domain) |
| `DOMAIN` | localhost | Domain name |
| `DEBUG` | False | Debug mode flag |
| `DB_PORT` | 5432 | Database port |

##### Security Keys
| Variable | Purpose | Requirements |
|----------|----------|----------|
| `SECRET_KEY_REG` | Django registration secret | See security notes |
| `SECRET_KEY_GAME` | Django game service secret | See security notes |

#### Important Considerations

1. Default values are provided in docker-compose files for development
2. Production deployments should override default values
3. Sensitive variables must be properly secured
4. Server URL and domain settings must match

#### Notes

- The project uses self-signed certificates for development
- Default credentials and settings are for development only
- Make sure ports 8080 and 8443 are available
