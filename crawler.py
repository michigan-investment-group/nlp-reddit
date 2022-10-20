# Script to scrape data off Reddit
import praw
import json
import helpers as helpers
from uuid import uuid4

from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage
from nltk.sentiment.vader import SentimentIntensityAnalyzer


keys = {
    'hf_key': 'api_QBEvzoutRNsLTridfiEvmDwHBHtnMwDOHk',
    'finance_key': 'f913bbd3dad0c411c864c0d960a711e7'
}

cred = credentials.Certificate('./keys.json')

firebase_app = firebase_admin.initialize_app(cred, name='reddit')
client = firestore.client(firebase_app)
storage = storage.client(firebase_app)

CLIENT_ID = keys['reddit']['client_id']
CLIENT_SECRET = keys['reddit']['client_secret']
USER_AGENT = keys['reddit']['user_agent']

SUB_REDDITS = ['stocks', 'wallstreetbets', 'stockmarket']
HOT_POST_COUNT = 250

class RedditCrawler:
    def __init__(self):
        self.sid = SentimentIntensityAnalyzer()
        self.reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    
    def _calculate_sentiment(self, text):
        text_scores = self.sid.polarity_scores(text)
        return text_scores['compound'], {
            'positive': text_scores['pos'],
            'neutral': text_scores['neu'],
            'negative': text_scores['neg']
        }

    def _upload_data(self, data):
        for stock in data:
            helpers.upload(client, stock, data[stock])
        return data

    def crawl(self, tickers=None):
        print("Scraping data from Reddit")
        if tickers is not None:
            stocks = tickers
        else:
            exchanges = ['New York Stock Exchange', 'Nasdaq Global Select']
            stocks = helpers.get_tickers(exchanges, keys['finance_key'])
        subreddit = '+'.join(SUB_REDDITS)
        target_subreddit = self.reddit.subreddit(subreddit)
        hot_posts = target_subreddit.hot(limit=HOT_POST_COUNT)

        results = {}

        for post in hot_posts:
            title = post.title 
            text = post.selftext
            time = post.created_utc
            url = post.url
            post_id = post.id
            title_compound, title_scores = self._calculate_sentiment(title)
            text_compound, text_scores = self._calculate_sentiment(text)

            sentiment = (title_compound + text_compound) / 2
            
            for stock in stocks:
                if '$' + stock in text:
                    reddit_post_obj = {
                        'ticker': stock,
                        'timestamp': time,
                        'date_crawled': int(time.time()),
                        'image': '',
                        'id': post_id,
                        'title': title,
                        'text': text,
                        'type': 'reddit',
                        'site': 'reddit.com',
                        'sentiment': sentiment,
                        'title_sentiment': title_scores,
                        'text_sentiment': text_scores,
                        'url': url,
                    }
                    if stock not in results:
                        results[stock] = [reddit_post_obj]
                    else:
                        results[stock].append(reddit_post_obj)
        
        file_path = "reddit-" + uuid4() + ".json"
        with open(file_path, "w") as f:
            json.dump(f, results)
        
        bucket = storage.bucket() # storage bucket
        blob = bucket.blob(file_path)
        return blob.upload_from_filename(file_path)