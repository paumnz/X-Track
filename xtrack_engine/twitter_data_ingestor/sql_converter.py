import argparse
import re
import mysql.connector
import pymongo
from urllib.parse import urlparse

class DataMigration:
    def __init__(self, mongo_uri, mongo_db, mongo_collection, sql_config):
        self.mongo_client = pymongo.MongoClient(mongo_uri)
        self.topics_db = self.mongo_client[mongo_db]
        self.tweets_collection = self.topics_db[mongo_collection]
        self.sql_db = mysql.connector.connect(**sql_config)
        self.sql_cursor = self.sql_db.cursor(buffered=True)


    def extract_date(self, created_at):
        created_at = "X" + created_at
        date = re.search(r'X(.*?)T', created_at).group(1)
        date_time = re.search(r'T(.*?)\.', created_at).group(1)
        return date + " " + date_time

    def insert_user(self, user_id, username=None):
        sql = "SELECT id FROM user WHERE user_id = %s"
        val = (user_id,)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return res[0]
        else:
            sql = "INSERT INTO user (username, user_id) VALUES (%s, %s);"
            val = (username, user_id)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def insert_mention(self, tweet_id, mention_id):
        sql = "INSERT INTO mention (tweet_id, user_id) VALUES (%s, %s);"
        val = (tweet_id, mention_id)
        self.sql_cursor.execute(sql, val)
        return self.sql_cursor.lastrowid

    def insert_hashtag(self, hashtag):
        sql = "SELECT id FROM hashtag WHERE hashtag = %s"
        val = (hashtag,)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return res[0]
        else:
            sql = "INSERT INTO hashtag (hashtag) VALUES (%s);"
            val = (hashtag,)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def insert_hashtag_tweet(self, tweet_id, hashtag_id):
        sql = "INSERT INTO hashtagt_tweet (tweet_id, hashtag_id) VALUES (%s, %s);"
        val = (tweet_id, hashtag_id)
        self.sql_cursor.execute(sql, val)
        return self.sql_cursor.lastrowid

    def insert_url(self, url):
        url_link = url["url"]
        expanded_url = url["expanded_url"]
        domain = urlparse(expanded_url).netloc
        title = url.get("title", None)
        description = url.get("description", None)
        unwound_url = url.get("unwound_url", None)

        sql = "SELECT id FROM url WHERE url = %s"
        val = (url_link,)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return res[0]
        else:
            sql = """INSERT INTO url (url, expanded_url, domain, title, description, unwound_url) 
                     VALUES (%s, %s, %s, %s, %s, %s);"""
            val = (url_link, expanded_url, domain, title, description, unwound_url)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def insert_url_tweet(self, tweet_id, url_id):
        sql = "INSERT INTO url_tweet (tweet_id, url_id) VALUES (%s, %s);"
        val = (tweet_id, url_id)
        self.sql_cursor.execute(sql, val)
        return self.sql_cursor.lastrowid

    def insert_mentions(self, tweet, tweet_id):
        if "entities" in tweet and "mentions" in tweet["entities"]:
            for mention in tweet["entities"]["mentions"]:
                user_id = self.insert_user(user_id=mention["id"], username=mention["username"])
                self.insert_mention(tweet_id, user_id)

    def insert_hashtags(self, tweet, tweet_id):
        if "entities" in tweet and "hashtags" in tweet["entities"]:
            for hashtag in tweet["entities"]["hashtags"]:
                hashtag_id = self.insert_hashtag(hashtag["tag"])
                self.insert_hashtag_tweet(tweet_id, hashtag_id)

    def insert_urls(self, tweet, tweet_id):
        if "entities" in tweet and "urls" in tweet["entities"]:
            for url in tweet["entities"]["urls"]:
                url_id = self.insert_url(url)
                self.insert_url_tweet(tweet_id, url_id)

    def insert_reply(self, tweet, tweet_id):
        in_reply_to_user_id = tweet.get("in_reply_to_user_id", None)
        if in_reply_to_user_id:
            sql = "INSERT INTO reply (tweet_id, reply_to) VALUES (%s, %s);"
            val = (tweet_id, in_reply_to_user_id)
            self.sql_cursor.execute(sql, val)
        else:
            if "referenced_tweets" in tweet:
                for referenced in tweet["referenced_tweets"]:
                    if referenced["type"] == "replied_to":
                        sql = "INSERT INTO reply (tweet_id, reply_to) VALUES (%s, %s);"
                        val = (tweet_id, referenced["id"])
                        self.sql_cursor.execute(sql, val)
                    elif referenced["type"] == "retweeted":
                        sql = "INSERT INTO retweet (tweet_id, retweeted) VALUES (%s, %s);"
                        val = (tweet_id, referenced["id"])
                        self.sql_cursor.execute(sql, val)
                    elif referenced["type"] == "quoted":
                        sql = "INSERT INTO quoted (tweet_id, quoted) VALUES (%s, %s);"
                        val = (tweet_id, referenced["id"])
                        self.sql_cursor.execute(sql, val)

    def insert_metrics(self, tweet, tweet_id):
        sql = """INSERT INTO tweet_metrics (tweet_id, retweet_count, reply_count, like_count, quote_count) 
                 VALUES (%s, %s, %s, %s, %s);"""
        val = (tweet_id, tweet["public_metrics"]["retweet_count"], tweet["public_metrics"]["reply_count"], 
               tweet["public_metrics"]["like_count"], tweet["public_metrics"]["quote_count"])
        self.sql_cursor.execute(sql, val)
        return self.sql_cursor.lastrowid

    def insert_annotation(self, annotation):
        annotation_id = annotation["entity"]["id"]
        name = annotation["entity"].get("name", None)
        description = annotation["domain"].get("description", None)
        category = annotation["domain"].get("name", None)

        sql = "SELECT id FROM domain WHERE name = %s"
        val = (name,)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return res[0]
        else:
            sql = """INSERT INTO domain (annotation_id, name, description, category) 
                     VALUES (%s, %s, %s, %s);"""
            val = (annotation_id, name, description, category)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def insert_annotation_prediction(self, annotation):
        probability = round(float(annotation["probability"]), 4)
        annotation_type = annotation["type"]
        normalized_text = annotation["normalized_text"]

        sql = "SELECT id FROM annotation WHERE normalized_text = %s"
        val = (normalized_text,)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return res[0]
        else:
            sql = """INSERT INTO annotation (type, probability, normalized_text) 
                     VALUES (%s, %s, %s);"""
            val = (annotation_type, probability, normalized_text)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def insert_annotations(self, tweet, tweet_id):
        if "context_annotations" in tweet:
            for annotation in tweet["context_annotations"]:
                domain_id = self.insert_annotation(annotation)
                sql = "INSERT INTO annotation_tweet (tweet_id, domain_id) VALUES (%s, %s);"
                val = (tweet_id, domain_id)
                self.sql_cursor.execute(sql, val)

        if "entities" in tweet and "annotations" in tweet["entities"]:
            for annotation in tweet["entities"]["annotations"]:
                annotation_id = self.insert_annotation_prediction(annotation)
                sql = "INSERT INTO annotation_prediction_tweet (tweet_id, annotation_id) VALUES (%s, %s);"
                val = (tweet_id, annotation_id)
                self.sql_cursor.execute(sql, val)

    def insert_tweet(self, tweet, author_id):
        sql = "SELECT id FROM tweet WHERE tweet_id = %s"
        val = (tweet["id"],)
        self.sql_cursor.execute(sql, val)
        res = self.sql_cursor.fetchone()

        if res:
            return False
        else:
            tweet_id = tweet["id"]
            source = tweet["source"]
            reply_settings = tweet["reply_settings"]
            possibly_sensitive = tweet["possibly_sensitive"]
            created_at = self.extract_date(tweet["created_at"])
            lang = tweet["lang"]
            conversation_id = tweet["conversation_id"]
            text = tweet["text"]
            start_time = self.extract_date(tweet["start_time"])
            end_time = self.extract_date(tweet["end_time"])
            trending_topic = tweet.get("trending_topic", "undefined")
            campaign = tweet.get("election", "pol")

            psoe = self.mentions_psoe(tweet)
            pp = self.mentions_pp(tweet)
            vox = self.mentions_vox(tweet)
            liberal = self.mentions_liberal(tweet)
            conservative = self.mentions_conservative(tweet)
            podemos = self.mentions_podemos(tweet)
            communism = self.mentions_communism(tweet)
            gender = self.mentions_gender(tweet)
            cs = self.mentions_cs(tweet)
            independentism = self.mentions_independentism(tweet)
            spain = self.mentions_spain(tweet)

            in_reply_to_user_id = tweet.get("in_reply_to_user_id", None)

            sql = """INSERT INTO tweet (tweet_id, source, reply_settings, possibly_sensitive, author_id, created_at, lang, conversation_id, text, start_time, end_time, trending_topic, campaign, in_reply_to_user_id, mentions_psoe, mentions_pp, mentions_vox, mentions_liberal, mentions_conservative, mentions_podemos, mentions_communism, mentions_gender, mentions_cs, mentions_independentism, mentions_spain) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            val = (tweet_id, source, reply_settings, possibly_sensitive, author_id, created_at, lang, conversation_id, text, start_time, end_time, trending_topic, campaign, in_reply_to_user_id,
                   psoe, pp, vox, liberal, conservative, podemos, communism, gender, cs, independentism, spain)
            self.sql_cursor.execute(sql, val)
            return self.sql_cursor.lastrowid

    def mentions_psoe(self, tweet):
        strings_psoe = ["🌹", "/❤️", "#psoe", "votapsoe"]
        return any(s in tweet["text"].lower() for s in strings_psoe)

    def mentions_pp(self, tweet):
        strings_pp = ["💙", "#pp", "#yovotopp", "equippogana", "españaenserio"]
        return any(s in tweet["text"].lower() for s in strings_pp)

    def mentions_vox(self, tweet):
        terms_vox = ["💚", "🐸", "#vox"]
        return any(s in terms_vox for s in tweet["text"].lower())

    def mentions_liberal(self, tweet):
        terms_liberal = ["🇦🇩", "🇨🇭", "🐍", "💛", "#let"]
        return any(s in terms_liberal for s in tweet["text"].lower())

    def mentions_conservative(self, tweet):
        terms_conservative = ["🇵🇱", "🇭🇺", "✝️", "#spexit"]
        return any(s in terms_conservative for s in tweet["text"].lower())

    def mentions_podemos(self, tweet):
        terms_podemos = ["💜", "🔻", "#podemos", "#sisepuede"]
        return any(s in terms_podemos for s in tweet["text"].lower())

    def mentions_communism(self, tweet):
        terms_communism = ["🇨🇺", "☭", "🇨🇳"]
        return any(s in terms_communism for s in tweet["text"].lower())

    def mentions_gender(self, tweet):
        terms_gender = ["🏳️‍🌈", "♀️", "⚧️", "#lgbt"]
        return any(s in terms_gender for s in tweet["text"].lower())

    def mentions_cs(self, tweet):
        terms_cs = ["🧡", "#cs"]
        return any(s in terms_cs for s in tweet["text"].lower())

    def mentions_independentism(self, tweet):
        terms_indepe = ["🎗️", "#freetothom", "1oct", "freedomcatalonia", "🏴", "soccdr"]
        return any(s in terms_indepe for s in tweet["text"].lower())

    def mentions_spain(self, tweet):
        terms_spain = ["🇪🇸", "España"]
        return any(s in terms_spain for s in tweet["text"].lower())

    def process_tweets(self):
        tweets = self.tweets_collection.find(no_cursor_timeout=True, batch_size=50)
        for tweet in tweets:
            try:
                author_id = self.insert_user(tweet["author_id"])
                tweet_id = self.insert_tweet(tweet, author_id)

                if tweet_id:
                    self.insert_mentions(tweet, tweet_id)
                    self.insert_urls(tweet, tweet_id)
                    self.insert_hashtags(tweet, tweet_id)
                    self.insert_metrics(tweet, tweet_id)
                    self.insert_annotations(tweet, tweet_id)
                    self.insert_reply(tweet, tweet_id)
                    self.sql_db.commit()
            except Exception as e:
                print(f"Error processing tweet {tweet['id']}: {e}")
