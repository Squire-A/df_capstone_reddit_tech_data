from utils.db_utils import get_sql_connection
from utils.reddit_api_utils import get_reddit_subreddit
from utils.pipeline_utils import create_tables, extraction_process

# Set the number of posts and comments to fetch and the subreddit to get them from
NUMBER_OF_POSTS = 2
NUMBER_OF_COMMENTS = 5
SUBREDDIT = "technology"

def main():
    # Get a DB connection engine
    print("Getting SQL connection...")
    engine = get_sql_connection()
    print("SQL connection successful.")

    # Create the required tables if they don't exist
    print("Creating tables...")
    create_tables(engine)
    print("Tables are present and ready for data insertion.")

    # Get a Reddit API client and get the subreddit data object
    print(f"Fetching Reddit API and {SUBREDDIT} subreddit...")
    reddit, subreddit = get_reddit_subreddit(SUBREDDIT)
    print("Reddit API connection established and Subreddit fetched successfully.")

    # Fetch the top hot NUMBER_OF_POSTS from the subreddit and extract and load the post and comment data
    print("Fetching posts and comments and writing to the database...")
    extraction_process(reddit, subreddit, engine, NUMBER_OF_POSTS, NUMBER_OF_COMMENTS)
    print("Posts and comments written to the database successfully.")
    
    print("Pipeline execution complete.")
    
if __name__ == "__main__":
    main()