import os

def get_sql_query(query_file):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(f'{base_dir}/SQL/{query_file}', 'r') as file:
            query = file.read()
            return query
    except Exception as e:
        print(f'An error occurred reading the SQL query file: {e}')
        raise e