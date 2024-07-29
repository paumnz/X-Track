import pandas as pd
import plotly.express as px
import networkx as nx
from sqlalchemy import create_engine

class Medias:
    def __init__(self, db_connection, pymongo_conn, campaigns, hashtags=None, k=15, writer=None):
        self._db_connection = db_connection
        self._pymongo_conn = pymongo_conn
        self._campaigns = campaigns
        self._hashtags = hashtags
        self._k = k
        self._writer = writer

    def get_top_domains(self):
        """
        Retrieve top domains mentioned in tweets for the specified campaigns and hashtags.
        """
        query = """
            SELECT url.domain, COUNT(tweet.id) AS num 
            FROM tweet
            JOIN url_tweet ON url_tweet.tweet_id = tweet.id
            JOIN url ON url_tweet.url_id = url.id
            JOIN user ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            AND url.domain NOT IN ('youtube.com','twitter.com','ift.tt','fb.me','ctt.ec','bit.ly','youtu.be',
                                   'www.youtube.com','t.me','goo.gl','t.co','buff.ly','www.facebook.com','facebook.com',
                                   'support.twitter.com','vk.ru','vk.cc','vk.com','ow.ly','instagram.com','wp.me',
                                   'www.pscp.tv','www.instagram.com','www.fiverr.com','patreon.com','rplr.co','open.spotify.com')
            GROUP BY url.domain 
            ORDER BY num DESC 
            LIMIT %(limit)s
        """

        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None,
            'limit': self._k
        }

        medias_mentioned = pd.read_sql(query, con=self._db_connection, params=params)
        medias_mentioned.to_excel(self._writer, sheet_name='top_domains', index=False, header=True)

        return medias_mentioned

    def get_top_headlines(self):
        """
        Retrieve top headlines mentioned in tweets for the specified campaigns and hashtags.
        """
        query = """
            SELECT url.title, COUNT(tweet.id) AS num 
            FROM tweet
            JOIN url_tweet ON url_tweet.tweet_id = tweet.id
            JOIN url ON url_tweet.url_id = url.id
            JOIN user ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            AND url.title != ''
            AND url.domain NOT IN ('youtube.com','twitter.com','ift.tt','fb.me','ctt.ec','bit.ly','youtu.be',
                                   'www.youtube.com','t.me','goo.gl','t.co','buff.ly','www.facebook.com','facebook.com',
                                   'support.twitter.com','vk.ru','vk.cc','vk.com','ow.ly','instagram.com','wp.me',
                                   'www.pscp.tv','www.instagram.com','www.fiverr.com','patreon.com','rplr.co','open.spotify.com')
            GROUP BY url.title 
            ORDER BY num DESC 
            LIMIT %(limit)s
        """

        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None,
            'limit': self._k
        }

        medias_mentioned = pd.read_sql(query, con=self._db_connection, params=params)
        medias_mentioned.to_excel(self._writer, sheet_name='top_headlines', index=False, header=True)

        return medias_mentioned

