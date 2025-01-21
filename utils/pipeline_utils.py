from utils.db_utils import execute_sql_transaction
from utils.sql_utils import get_sql_query

def create_tables(engine):
    # Retrieve queries to create the posts and comments tables
    create_posts_table_query = get_sql_query('create_posts_table.sql')
    create_comments_table_query = get_sql_query('create_comments_table.sql')
    # Execute the queries to create the tables
    execute_sql_transaction(create_posts_table_query, engine)
    execute_sql_transaction(create_comments_table_query, engine)
    