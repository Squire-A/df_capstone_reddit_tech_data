import streamlit as st
import pandas as pd
from utils.wordcloud_utils import generate_wordcloud
from utils.db_utils import get_sql_connection
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv('.env')
    
host = os.getenv('DB_HOST')
user = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
port = os.getenv('DB_PORT')
database = os.getenv('DB_DATABASE')

print(host, user, password, port, database)

if not all([host, user, port, database]):
    raise ValueError("One or more database environment variables are missing.")
if not password:
    print("Warning: No password found for the database connection. This may or may not be a problem!")

connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

try:
    engine = create_engine(connection_string)
except Exception as e:
    print(f"An error occurred creating the database engine: {e}")
    raise e

with engine.connect() as conn:
    df = pd.read_sql_query("SELECT body FROM student.as_capstone_comments WHERE post_id = '1i6i5jm';", conn)
    
df
all_comments = ' '.join(body for body in df['body'].str.strip())
st.write(all_comments)
# fig = generate_wordcloud(all_comments)

# st.pyplot(fig)