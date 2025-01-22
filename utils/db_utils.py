import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text



def get_sql_connection():
    
    load_dotenv()
    
    host = os.getenv('DB_HOST')
    user = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_DATABASE')
    
    if not all([host, user, port, database]):
        raise ValueError("One or more database environment variables are missing.")
    if not password:
        print("Warning: No password found for the database connection. This may or may not be a problem!")
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    try:
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"An error occurred creating the database engine: {e}")
        raise e
    

def execute_sql_transaction(query, engine, data=None):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(query), data)
            transaction.commit()
        except Exception as e:
            print(f"An error occurred executing the query: {e}")
            transaction.rollback()
            raise e
        