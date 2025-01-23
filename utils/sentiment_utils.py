from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import plotly.express as px

nltk.download('vader_lexicon')

# Custom colours for the sentiment pie chart and comparison chart
CUSTOM_COLOURS = {
        'Negative': 'lightcoral',
        'Neutral': 'lightgrey',
        'Positive': 'lightgreen'
    }

def get_sentiment(df, column):
    # Get the sentiment of the text in the column
    # Initialise the SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    # Get the sentiment scores for each text in the column
    df['sentiment_compound'] = df[column].apply(lambda x: sia.polarity_scores(x)['compound'])
    # Get the sentiment label based on the compound score
    df['sentiment_label'] = df['sentiment_compound'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))
    return df

def get_sentiment_counts(df):
    # Get the count of each sentiment label
    sentiment_counts = df['sentiment_label'].value_counts()
    # Reset the index and rename the columns
    sentiment_counts = sentiment_counts.reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    # Sort the values in descending order, this ensures the dataframe is in the correct order for the charts
    sentiment_counts = sentiment_counts.sort_values('Sentiment', ascending=False)
    # Reset the index so when multiple dataframes are concatenated, the index is consistent
    sentiment_counts = sentiment_counts.reset_index(drop=True)
    return sentiment_counts

def get_sentiment_pie_chart(df, column):
    # Get the sentiment of the text in the column
    df = get_sentiment(df, column)
    # Get the count of each sentiment label
    sentiment_counts = get_sentiment_counts(df)
    # Create the pie chart
    fig = px.pie(sentiment_counts, names='Sentiment', values='Count', color='Sentiment', color_discrete_map=CUSTOM_COLOURS)
    fig.update_layout(showlegend=False)
    return fig

def get_sentiment_daily_comparison_chart(df, title_string):
    # Melt the dataframe to have the date as a column
    df = df.melt(id_vars='Sentiment', var_name='Date', value_name='Count')
    # Get the total count for each date
    df['Total'] = df.groupby('Date')['Count'].transform('sum')
    # Calculate the percentage of each sentiment for each date
    df['Percentage'] = df['Count'] / df['Total'] * 100
    # Create the bar chart
    fig = px.bar(df, x='Date', y='Percentage', color='Sentiment', title=title_string, color_discrete_map=CUSTOM_COLOURS)
    return fig
