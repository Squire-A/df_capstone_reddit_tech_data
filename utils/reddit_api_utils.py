import praw
from dotenv import load_dotenv
import os

def get_reddit_client():
    load_dotenv()
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent = os.getenv('REDDIT_USER_AGENT')
    
    if not all([client_id, client_secret, user_agent]):
        raise ValueError("One or more reddit environment variables are missing.")
    
    try:
        reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret, 
                    user_agent=user_agent)
        return reddit
    except Exception as e:
        print(f"An error occurred creating the Reddit client: {e}")
        raise e
    
def get_reddit_subreddit(subreddit_name):
    try:
        reddit = get_reddit_client()
        subreddit = reddit.subreddit(subreddit_name)
        return (reddit, subreddit)
    except Exception as e:
        print(f"An error occurred fetching the subreddit: {e}")
        raise e