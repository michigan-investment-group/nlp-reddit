from flask import Flask, request, make_response, jsonify
from crawler import RedditCrawler
app = Flask(__name__)


reddit = RedditCrawler()

reddit.crawl()