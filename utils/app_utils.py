import pandas as pd
from sqlalchemy import text
import datetime
from utils.sql_utils import get_sql_query
from utils.wordcloud_utils import generate_wordcloud

def get_df_database(query, engine, params=None):
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    return df

def get_posts_df_on_date(engine, start_date, end_date, comments=False):
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
    params = {"start_date": start_datetime, "end_date": end_datetime}
    if comments:
        query = get_sql_query('select_comments_on_date.sql')
    else:
        query = get_sql_query('select_titles_on_date.sql')
    df = get_df_database(query, engine, params)
    return df

def get_comments_df_from_post(engine, post_id):
    query = get_sql_query('select_comments_from_post.sql')
    params = {"post_id": post_id}
    df = get_df_database(query, engine, params)
    return df

def get_top_10_words(words_dict):
    top_10_words = list(words_dict.keys())[:10]
    df = pd.DataFrame(top_10_words, columns=['Word'])
    df['Rank'] = df.index + 1
    df = df[['Rank', 'Word']]
    df = df.set_index('Rank')
    return df

def append_day(date, engine, comments=False):
    if comments:
        day_df = get_posts_df_on_date(engine, date, date, comments=True)
        day_words = generate_wordcloud(day_df, 'body', figure=False)
    else:
        day_df = get_posts_df_on_date(engine, date, date)
        day_words = generate_wordcloud(day_df, 'title', figure=False)
    
    day_words = get_top_10_words(day_words)
    return day_words['Word']
    