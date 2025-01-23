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

st.header('/r/technology Hot Posts Analysis')

with st.sidebar:
    # Get the timeframe for analysis from the user
    st.header('Date Selection')
    st.write('Select a date range from which to analyse the hot /r/technology posts and comments')
    
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input('Start Date', value='today', min_value=MIN_DATE, max_value=MAX_DATE, key=1)
    with col2:
        end_date_max = min(datetime.date.today(), start_date + datetime.timedelta(days=7))
        end_date = st.date_input('End Date', value='today', min_value=start_date, max_value=end_date_max, key=2)

# Create the tabs for the different analysis sections
posts, comments, day_to_day = st.tabs(['Post Titles', 'Comments', 'Day to Day Comparison'])

with posts:
    # Get the posts for the selected date range
    posts_df = get_posts_df_on_date(engine, start_date, end_date)
    # Generate the wordcloud and top 10 words for the post titles
    posts_wordcloud, posts_words = generate_wordcloud(posts_df, 'title')
    st.subheader('Most Common Words in Post Titles')
    # Display the wordcloud and caption
    st.pyplot(posts_wordcloud, use_container_width=False)
    st.caption(f"Top 100 words in post titles created between {start_date} and {end_date}")
    
    left, right = st.columns(2)
    
    with left:
        st.subheader('Sentiment Analysis of Titles')
        st.caption('A breakdown of the sentiment of the hot posts titles')
        sentiment_fig = get_sentiment_pie_chart(posts_df, 'title')
        st.plotly_chart(sentiment_fig)

    with right:
        st.subheader('Top 10 Words in Post Titles')
        st.caption('The most common words seen in the post titles')
        df = get_top_10_words(posts_words)
        st.dataframe(df)
    
with comments:
    
    selection_string = 'Select a post to view the comments analysis. The posts are ordered by their score, with the highest score at the top'
    post_selection = st.selectbox(selection_string, posts_df['title'])
    
    post_id = posts_df.loc[posts_df['title'] == post_selection, 'post_id'].values[0]

    comments_df = get_comments_df_from_post(engine, post_id)

    comments_wordcloud, comments_words = generate_wordcloud(comments_df, 'body')

    st.pyplot(comments_wordcloud, use_container_width=False)
    st.caption(f"Top 100 words in the top 100 top level comments of the selected post: {post_selection}")
    left, right = st.columns(2)
    
    with left:
        st.subheader('Sentiment Analysis of Comments')
        st.caption('A breakdown of the sentiment of the top 100 comments')
        sentiment_fig = get_sentiment_pie_chart(comments_df, 'body')
        st.plotly_chart(sentiment_fig)
        
    with right:
        st.subheader('Top 10 words from comments')
        st.caption('The most common words seen in the top 100 comments')
        # Retrieve and display the top 10 words from the comments
        df = get_top_10_words(comments_words)
        st.dataframe(df)

with day_to_day:
    
    words, sentiment = st.tabs(['Trending Words', 'Sentiment Analysis'])
    
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
    
    with words:
        # Display the top 10 words dataframes
        st.subheader('Top 10 Words in Post Titles')
        st.dataframe(day_to_day_top_10_posts)
        st.subheader('Top 10 Words in Comments')
        st.dataframe(day_to_day_top_10_comments)
    with sentiment:
        # Display sentiment daily comparison charts
        # st.subheader('Sentiment Analysis of Posts and Comments')
        st.plotly_chart(get_sentiment_daily_comparison_chart(day_to_day_posts_sentiments, 'Sentiment Breakdown of Post Titles by Day'))
        st.plotly_chart(get_sentiment_daily_comparison_chart(day_to_day_comments_sentiments, 'Sentiment Breakdown of Comments by Day'))