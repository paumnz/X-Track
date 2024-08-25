import argparse
import datetime
import time
import requests
import pymongo
from transformers import pipeline

class TwitterDataIngestion:
    def __init__(self, election, bearer_token, daily_tweet_limit, mongo_uri, db_name, collection_name, tweets_collection_name, users_collection_name):
        self.election = election
        self.bearer = bearer_token
        self.daily_tweet_limit = daily_tweet_limit
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.collection_tweets = self.db[tweets_collection_name]
        self.collection_users = self.db[users_collection_name]
        self.sentiment_analysis = pipeline("sentiment-analysis", model="sagorsarker/codeswitch-spaeng-sentiment-analysis-lince", tokenizer="sagorsarker/codeswitch-spaeng-sentiment-analysis-lince")
        self.hate_speech = pipeline("text-classification", model="Hate-speech-CNERG/dehatebert-mono-spanish", tokenizer="Hate-speech-CNERG/dehatebert-mono-spanish")
        self.ses = requests.Session()
        self.ses.headers["Authorization"] = f"Bearer {self.bearer}"
        self.ses.headers["User-Agent"] = "Your-User-Agent-Here" # Put your user-agent here.
    
    def get_sentiment(self, text):
        label_positive = 'LABEL_1'
        label_negative = 'LABEL_0'
        text_analysis = self.sentiment_analysis(text)

        result = {}
        for l in text_analysis:
            if l["label"] == label_positive:
                result["positive"] = l["score"]
                result["negative"] = 0.0
            elif l["label"] == label_negative:
                result["negative"] = l["score"]
                result["positive"] = 0.0

        return result

    def get_hate(self, text):
        try:
            result = self.hate_speech(text)
            res = {
                "hate": 0.0,
                "non_hate": 0.0
            }
            for val in result:
                if val["label"] == 'HATE':
                    res["hate"] = val["score"]
                if val["label"] == 'NON_HATE':
                    res["non_hate"] = val["score"]

            return res
        except Exception as e:
            print(str(e))
            return {
                "hate": None,
                "non_hate": None
            }

    def _parse_next_token(self, result):
        try:
            if "meta" in result and "next_token" in result["meta"]:
                next_token = result["meta"]["next_token"]
            else:
                next_token = False
            return next_token
        except Exception as e:
            print(result)
            print(str(e))
            return False

    def insert_tweets(self, rc, start_time, end_time, trending_topic):
        time.sleep(1)
        if rc:
            if "includes" in rc and "users" in rc["includes"]:
                for u in rc["includes"]["users"]:
                    self.collection_users.insert_one(u)

            for d in rc["data"]:
                d["start_time"] = str(start_time)
                d["end_time"] = str(end_time)
                d["trending_topic"] = trending_topic
                d["election"] = self.election

                try:
                    sentiment = self.get_sentiment(d["text"])
                except Exception as e:
                    print(str(e))
                    sentiment = {}

                try:
                    hate = self.get_hate(d["text"])
                except Exception as e:
                    print(str(e))
                    hate = {}

                d["sentiment"] = sentiment
                d["hate_speech"] = hate
                self.collection_tweets.insert_one(d)

    def get_tweets(self, url, params):
        try:
            rc = self.ses.get(url=url, params=params, timeout=5)
            rc = rc.json()
            if rc["meta"]["result_count"] == 0:
                return {"data": []}
            return rc
        except Exception as e:
            print(str(e))
            time.sleep(300)
            return self.get_tweets(url, params)

    def fetch_and_store_tweets(self):
        documents = list(self.collection.find(no_cursor_timeout=True, batch_size=5))

        for row in documents:
            try:
                hours = int(row["hour"])
                hours_added = datetime.timedelta(hours=hours)
                hours_added_end = datetime.timedelta(hours=hours + 1)

                trend_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
                trend_date_hours = trend_date + hours_added
                trend_date_hours_end = trend_date + hours_added_end

                trend_date_hours = trend_date_hours.isoformat() + ".00Z"
                trend_date_hours_end = trend_date_hours_end.isoformat() + ".00Z"
                params = {
                    "tweet.fields": "attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,public_metrics,possibly_sensitive,referenced_tweets,reply_settings,source,text,withheld",
                    "start_time": trend_date_hours,
                    "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld",
                    "expansions": "entities.mentions.username",
                    "end_time": trend_date_hours_end,
                    "query": row["trending_topic"].encode('utf-8'),
                    "max_results": 100
                }
                url = "https://api.twitter.com/2/tweets/search/all"
                rc = self.get_tweets(url, params)

                self.insert_tweets(rc, trend_date_hours, trend_date_hours_end, row["trending_topic"])
                time.sleep(1)

                next_token = self._parse_next_token(rc)
                try:
                    num_tweets = len(rc["data"])
                except Exception as e:
                    print(str(e))
                    num_tweets = 0

                while rc and next_token and num_tweets < self.daily_tweet_limit:
                    try:
                        params["next_token"] = next_token
                        rc = self.get_tweets(url, params)
                        self.insert_tweets(rc, trend_date_hours, trend_date_hours_end, row["trending_topic"])
                        next_token = self._parse_next_token(rc)
                        if rc:
                            num_tweets += len(rc["data"])
                        else:
                            time.sleep(2)
                    except Exception as e:
                        time.sleep(5)
                        print(str(e))
            except Exception as e:
                print(str(e))
