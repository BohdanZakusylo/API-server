# API-Server

## Getting Started:
### Prerequisites:
- Python (version 3.9 or higher)
- pip

### Setup the virtual environment

`python -m venv .venv`

### For Mac
# Activate the virtual environment
`source .venv/bin/activate`   
`touch .env`  
`cp .env.dist .env`

### For Windows
# Activate the virtual environment
`.venv\Scripts\activate`
`make the .env file and copy everything from .env.dist to .env`

### Install Dependencies:
`pip install -r requirements.txt`

Put certificate and key files into config/server-keys/

Run the server:
`hypercorn app.main:app --keyfile config/server-keys/key.pem --certfile config/server-keys/cert.pem`
`uvicorn app.main:app --reload`
