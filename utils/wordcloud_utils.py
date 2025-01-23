import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt

nltk.download('stopwords')
nltk.download('punkt_tab')

def clean_text(text):
    stop_words = set(stopwords.words("english"))
    
    # Remove URLs and special characters
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[^\w\s]", "", text)
    
    # Convert to lowercase and remove stopwords
    words = word_tokenize(text.lower())
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

def generate_wordcloud(df, column, no_of_words=100, figure=True):
    text = ' '.join(text for text in df[column].str.strip())
    final_text = clean_text(text)
    wordcloud = WordCloud(max_words=no_of_words, width=600, height=200, background_color='white').generate(final_text)
    wordcloud_words = wordcloud.words_
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    return (fig, wordcloud_words) if figure else wordcloud_words