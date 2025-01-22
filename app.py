import streamlit as st
import pandas as pd
from utils.wordcloud_utils import generate_wordcloud
from utils.db_utils import get_sql_connection
import datetime
from utils.app_utils import get_posts_df_on_date, get_comments_df_from_post, get_top_10_words
from utils.sentiment_utils import get_sentiment_pie_chart

st.set_page_config(page_title='/r/technology Reddit Analysis', layout="wide")

MIN_DATE = datetime.date(2025, 1, 21)
MAX_DATE = datetime.date.today()

engine = get_sql_connection()

st.header('/r/technology Reddit Analysis')

with st.sidebar:
    
    st.header('Date Selection')
    st.write('Select a date range from which to analyse the Reddit posts')
    
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Start Date', value='today', min_value=MIN_DATE, max_value=MAX_DATE, key=1)
    with col2:
        end_date = st.date_input('End Date', value='today', min_value=start_date, max_value=MAX_DATE, key=2)

with st.container():
    
    posts, comments = st.tabs(['Post Titles', 'Comments'])
    
    with posts:
        left, middle, right = st.columns([2, 1, 1])

        with left:
            posts_df = get_posts_df_on_date(engine, start_date, end_date)
            posts_wordcloud, posts_words = generate_wordcloud(posts_df, 'title')
            st.subheader('Most Common Words in Post Titles')
            st.pyplot(posts_wordcloud)
            st.caption(f"Top 100 words wordcloud from post titles created between {start_date} and {end_date}")
            
        with middle:
            st.subheader('Sentiment Analysis of Titles')
            sentiment_fig = get_sentiment_pie_chart(posts_df, 'title')
            st.plotly_chart(sentiment_fig)

        with right:
            st.subheader('Top 10 Words in Post Titles')
            df = get_top_10_words(posts_words)
            st.dataframe(df)
        
    with comments:
        
        post_selection = st.selectbox('Select a post', posts_df['title'])
        
        left, middle, right = st.columns([2, 1, 1])
        
        with left:
            
            post_id = posts_df.loc[posts_df['title'] == post_selection, 'post_id'].values[0]

            comments_df = get_comments_df_from_post(engine, post_id)

            comments_wordcloud, comments_words = generate_wordcloud(comments_df, 'body')

            st.pyplot(comments_wordcloud)
            
        with middle:
            st.subheader('Sentiment Analysis')
            sentiment_fig = get_sentiment_pie_chart(comments_df, 'body')
            st.plotly_chart(sentiment_fig)
            
        with right:
            st.subheader('Top 10 words from comments')
            df = get_top_10_words(comments_words)
            st.dataframe(df)