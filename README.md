# API-server
## Start

`python(python3) -m venv .venv`

### Mac

`source .venv/bin/activate`   
`touch .env`  
`cp .env.dist .env`

### Windows
`.venv\Scripts\activate`
`make the .env file and copy everything from .env.dist to .env`
    

`pip install -r requirements.txt`
`uvicorn app.main:app --reload` 