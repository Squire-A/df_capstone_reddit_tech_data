from utils.db_utils import execute_sql_transaction
from utils.sql_utils import get_sql_query
import pandas as pd

def create_tables(engine):
    # Retrieve queries to create the posts and comments tables
    create_posts_table_query = get_sql_query('create_posts_table.sql')
    create_comments_table_query = get_sql_query('create_comments_table.sql')
    # Execute the queries to create the tables
    execute_sql_transaction(create_posts_table_query, engine)
    execute_sql_transaction(create_comments_table_query, engine)
    
    
def extract_load_post(post, engine):
    # Retrieve query to insert post to the database
    insert_post_query = get_sql_query('insert_post.sql')
    # Compile a dictionary of the data to be inserted
    data = {'post_id': post.id, 
            'title': post.title, 
            'date_created': pd.to_datetime(post.created_utc, unit='s'), 
            'score': post.score, 
            'comments': post.num_comments, 
            'url': post.url
            }
    # Execute the query to insert the post data
    execute_sql_transaction(insert_post_query, engine, data)
    
    
def extract_comments(reddit, post_id, no_of_comments):
    # Fetch the top NUMBER_OF_COMMENTS from the post
    
    # Extract comments from the post
    submission = reddit.submission(id=post_id)
    # Set the comment sort order to top
    submission.comment_sort = 'top'
    # Flatten the comment tree
    submission.comments.replace_more(limit=0)
    # Make a list of the top NUMBER_OF_COMMENTS comments
    comments = submission.comments.list()[:no_of_comments]
    
    return comments


def load_comments(comments, post_id, engine):
    for comment in comments:
        # Retrieve query to insert comment to the database
        insert_comments_query = get_sql_query('insert_comments.sql')
        
        # Compile a dictionary of the data to be inserted
        data = {'comment_id': comment.id,
                'post_id': post_id,
                'body': comment.body,
                'score': comment.score,
                'date_created': pd.to_datetime(comment.created_utc, unit='s')
                }
        # Execute the query to insert the comment data
        execute_sql_transaction(insert_comments_query, engine, data)


def delete_excess_comments(post_id, no_of_comments, engine):
    # Retrieve query to delete excess comments from the database
    delete_excess_comments_query = get_sql_query('delete_excess_comments.sql')
    
    # Compile a dictionary of the data to be deleted
    data = {'post_id': post_id,
            'number_of_comments': no_of_comments}
    
    # Execute the query to delete any excess comments
    execute_sql_transaction(delete_excess_comments_query, engine, data)
    
    
def extraction_process(reddit, subreddit, engine, no_of_posts, no_of_comments):
    try:
        # Iterate through the desired number of hot posts
        for post in subreddit.hot(limit=no_of_posts):
            # Extract and load the post data
            extract_load_post(post, engine)
            
            # Extract comments from the post
            comments = extract_comments(reddit, post.id, no_of_comments)
            
            # Load the comments to the database
            load_comments(comments, post.id, engine)
            
            # Delete any excess comments
            delete_excess_comments(post.id, no_of_comments, engine)
    except Exception as e:
        print(f'There was an error during extraction and loading to the database {e}')
        raise e