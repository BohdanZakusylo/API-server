#API-Server

## Prerequisites:
- Python 3.9 or higher
- pip

## Getting started

1) Install Microsoft ODBC 18 Driver

MacOS:

`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"`

`brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release`

`brew update`

`HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18`

Windows:

Download the installer from here and run it:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16

Go to the project folder

2) Setup the virtual environment
`python -m venv .venv`

3) Activate the virtual environment
Windows:
`.venv\Scripts\activate`
Mac:
`source .venv/bin/activate`

4) Environment variables
Navigate to the project folder
Create a .env file
Copy the contents from .env.dist into .env

Here is an example of a command for Mac:

`touch .env`
`cp .env.dist .env`

Fill out the .env

SERVER=`host` (for localhost, use `127.0.0.1`)

DATABASE=`Netflix`

USER_NAME=`user`

PASSWORD=`password`

PUBLIC_KEY=`config/jwt/public.pem`

PRIVATE_KEY=`config/jwt/private.pem`

API_ADDRESS=`127.0.0.1`


5) Certificates
Put private and public keys into config/jwt


6) Install dependencies
`pip install --no-binary :all: pyodbc`
`pip install -r requirements.txt`


7) Run the program
`uvicorn app.main:app --reload`
