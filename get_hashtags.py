import operator
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from scipy import stats
import collections
import networkx as nx
import pymongo

class Hashtags:
    def __init__(self, db_connection, pymongo_conn, campaigns, k, writer):
        self._db_connection = db_connection
        self._pymongo_conn = pymongo_conn
        self._campaigns = campaigns
        self._k = k
        self._writer = writer

    def get_top_hashtags(self):
        """Get top hashtags by number of tweets."""
        query = """
        SELECT hashtag.hashtag, COUNT(tweet.id) AS num 
        FROM tweet 
        JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id 
        JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id 
        WHERE tweet.campaign IN %(campaigns)s
        GROUP BY hashtag.hashtag 
        ORDER BY num DESC 
        LIMIT %(limit)s;
        """
        params = {'campaigns': tuple(self._campaigns), 'limit': self._k}
        medias_mentioned = pd.read_sql(query, con=self._db_connection, params=params)
        medias_mentioned = medias_mentioned.sort_values(by=["num"], ascending=False)
        medias_mentioned.to_excel(self._writer, sheet_name='top_hashtags', index=False, header=True)

        self._create_bar_chart(medias_mentioned, 'hashtag', 'num', "Hashtag", "Num. Tweets", "Top hashtags in the conversation", "top_hashtags.png")
        
        return medias_mentioned

    def get_top_hashtags_hate(self):
        """Get top hashtags related to negative sentiment."""
        query = """
        SELECT hashtag.hashtag, COUNT(tweet.id) AS num, AVG(sentiment.negative) AS negative 
        FROM tweet 
        JOIN sentiment ON sentiment.tweet_id = tweet.id 
        JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id 
        JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id 
        WHERE tweet.campaign IN %(campaigns)s
        GROUP BY hashtag.hashtag 
        ORDER BY negative DESC 
        LIMIT %(limit)s;
        """
        params = {'campaigns': tuple(self._campaigns), 'limit': self._k}
        medias_mentioned = pd.read_sql(query, con=self._db_connection, params=params)
        medias_mentioned = medias_mentioned.sort_values(by=["num"], ascending=False)
        medias_mentioned.to_excel(self._writer, sheet_name='top_hashtags_hate', index=False, header=True)

        self._create_bar_chart(medias_mentioned, 'hashtag', 'num', "Hashtag", "Num. Tweets", "Top hashtags related to negative sentiment", "top_hashtags_negative.png")

        return medias_mentioned

    def _create_bar_chart(self, data, x_col, y_col, x_label, y_label, title, output_file):
        """Create a bar chart and save as an image."""
        fig = px.bar(data, x=x_col, y=y_col, labels={x_col: x_label, y_col: y_label}, title=title)
        fig.write_image(output_file)


