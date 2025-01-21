import praw
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import pandas as pd

NUMBER_OF_POSTS = 10
NUMBER_OF_COMMENTS = 10

load_dotenv()

# DB Configuration
host = os.getenv('DB_HOST')
user = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
port = os.getenv('DB_PORT')
database = os.getenv('DB_DATABASE')
dbschema = os.getenv('DB_NAME')

# Reddit Configuration
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = os.getenv('REDDIT_USER_AGENT')

# Connect to the database
connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)
connection = engine.connect()


# Create the tables if they are not present
create_posts_table_query = """
CREATE TABLE IF NOT EXISTS student.as_capstone_posts (
    post_id VARCHAR(10) PRIMARY KEY,
    title TEXT,
    date_created TIMESTAMP,
    score INT,
    comments INT,
    url TEXT
);
"""

create_comments_table_query = """
CREATE TABLE IF NOT EXISTS student.as_capstone_comments (
    comment_id VARCHAR(10) PRIMARY KEY,
    post_id VARCHAR(10),
    body TEXT,
    score INT,
    date_created TIMESTAMP
);
"""

with engine.connect() as connection:
    transaction = connection.begin()
    try:
        connection.execute(text(create_posts_table_query))
        connection.execute(text(create_comments_table_query))
        transaction.commit()
    except:
        transaction.rollback()
        raise
    
# Initialize the Reddit API
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Select the /r/technology subreddit
subreddit = reddit.subreddit("technology")
            
for post in subreddit.hot(limit=NUMBER_OF_POSTS):
    post_id = post.id
    title = post.title
    date_created = pd.to_datetime(post.created_utc, unit='s')
    score = post.score
    comments = post.num_comments
    url = post.url
    
    insert_post_query = """
    INSERT INTO student.as_capstone_posts (post_id, title, date_created, score, comments, url)
    VALUES (:post_id, :title, :date_created, :score, :comments, :url)
    ON CONFLICT (post_id)
    DO UPDATE SET 
        score = EXCLUDED.score, 
        comments = EXCLUDED.comments;
    """
    data = {'post_id': post_id, 
                'title': title, 
                'date_created': date_created, 
                'score': score, 
                'comments': comments, 
                'url': url}
    
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text(insert_post_query), data)
            transaction.commit()
        except:
            transaction.rollback()
            raise
        
    # Extract comments
    submission = reddit.submission(id=post_id)
    submission.comment_sort = "top"
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list()[:NUMBER_OF_COMMENTS]:
        
        insert_comments_query = """
                INSERT INTO student.as_capstone_comments (comment_id, post_id, body, score, date_created)
                VALUES (:comment_id, :post_id, :body, :score, :date_created)
                ON CONFLICT (comment_id) 
                DO UPDATE SET 
                    body = EXCLUDED.body, 
                    score = EXCLUDED.score; 
                """
        data = {'comment_id': comment.id,
                'post_id': post_id,
                'body': comment.body,
                'score': comment.score,
                'date_created': pd.to_datetime(comment.created_utc, unit='s')
            }
                
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(insert_comments_query), data)
                transaction.commit()
            except:
                transaction.rollback()
                raise
    
    delete_comments_query = """
            DELETE FROM student.as_capstone_comments
            WHERE post_id = :post_id AND comment_id NOT IN (
                SELECT comment_id FROM student.as_capstone_comments
                WHERE post_id = :post_id
                ORDER BY score DESC
                LIMIT :number_of_comments
            )
        """
    data = {'post_id': post_id,
            'number_of_comments': NUMBER_OF_COMMENTS}
    with engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(text(delete_comments_query), data)
                transaction.commit()
            except:
                transaction.rollback()
                raise
    