import tweepy
import twint
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
import re
import nest_asyncio
nest_asyncio.apply()

from Config.settings import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET



# from Config.settings import MONGO_URL, SLACK_WEBHOOK

MONGO_URL = "localhost"
client = MongoClient(MONGO_URL)

db = client.twitter_bot
collection = db.twitter_thread






# Authenticate to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


api = tweepy.API(auth, wait_on_rate_limit=True)


