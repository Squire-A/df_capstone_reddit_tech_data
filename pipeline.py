import pandas as pd
from utils.db_utils import get_sql_connection, execute_sql_transaction
from utils.reddit_api_utils import get_reddit_subreddit
from utils.sql_utils import get_sql_query
from utils.pipeline_utils import create_tables

# Set the number of posts ,comments to fetch and subreddit to get them from
NUMBER_OF_POSTS = 10
NUMBER_OF_COMMENTS = 200
SUBREDDIT = "technology"

def main():
    # Get a DB connection engine
    print("Getting SQL connection...")
    engine = get_sql_connection()
    print("SQL connection successful.")

    # Create the required tables if they don't exist
    print("Creating tables...")
    create_tables(engine)
    print("Tables created successfully.")

    # Get a Reddit API client and get the subreddit data object
    print("Fetching subreddit...")
    reddit, subreddit = get_reddit_subreddit(SUBREDDIT)
    print("Subreddit fetched successfully.")

    # Fetch the top hot NUMBER_OF_POSTS from the subreddit
    print("Fetching posts and comments and writing to the database...")
    for post in subreddit.hot(limit=NUMBER_OF_POSTS):
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
            
        # Extract comments from the post
        submission = reddit.submission(id=post.id)
        # Set the comment sort order to top
        submission.comment_sort = 'top'
        # Flatten the comment tree
        submission.comments.replace_more(limit=0)
        
        # Fetch the top NUMBER_OF_COMMENTS comments and loop through them
        for comment in submission.comments.list()[:NUMBER_OF_COMMENTS]:
            
            # Retrieve query to insert comment to the database
            insert_comments_query = get_sql_query('insert_comments.sql')
            # Compile a dictionary of the data to be inserted
            data = {'comment_id': comment.id,
                    'post_id': post.id,
                    'body': comment.body,
                    'score': comment.score,
                    'date_created': pd.to_datetime(comment.created_utc, unit='s')
                    }
            # Execute the query to insert the comment data
            execute_sql_transaction(insert_comments_query, engine, data)
        
        # Retrieve query to delete excess comments from the database
        delete_excess_comments_query = get_sql_query('delete_excess_comments.sql')
        # Compile a dictionary of the data to be deleted
        data = {'post_id': post.id,
                'number_of_comments': NUMBER_OF_COMMENTS}
        # Execute the query to delete any excess comments
        execute_sql_transaction(delete_excess_comments_query, engine, data)
    print("Posts and comments written to the database successfully.")
    print("Pipeline execution complete.")
    
if __name__ == "__main__":
    main()