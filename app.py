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
        # Get the end date and set the max value to 7 days from the start date or today's date, whichever is earlier
        end_date_max = min(datetime.date.today(), start_date + datetime.timedelta(days=7))
        end_date = st.date_input('End Date', value='today', min_value=start_date, max_value='today', key=2)
        
    st.markdown('---')
    st.markdown('''
                ## About
                This app analyses the hot posts from the /r/technology subreddit.
                The data is collected from the Reddit API and stored in a postgreSQL database.
                The extraction script can be seen in the [github repository](https://github.com/Squire-A/df_capstone_reddit_tech_data).
                If you enter a date range, the database is queried and analysis performed on all the posts and comments in that date range on the database. 
                At this time the earliest data available is from 21st January 2025 and the maximum timeframe is 7 days. The extraction script is usually ran every 2 hours and checks the top 10 hot posts and 100 comments on each post from the /r/technology subreddit.
                
                __Please be aware that the words presented are not censored and may contain offensive language.__
                
                If you'd like to connect with me, please reach out on [LinkedIn](https://www.linkedin.com/in/anthony-squire-54508aa0/)!
                I'm always open to feedback and suggestions and I'm very eager to learn.
                
                Thanks for checking out the app!
                
                Anthony Squire
            ''')

# Create the tabs for the different analysis sections
posts, comments, day_to_day = st.tabs(['Post Titles', 'Comments', 'Day to Day Comparison'])
# Get the posts for the selected date range
posts_df = get_posts_df_on_date(engine, start_date, end_date)

# Check if there are any posts before conducting analysis
if not posts_df.empty:
    
    with posts:
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
            # Retrieve and display the sentiment analysis of the posts
            sentiment_fig = get_sentiment_pie_chart(posts_df, 'title')
            st.plotly_chart(sentiment_fig)

        with right:
            st.subheader('Top 10 Words in Post Titles')
            st.caption('The most common words seen in the post titles')
            # Retrieve and display the top 10 words from the posts
            df = get_top_10_words(posts_words)
            st.dataframe(df)

        
    with comments:
        
        selection_string = 'Select a post to view the comments analysis. The posts are ordered by their score, with the highest score at the top'
        post_selection = st.selectbox(selection_string, posts_df['title'])
        # Get the post_id for the selected post
        post_id = posts_df.loc[posts_df['title'] == post_selection, 'post_id'].values[0]
        # Get the comments for the selected post
        comments_df = get_comments_df_from_post(engine, post_id)
        # Generate the wordcloud and top 10 words for the comments
        comments_wordcloud, comments_words = generate_wordcloud(comments_df, 'body')

        st.pyplot(comments_wordcloud, use_container_width=False)
        st.caption(f"Top 100 words in the top 100 top level comments of the selected post: {post_selection}")
        left, right = st.columns(2)
        
        with left:
            st.subheader('Sentiment Analysis of Comments')
            st.caption('A breakdown of the sentiment of the top 100 comments')
            # Retrieve and display the sentiment analysis of the comments
            sentiment_fig = get_sentiment_pie_chart(comments_df, 'body')
            st.plotly_chart(sentiment_fig)
            
        with right:
            st.subheader('Top 10 words from comments')
            st.caption('The most common words seen in the top 100 comments')
            # Retrieve and display the top 10 words from the comments
            df = get_top_10_words(comments_words)
            st.dataframe(df)

    # Initialise variable to determine if any date has no data
    blank_day = False

    with day_to_day:
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
            
            if not day_posts.empty:
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
            else:
                # Set blank_day to True as there is at lest one day with no post data
                blank_day = True
                # If there are no posts for the current date place None in the dataframes so that the day still appears in the visualisations
                day_to_day_top_10_posts[date] = None
                day_to_day_top_10_comments[date] = None
                day_to_day_posts_sentiments[date] = None
                day_to_day_comments_sentiments[date] = None
                
        if blank_day:
            st.warning('At least one date in the selected range has no hot posts')
            
        words, sentiment = st.tabs(['Trending Words', 'Sentiment Analysis'])
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

else:
    # Present an error message when there is no data to display
    st.error('There are not yet any hot posts in the selected date range')