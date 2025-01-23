import streamlit as st
import pandas as pd
from utils.wordcloud_utils import generate_wordcloud
from utils.db_utils import get_sql_connection
import datetime
from utils.app_utils import get_posts_df_on_date, get_comments_df_from_post, get_top_10_words, append_day
from utils.sentiment_utils import get_sentiment_pie_chart, get_sentiment, get_sentiment_counts, get_sentiment_daily_comparison_chart

st.set_page_config(page_title='/r/technology Reddit Analysis', layout="wide")

MIN_DATE = datetime.date(2025, 1, 21)
MAX_DATE = datetime.date.today()

engine = get_sql_connection()

st.header('/r/technology Reddit Analysis')

with st.sidebar:
    
    st.header('Date Selection')
    st.write('Select a date range from which to analyse the /r/technology posts')
    
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Start Date', value='today', min_value=MIN_DATE, max_value=MAX_DATE, key=1)
    with col2:
        end_date_max = min(datetime.date.today(), start_date + datetime.timedelta(days=7))
        end_date = st.date_input('End Date', value='today', min_value=start_date, max_value=end_date_max, key=2)

with st.container():
    
    posts, comments, day_to_day = st.tabs(['Post Titles', 'Comments', 'Day to Day Comparison'])
    
    with posts:
        
        posts_df = get_posts_df_on_date(engine, start_date, end_date)
        posts_wordcloud, posts_words = generate_wordcloud(posts_df, 'title')
        st.subheader('Most Common Words in Post Titles')
        st.pyplot(posts_wordcloud, use_container_width=False)
        st.caption(f"Top 100 words wordcloud from post titles created between {start_date} and {end_date}")
        
        left, right = st.columns(2)
        
        with left:
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
            
    with day_to_day:
        st.write('Day to Day Comparison')
        
        # Get all dates in the chosen date range
        date_range = pd.date_range(start_date, end_date)
        
         # Initialise the dataframes for the top 10 words and sentiment analysis
        day_to_day_top_10 = pd.DataFrame({'Rank': range(1, 11)})
        day_to_day_posts_sentiments = pd.DataFrame({'Sentiment': ['Positive', 'Neutral', 'Negative']})
        day_to_day_comments_sentiments = pd.DataFrame({'Sentiment': ['Positive', 'Neutral', 'Negative']})
        day_to_day_top_10_posts = day_to_day_top_10.set_index('Rank')
        day_to_day_top_10_comments = day_to_day_top_10.set_index('Rank')
        
        for date in date_range:
            date = date.date()
            # Get the posts and comments for the day
            day_posts = get_posts_df_on_date(engine, date, date)
            day_comments = get_posts_df_on_date(engine, date, date, comments=True)
            
            # Append the top 10 words to the dataframe
            day_to_day_top_10_posts[date] = append_day(date, engine)
            day_to_day_top_10_comments[date] = append_day(date, engine, comments=True)
            
            # Sentiment analysis of posts and comments
            day_post_sentiments = get_sentiment(day_posts, 'title')
            day_comment_sentiments = get_sentiment(day_comments, 'body')
            
            # Get the sentiment counts
            day_post_sentiment_counts = get_sentiment_counts(day_post_sentiments)
            day_comment_sentiment_counts = get_sentiment_counts(day_comment_sentiments)
            
            # Add the sentiment counts to the dataframes
            day_to_day_posts_sentiments[date] = day_post_sentiment_counts['Count']
            day_to_day_comments_sentiments[date] = day_comment_sentiment_counts['Count']
            
        # Display the top 10 words dataframes
        st.dataframe(day_to_day_top_10_posts)
        st.dataframe(day_to_day_top_10_comments)
        
        # Display sentiment daily comparison charts
        st.plotly_chart(get_sentiment_daily_comparison_chart(day_to_day_posts_sentiments, 'Sentiment of Posts'))
        st.plotly_chart(get_sentiment_daily_comparison_chart(day_to_day_comments_sentiments, 'Sentiment of Comments'))