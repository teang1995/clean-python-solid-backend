from dotenv import load_dotenv
import os

load_dotenv()

db_username = os.getenv('DB_USERNAME')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_database = os.getenv('DB_DATABASE')

if __name__ == "__main__":
    print(db_username)
    print(db_password)
    print(db_host)
    print(db_port)
    print(db_database)