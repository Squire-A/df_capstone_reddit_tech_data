from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import plotly.express as px

nltk.download('vader_lexicon')

CUSTOM_COLOURS = {
        'Negative': 'lightcoral',
        'Neutral': 'lightgrey',
        'Positive': 'lightgreen'
    }

def get_sentiment(df, column):
    sia = SentimentIntensityAnalyzer()
    df['sentiment_compound'] = df[column].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['sentiment_label'] = df['sentiment_compound'].apply(lambda x: 'Positive' if x >= 0.05 else ('Negative' if x <= -0.05 else 'Neutral'))
    return df

def get_sentiment_counts(df):
    sentiment_counts = df['sentiment_label'].value_counts()
    sentiment_counts = sentiment_counts.reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    sentiment_counts = sentiment_counts.sort_values('Sentiment', ascending=False)
    sentiment_counts = sentiment_counts.reset_index(drop=True)
    return sentiment_counts

def get_sentiment_pie_chart(df, column):
    df = get_sentiment(df, column)
    sentiment_counts = get_sentiment_counts(df)
    
    fig = px.pie(sentiment_counts, names='Sentiment', values='Count', color='Sentiment', color_discrete_map=CUSTOM_COLOURS)
    fig.update_layout(showlegend=False)
    return fig

def get_sentiment_daily_comparison_chart(df, title_string):
    df = df.melt(id_vars='Sentiment', var_name='Date', value_name='Count')
    df['Total'] = df.groupby('Date')['Count'].transform('sum')
    df['Percentage'] = df['Count'] / df['Total'] * 100
    fig = px.bar(df, x='Date', y='Percentage', color='Sentiment', title=title_string, color_discrete_map=CUSTOM_COLOURS)
    return fig
