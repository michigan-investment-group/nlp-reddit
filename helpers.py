# Helper functions
import urllib
import json
from requests import request

FINANCE_URL = 'https://financialmodelingprep.com/api/v3/'

def make_url(base_url , *res, **params):
    url = base_url
    for r in res:
        url = '{}/{}'.format(url, r)
    if params:
        url = '{}?{}'.format(url, urllib.parse.urlencode(params))
    return url

#returns a list of tickers
def get_tickers(exchanges, API_KEY):
    url = make_url(FINANCE_URL, 'available-traded/list', apikey=API_KEY)
    data = request('GET', url).json()
    tickers = []
    for res in data:
        try:
            if res['exchange'] in exchanges:
                tickers.append(res['symbol'])
        except:
            continue
    return tickers

# Upload data to Firebase
def upload(client, ticker, posts):
    def chunks(seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out
    
    reddit_chunks = chunks(posts, 500)
    for chunk in reddit_chunks:
        batch = client.batch()
        for post in chunk:
            path = 'stocks/{}/news/{}'.format(ticker, post['id'])
            ref = client.document(path)
            batch.set(ref, post)
        batch.commit()
    return

    
    