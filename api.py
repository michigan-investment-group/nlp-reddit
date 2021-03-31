"""api.py

Reddit API for Reddit Crawling

Authors: Nihar Joshi, Shant Amerkanian, Andrew Ferruolo, 
James Doredla, Julian Tarazi, Benjamin Oostendorp, Stephen Hajjar, Brandon Fan

"""

import os
import time
from flask import Flask, request, make_response, jsonify
from crawler import RedditCrawler
import logging
app = Flask(__name__)


reddit = RedditCrawler()

#configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/crawl', methods=['GET'])
def handle_reddit():
    logger.info("handle_reddit() called at time %s", time.now())
    reddit.crawl()
    response = make_response(jsonify({
        "task": "Reddit Crawling",
        "status": "Completed"
    }))
    logger.info("Response: %s", response)
    return response

@app.route('/crawl_ticker', methods=['GET'])
def handle_reddit_ticker(): 
    ticker = request.args.get('ticker')
    logger.info("handle_reddit_ticker() with argument {ticker} called at time %s", time.now())
    data = reddit.crawl(tickers=[ticker])
    response = make_response(jsonify(data))
    logger.info("Response: %s", response)
    return response

# ==================== DO NOT ALTER THIS ====================

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 6600))
    app.run(host='0.0.0.0', port=PORT)
