from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import plotly.express as px

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

def get_sentiment(df, column):
    df['sentiment_compound'] = df[column].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['sentiment_label'] = df['sentiment_compound'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))
    return df

def get_sentiment_counts(df):
    sentiment_counts = df['sentiment_label'].value_counts()
    sentiment_counts = sentiment_counts.reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    return sentiment_counts

def get_sentiment_pie_chart(df, column):
    df = get_sentiment(df, column)
    sentiment_counts = get_sentiment_counts(df)
    custom_colours = {
        'Negative': 'lightcoral',
        'Neutral': 'lightgrey',
        'Positive': 'lightgreen'
    }
    fig = px.pie(sentiment_counts, names='Sentiment', values='Count', color='Sentiment', color_discrete_map=custom_colours)
    fig.update_layout(showlegend=False)
    return fig