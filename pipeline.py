import pandas as pd
from utils.db_utils import get_sql_connection, execute_sql_transaction
from utils.reddit_api_utils import get_reddit_subreddit
from utils.sql_utils import get_sql_query

# Set the number of posts and comments to fetch
NUMBER_OF_POSTS = 2
NUMBER_OF_COMMENTS = 5
SUBREDDIT = "technology"

# Get a DB connection engine
engine = get_sql_connection()

# Create the tables if they are not present
create_posts_table_query = get_sql_query('create_posts_table.sql')
create_comments_table_query = get_sql_query('create_comments_table.sql')

execute_sql_transaction(create_comments_table_query, engine)
execute_sql_transaction(create_posts_table_query, engine)

# Get a Reddit API client and select the subreddit
reddit, subreddit = get_reddit_subreddit(SUBREDDIT)
            
# Fetch the top hot NUMBER_OF_POSTS from the subreddit
for post in subreddit.hot(limit=NUMBER_OF_POSTS):

    insert_post_query = get_sql_query('insert_post.sql')

    data = {'post_id': post.id, 
            'title': post.title, 
            'date_created': pd.to_datetime(post.created_utc, unit='s'), 
            'score': post.score, 
            'comments': post.num_comments, 
            'url': post.url
            }
    
    execute_sql_transaction(insert_post_query, engine, data)
        
    # Extract comments
    submission = reddit.submission(id=post.id)
    submission.comment_sort = 'top'
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list()[:NUMBER_OF_COMMENTS]:
        
        insert_comments_query = get_sql_query('insert_comments.sql')

        data = {'comment_id': comment.id,
                'post_id': post.id,
                'body': comment.body,
                'score': comment.score,
                'date_created': pd.to_datetime(comment.created_utc, unit='s')
                }
        
        execute_sql_transaction(insert_comments_query, engine, data)
    
    delete_excess_comments_query = get_sql_query('delete_excess_comments.sql')
    
    data = {'post_id': post.id,
            'number_of_comments': NUMBER_OF_COMMENTS}
    
    execute_sql_transaction(delete_excess_comments_query, engine, data)
    