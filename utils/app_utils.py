import pandas as pd
from sqlalchemy import text
import datetime
from utils.sql_utils import get_sql_query
from utils.wordcloud_utils import generate_wordcloud

def get_df_database(query, engine, params=None):
    # Get a dataframe from the database
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    return df

def get_posts_df_on_date(engine, start_date, end_date, comments=False):
    # Get the posts for the selected date range
    # Get the start and end datetime objects
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
    # Get the posts for the selected date range
    params = {"start_date": start_datetime, "end_date": end_datetime}
    if comments:
        query = get_sql_query('select_comments_on_date.sql')
    else:
        query = get_sql_query('select_titles_on_date.sql')
    df = get_df_database(query, engine, params)
    return df

def get_comments_df_from_post(engine, post_id):
    # Get a df of the comments from the specified post
    query = get_sql_query('select_comments_from_post.sql')
    params = {"post_id": post_id}
    df = get_df_database(query, engine, params)
    return df

def get_top_10_words(words_dict):
    # Get the top 10 words from the given dictionary
    top_10_words = list(words_dict.keys())[:10]
    # Make a df of the top 10 words
    df = pd.DataFrame(top_10_words, columns=['Word'])
    # Add a rank column
    df['Rank'] = df.index + 1
    # Set the df to just the Rank and Word column
    df = df[['Rank', 'Word']]
    # Make the Rank column the df index
    df = df.set_index('Rank')
    return df

def append_day(date, engine, comments=False):
    # Get the posts or comments words
    if comments:
        day_df = get_posts_df_on_date(engine, date, date, comments=True)
        day_words = generate_wordcloud(day_df, 'body', figure=False)
    else:
        day_df = get_posts_df_on_date(engine, date, date)
        day_words = generate_wordcloud(day_df, 'title', figure=False)
    # Get the top 10 words
    day_words = get_top_10_words(day_words)
    # Return just the word column to be appended
    return day_words['Word']
    