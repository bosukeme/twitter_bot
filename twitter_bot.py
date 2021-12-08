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




search_day = datetime.now() - timedelta(60)
search_day_str = datetime.strftime(search_day, '%Y-%m-%d')

num_tweets = 1000
date = search_day_str


def twint_to_pandas(columns):
    return twint.output.panda.Tweets_df[columns]


def get_latest_tweets_from_handle(username, num_tweets, date):
    """
        This uses twint to get all the tweets made by the username/handle
    """
    c = twint.Config()
    c.Username = username
    c.Limit = num_tweets
    c.Pandas = True
    c.Since = date
    c.Hide_output = True

    twint.run.Search(c)
    
    try:
        tweet_df = twint_to_pandas(['id', 'conversation_id', 'date', 'tweet', 'language', 'hashtags', 
               'username', 'name', 'link', 'urls', 'photos', 'video',
               'thumbnail', 'retweet', 'nlikes', 'nreplies', 'nretweets', 'source', "reply_to"])
    except Exception as e:
        print(e)
        tweet_df = pd.DataFrame()
        
    return tweet_df

def cleanup_tweet(tweet, twitter_handle, num_reply=0):
    """
    This function takes in a tweet and then cleans it up by removing non alphanumericals etc
    """
    try:
        tweet_tokens = tweet.split()[num_reply:] # we ignore the first token which will always be the handle
        text_list = []
        for token in tweet_tokens:
            temp = ''.join([i for i in token if (i.isalpha() or (i in ['.',',', '..', '…', ':', ';', '?', '"', '-', '(', ')']) or i.isdigit())])        
            if '#' not in temp:
                if twitter_handle not in temp:
                    text_list.append(temp.strip())

        tweet_text = ' '.join(text_list)
        tweet_text = re.sub(r"http\S+", "", tweet_text)
        tweet_text = tweet_text.strip()
    except Exception as e:
        print(e)
    return tweet_text


def get_record_details(search_dict, collection, find_one=True):
    """
        This searches through mongodb for a single record
    """
    try:
        query = collection.find_one(search_dict) if find_one else collection.find(search_dict)
        return query
    except Exception as e:
        print(e)
        return None


def insert_records(collection, record):
    """
        This inserts a single record to mongo db
    """
    try:
        collection.insert_one(record)
    except Exception as e:
        print(e)

def save_to_mongo_db(data, collection):
    """
        This saves the record to mongo db
    """
    insert_records(collection, data)
    cur = collection.count_documents({})
    print(f"we have {cur} entries")


def process_tweets(item):    
    
    search_dict = {"tag_id": item['id']}
    search_query = get_record_details(search_dict, collection, find_one=True)
    
    if search_query == None:
    
        try:
            print("as reply")
            ## tweets that were as replies
            if item['in_reply_to_status_id']:

                handle = item['in_reply_to_screen_name']
                thread_id = str(item['in_reply_to_status_id'])
                print(thread_id)
                print(handle)
                
                user_dict = { 
                    
                    "tag_id": item['id'],
                    "name": item['user']['name'],
                    "username": item['user']['screen_name'],
                    "bio": item['user']['description'],
                    
                }
                print(user_dict)

                
                dff = get_latest_tweets_from_handle(handle, num_tweets, date)
                conversation_id = dff[dff['id'] == thread_id]['conversation_id'].tolist()[0]
                df_thread = dff[dff['conversation_id'] == conversation_id]
                df_thread['len_reply'] = df_thread['reply_to'].apply(lambda row: len(row))
                df_thread = df_thread[df_thread['len_reply']== 0]
                df_thread = df_thread.sort_index(axis = 0, ascending=False)
                df_thread = df_thread.reset_index(drop=True)
                df_thread = df_thread[['id', 'conversation_id', 'tweet', 'username', 'name', 'link', 'photos']]
                df_thread['tweet'] = df_thread['tweet'].apply(lambda row: cleanup_tweet(row, handle))
                df_thread['tweet'] = df_thread['tweet'].apply(lambda row: row.split(':') if ":" in row else [row])
                df_thread_dict = df_thread.to_dict("records")
                
                thread_dict = {
                    
                        "thread_dict": df_thread_dict
                }

                data = {**user_dict, **thread_dict}
                save_to_mongo_db(data, collection)
                print(data)
                
        except Exception as e:
            print(e)

        print("---------------------------------------------------------")
        try:
            print("as quote")
            ## tweets that were as quotes
            if item['quoted_status_id']:
                handle = item['quoted_status']['user']['screen_name']
                thread_id = str(item['quoted_status_id'])
                print(handle)
                print(thread_id)
                
                
                user_dict = { 
                    
                    "tag_id": item['id'],
                    "name": item['user']['name'],
                    "username": item['user']['screen_name'],
                    "bio": item['user']['description'],
                    
                }
                print(user_dict)
                
                
                dff = get_latest_tweets_from_handle(handle, num_tweets, date)
                conversation_id = dff[dff['id'] == thread_id]['conversation_id'].tolist()[0]
                df_thread = dff[dff['conversation_id'] == conversation_id]
                df_thread['len_reply'] = df_thread['reply_to'].apply(lambda row: len(row))
                df_thread = df_thread[df_thread['len_reply']== 0]
                df_thread = df_thread.sort_index(axis = 0, ascending=False)
                df_thread = df_thread.reset_index(drop=True)
                df_thread = df_thread[['id', 'conversation_id', 'tweet', 'username', 'name', 'link', 'photos']]
                df_thread['tweet'] = df_thread['tweet'].apply(lambda row: cleanup_tweet(row, handle))
                df_thread['tweet'] = df_thread['tweet'].apply(lambda row: row.split(':') if ":" in row else [row])
                df_thread_dict = df_thread.to_dict("records")

                thread_dict = {
                    
                        "thread_dict": df_thread_dict
                }

                data = {**user_dict, **thread_dict}
                save_to_mongo_db(data, collection)

                print(data)


        except Exception as e:
            print(e)

def start_twitter_bot():
    for item in tweepy.Cursor(api.mentions_timeline).items(100):

        item = item._json

        process_tweets(item)



start_twitter_bot()