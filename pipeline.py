import pandas as pd
from utils.db_utils import get_sql_connection, execute_sql_transaction
from utils.reddit_api_utils import get_reddit_subreddit

# Set the number of posts and comments to fetch
NUMBER_OF_POSTS = 2
NUMBER_OF_COMMENTS = 5
SUBREDDIT = "technology"

# Get a DB connection engine
engine = get_sql_connection()

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
    date_created TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES student.as_capstone_posts(post_id)
);
"""

execute_sql_transaction(create_comments_table_query, engine)
execute_sql_transaction(create_posts_table_query, engine)

# Get a Reddit API client
reddit, subreddit = get_reddit_subreddit(SUBREDDIT)

# Select the /r/technology subreddit
# subreddit = reddit.subreddit(SUBREDDIT)
            
for post in subreddit.hot(limit=NUMBER_OF_POSTS):
    # post_id = post.id
    # title = post.title
    # date_created = pd.to_datetime(post.created_utc, unit='s')
    # score = post.score
    # comments = post.num_comments
    # url = post.url
    
    insert_post_query = """
    INSERT INTO student.as_capstone_posts (post_id, title, date_created, score, comments, url)
    VALUES (:post_id, :title, :date_created, :score, :comments, :url)
    ON CONFLICT (post_id)
    DO UPDATE SET 
        score = EXCLUDED.score, 
        comments = EXCLUDED.comments;
    """
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
                'post_id': post.id,
                'body': comment.body,
                'score': comment.score,
                'date_created': pd.to_datetime(comment.created_utc, unit='s')
                }
        
        execute_sql_transaction(insert_comments_query, engine, data)
    
    delete_comments_query = """
            DELETE FROM student.as_capstone_comments
            WHERE post_id = :post_id AND comment_id NOT IN (
                SELECT comment_id FROM student.as_capstone_comments
                WHERE post_id = :post_id
                ORDER BY score DESC
                LIMIT :number_of_comments
            )
        """
    data = {'post_id': post.id,
            'number_of_comments': NUMBER_OF_COMMENTS}
    
    execute_sql_transaction(delete_comments_query, engine, data)
    