import streamlit as st
import pandas as pd
from utils.wordcloud_utils import generate_wordcloud
from utils.db_utils import get_sql_connection
import datetime
from utils.app_utils import get_posts_df_on_date, get_comments_df_from_post

MIN_DATE = datetime.date(2025, 1, 21)
MAX_DATE = datetime.date.today()

engine = get_sql_connection()

date_for_titles = st.date_input('Date', value='today', min_value=MIN_DATE, max_value=MAX_DATE)
st.write(f"Top 100 words wordcloud from post titles created on {date_for_titles}")

df = get_posts_df_on_date(engine, date_for_titles)

fig, words = generate_wordcloud(df, 'title')

st.pyplot(fig)

post_selection = st.selectbox('Select a title', df['title'])
post_id = df.loc[df['title'] == post_selection, 'post_id'].values[0]

df = get_comments_df_from_post(engine, post_id)

fig, words = generate_wordcloud(df, 'body')

st.pyplot(fig)