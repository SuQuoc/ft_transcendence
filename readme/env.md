◀️ [back](https://www.github_link_to_table_of_contents)


# <p align="center">Environment variables</p>

The .env file containing all the necessary variables should be saved here:
repo_root/docker_compose_files/.env

For many variables we have setup default values in the docker-compose yaml files. As some of theme are secrets, we could not setup any default variable, so those variables are mandatory.

## 🧐 Mandatory variables 
| variable name | default | remarks |
| -------- | -------- | -------- |
| EMAIL_HOST    | smtp.gmail.com    | should match with EMAIL_HOST_USER    |
| EMAIL_HOST_USER    | -    | -    |
| EMAIL_HOST_PASSWORD    | -    | -    |
| FT_CLIENT_ID     | -    | -    |◀️ [back](https://www.github_link_to_table_of_contents)


# <p align="center">Environment variables</p>

The .env file containing all the necessary variables should be saved here:
repo_root/docker_compose_files/.env

For many variables we have setup default values in the docker-compose yaml files. As some of theme are secrets, we could not setup any default variable, so those variables are mandatory.

## 🧐 Mandatory variables 
| variable name | default | remarks |
| -------- | -------- | -------- |
| EMAIL_HOST    | smtp.gmail.com    | should match with EMAIL_HOST_USER    |
| EMAIL_HOST_USER    | -    | -    |
| EMAIL_HOST_PASSWORD    | -    | -    |
| FT_CLIENT_ID     | -    | -    |
| FT_CLIENT_SECRET    | -    | -    |
        
## 🧐 Optional variables 
(some like django SECRET_KEY will be mandatory in the end)

| variable name | default | remarks |
| -------- | -------- | -------- |
| PYTHONUNBUFFERED              | -                         | to do |
| POSTGRES_DB_GAME              | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_DB_MANAGEMENT        | default_db                | - |
| POSTGRES_DB_REG               | reg_postgress_db          | - |
| POSTGRES_USER_GAME            | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_USER_MANAGEMENT      | posty                     | - |
| POSTGRES_USER_REG             | reg_postgress_user        | - |
| POSTGRES_PASSWORD_GAME        | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_PASSWORD_MANAGEMENT  | insecurepass              | - |
| POSTGRES_PASSWORD_REG         | reg_postgress_password    | - |
| POSTGRES_ACCESS_USER_GAME     | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_ACCESS_USER_MANAGEMENT   | accessy               | - |
| POSTGRES_ACCESS_USER_REG      | reg_postgress_access_user | - |
| POSTGRES_ACCESS_PASSWORD_GAME |  XXXXXXXXXXX              | needs to be setup correctly in game.yml   |
| POSTGRES_ACCESS_PASSWORD_REG  | reg_postgress_access_password | - |
| POSTGRES_ACCESS_PASSWORD_REG  | accesspass                | - |
| DJANGO_DEBUG_GAME             |                           | to do |
| DEBUG                         | False                     | to do | 
| DJANGO_DEBUG_REG              | False                     | -  |
| DB_HOST_REG                   | db_registration           | to do |
| DB_PORT                       | 5432                      | to do |
| SECRET_KEY_REG                | ***                       | Django secrets  |
| SECRET_KEY_GAME               |  XXXXXXXXXXX              | needs to be setup correctly in game.yml   |
| SERVER_URL                    | https://localhost:8000    | should match with domain |
| DOMAIN    | localhost    | should match with SERVER_URL    |


### ❗️❗️❗️❗️❗️❗️TO DOS ❗️❗️❗️❗️❗️

- DJANGO_ALLOWED_HOSTS, ENGINE should be deleted in the game.yml (we are not using them)
- PYTHONUNBUFFERED should be deleted since we do not call it
- DB_HOST and DB_PORT are used differently within the containers - either we harcode it in the yaml or not
- usermanagement container still uses the admin user (because of the django tests i guess)
- DEBUG should disapear and we should have DEBUG_MANAGEMENT and DEBUG_GAME
- DEBUG is hardcoded in the DJANGO game container
- do we need the following variables in UM: DJ_ALLOWED_HOSTS, DJ_SUDO_USERNAME_MANAGEMENT, DJ_SUDO_EMAIL_MANAGEMENT, DJ_SUDO_PASSWORD_MANAGEMENT:-transcendence, JWT_SECRET
- if we use an admin in user management i would also do one in the other containers (REG and GAME)

### ❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️

## 🧐 Remarks

rules that user should follow when setting up their own environment variables

### Django secrets

according to [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html) the secrets should 

- be at least 50 characters long
- contain a mix of letters, digits, and symbols
- generated securely following one of those [secure functions]()
- be rotated regularly

### Usernames

### Passwords
| FT_CLIENT_SECRET    | -    | -    |
        
## 🧐 Optional variables 
(some like django SECRET_KEY will be mandatory in the end)

| variable name | default | remarks |
| -------- | -------- | -------- |
| PYTHONUNBUFFERED              | -                         | to do |
| POSTGRES_DB_GAME              | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_DB_MANAGEMENT        | default_db                | - |
| POSTGRES_DB_REG               | reg_postgress_db          | - |
| POSTGRES_USER_GAME            | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_USER_MANAGEMENT      | posty                     | - |
| POSTGRES_USER_REG             | reg_postgress_user        | - |
| POSTGRES_PASSWORD_GAME        | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_PASSWORD_MANAGEMENT  | insecurepass              | - |
| POSTGRES_PASSWORD_REG         | reg_postgress_password    | - |
| POSTGRES_ACCESS_USER_GAME     | XXXXXXXXXXX               | needs to be setup correctly in game.yml   |
| POSTGRES_ACCESS_USER_MANAGEMENT   | accessy               | - |
| POSTGRES_ACCESS_USER_REG      | reg_postgress_access_user | - |
| POSTGRES_ACCESS_PASSWORD_GAME |  XXXXXXXXXXX              | needs to be setup correctly in game.yml   |
| POSTGRES_ACCESS_PASSWORD_REG  | reg_postgress_access_password | - |
| POSTGRES_ACCESS_PASSWORD_REG  | accesspass                | - |
| DJANGO_DEBUG_GAME             |                           | to do |
| DEBUG                         | False                     | to do | 
| DJANGO_DEBUG_REG              | False                     | -  |
| DB_HOST_REG                   | db_registration           | to do |
| DB_PORT                       | 5432                      | to do |
| SECRET_KEY_REG                | ***                       | Django secrets  |
| SECRET_KEY_GAME               |  XXXXXXXXXXX              | needs to be setup correctly in game.yml   |
| SERVER_URL                    | https://localhost:8000    | should match with domain |
| DOMAIN    | localhost    | should match with SERVER_URL    |


### ❗️❗️❗️❗️❗️❗️TO DOS ❗️❗️❗️❗️❗️

- DJANGO_ALLOWED_HOSTS, ENGINE should be deleted in the game.yml (we are not using them)
- PYTHONUNBUFFERED should be deleted since we do not call it
- DB_HOST and DB_PORT are used differently within the containers - either we harcode it in the yaml or not
- usermanagement container still uses the admin user (because of the django tests i guess)
- DEBUG should disapear and we should have DEBUG_MANAGEMENT and DEBUG_GAME
- DEBUG is hardcoded in the DJANGO game container
- do we need the following variables in UM: DJ_ALLOWED_HOSTS, DJ_SUDO_USERNAME_MANAGEMENT, DJ_SUDO_EMAIL_MANAGEMENT, DJ_SUDO_PASSWORD_MANAGEMENT:-transcendence, JWT_SECRET
- if we use an admin in user management i would also do one in the other containers (REG and GAME)

### ❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️❗️

## 🧐 Remarks

rules that user should follow when setting up their own environment variables

### Django secrets

according to [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/Django_Security_Cheat_Sheet.html) the secrets should 

- be at least 50 characters long
- contain a mix of letters, digits, and symbols
- generated securely following one of those [secure functions]()
- be rotated regularly

### Usernames

### Passwords