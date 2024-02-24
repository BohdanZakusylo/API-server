# API-Server

## Getting Started:
### Prerequisites:
- Python (version 3.9 or higher)
- pip

### Setup the virtual environment

`python -m venv .venv`

## For Mac
### Activate the virtual environment
`source .venv/bin/activate`   
`touch .env`  
`cp .env.dist .env`

## For Windows
### Activate the virtual environment
`.venv\Scripts\activate`
`make the .env file and copy everything from .env.dist to .env`
`paste all the information in .env file that was provided`
Put private.pem and public.pem into `config/jwt/`

### Install Dependencies:
`pip install -r requirements.txt`

Put certificate and key files into config/server-keys/

Run the server:
Normally, run api on hypercorn. Hypercorn is an ASGI server, that supports https protocol. However, django doesn't support https, so we had to roll back on http. For using web page, please run api on uvicorn. Command is bellow.
`hypercorn app.main:app --keyfile config/server-keys/key.pem --certfile config/server-keys/cert.pem`
`uvicorn app.main:app --reload`

## Setup .env file

SERVER=`host` (for localhost, use `127.0.0.1`)

DATABASE=`Netflix`

USER_NAME=`user`

PASSWORD=`password`

PUBLIC_KEY=`config/jwt/public.pem`

PRIVATE_KEY=`config/jwt/private.pem`