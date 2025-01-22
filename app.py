import streamlit as st
import pandas as pd
from utils.wordcloud_utils import generate_wordcloud
from utils.db_utils import get_sql_connection
import datetime
from utils.app_utils import get_posts_df_on_date, get_comments_df_from_post

MIN_DATE = datetime.date(2025, 1, 21)
MAX_DATE = datetime.date.today()

engine = get_sql_connection()

st.title('Reddit Wordcloud Generator')

with st.sidebar:
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Start Date', value='today', min_value=MIN_DATE, max_value=MAX_DATE, key=1)
    with col2:
        end_date = st.date_input('End Date', value='today', min_value=start_date, max_value=MAX_DATE, key=2)

left, right = st.columns([3, 1])

with left:
    st.write(f"Top 100 words wordcloud from post titles created between {start_date} and {end_date}")
    posts_df = get_posts_df_on_date(engine, start_date, end_date)

    posts_fig, posts_words = generate_wordcloud(posts_df, 'title')

    st.pyplot(posts_fig)

    post_selection = st.selectbox('Select a post', posts_df['title'])
    post_id = posts_df.loc[posts_df['title'] == post_selection, 'post_id'].values[0]

    comments_df = get_comments_df_from_post(engine, post_id)

    comments_fig, comments_words = generate_wordcloud(comments_df, 'body')

    st.pyplot(comments_fig)
    
with right:
    top_10_words = list(posts_words.keys())[:10]
    df = pd.DataFrame(top_10_words, columns=['Word'])
    df['Rank'] = df.index + 1
    df = df[['Rank', 'Word']]
    df = df.set_index('Rank')
    st.dataframe(df)