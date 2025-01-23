import os

def get_sql_query(query_file):
    # Get the SQL query from the file
    # Get the base directory path of the project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        # Read the SQL query from the file
        with open(f'{base_dir}/SQL/{query_file}', 'r') as file:
            query = file.read()
            return query
    except Exception as e:
        print(f'An error occurred reading the SQL query file: {e}')
        raise e