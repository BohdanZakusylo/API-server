import app.common as common

common.load_dotenv(".env")

SERVER = common.os.getenv("SERVER")
DATABASE = common.os.getenv("DATABASE")
USERNAME = common.os.getenv("USER_NAME")
PASSWORD = common.os.getenv("PASSWORD")

connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

conn = common.pyodbc.connect(connectionString)
cursor = conn.cursor()

print("Connection established")
