from dotenv import load_dotenv
import os
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
if __name__ == "__main__":
    print(db_username)
    print(db_password)
    print(db_host)
    print(db_port)
    print(db_database)