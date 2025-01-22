import pandas as pd
from sqlalchemy import text
import datetime
from utils.sql_utils import get_sql_query

def get_df_database(query, engine, params=None):
    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)
    return df

def get_posts_df_on_date(engine, start_date, end_date):
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)
    params = {"start_date": start_datetime, "end_date": end_datetime}
    query = get_sql_query('select_titles_on_date.sql')
    df = get_df_database(query, engine, params)
    return df

def get_comments_df_from_post(engine, post_id):
    query = get_sql_query('select_comments_from_post.sql')
    params = {"post_id": post_id}
    df = get_df_database(query, engine, params)
    return df