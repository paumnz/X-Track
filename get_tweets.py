import operator
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
from scipy import stats
import collections
import networkx as nx
import pymongo
from networkx.algorithms.community import greedy_modularity_communities
import plotly.graph_objects as go
from nltk.corpus import stopwords
import re
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

class Tweets:
    def __init__(self, db_connection, pymongo_conn, campaigns, hashtags, k, writer):
        self._db_connection = db_connection
        self._pymongo_conn = pymongo_conn
        self._campaigns = campaigns
        self._hashtags = hashtags
        self._k = k
        self._writer = writer
        self._stops = set(stopwords.words('spanish'))
        self._stops.update(set(stopwords.words('english')))
        self._stops.update(set(stopwords.words('arabic')))
        self._stops.update(set(stopwords.words('french')))

    def _map_field(self, x, field):
        user = self._pymongo_conn.find_one({"id": str(x["user_id"])})
        if user:
            return user.get(field, "")
        return ""

    def _map_username(self, x):
        return self._map_field(x, "username")

    def _map_description(self, x):
        return self._map_field(x, "description")

    def get_repeated_tweets(self):
        """
        Retrieves the most repeated tweets based on specified campaigns and hashtags.
        """
        if self._hashtags:
            query = """
                SELECT tweet.text, user.user_id, COUNT(tweet.id) AS num
                FROM tweet, user, hashtagt_tweet, hashtag
                WHERE tweet.author_id = user.id
                AND tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                AND tweet.text NOT LIKE 'RT %%'
                GROUP BY tweet.text, user.user_id
                ORDER BY num DESC
                LIMIT %s;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags), self._k)
        else:
            query = """
                SELECT tweet.text, user.user_id, COUNT(tweet.id) AS num
                FROM tweet, user
                WHERE tweet.author_id = user.id
                AND tweet.campaign IN %s
                AND tweet.text NOT LIKE 'RT %%'
                GROUP BY tweet.text, user.user_id
                ORDER BY num DESC
                LIMIT %s;
            """
            params = (tuple(self._campaigns), self._k)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        tweets["username"] = tweets.apply(self._map_username, axis=1)
        tweets["description"] = tweets.apply(self._map_description, axis=1)
        tweets.to_excel(self._writer, sheet_name='repeated_tweets', index=False, header=True)
        return tweets

    def get_top_tweets(self, mode="rt"):
        """
        Retrieves the top tweets based on retweets or likes.
        """
        if self._hashtags:
            if mode == "like":
                query = """
                    SELECT tweet.text, user.user_id, tweet_metrics.like_count
                    FROM tweet, user, tweet_metrics, hashtagt_tweet, hashtag
                    WHERE tweet.text NOT LIKE 'RT %%'
                    AND tweet.campaign IN %s
                    AND hashtag.hashtag IN %s
                    AND hashtagt_tweet.tweet_id = tweet.id
                    AND hashtagt_tweet.hashtag_id = hashtag.id
                    AND tweet_metrics.tweet_id = tweet.id
                    AND tweet.author_id = user.id
                    ORDER BY tweet_metrics.like_count DESC
                    LIMIT %s;
                """
                params = (tuple(self._campaigns), tuple(self._hashtags), self._k)
            else:
                query = """
                    SELECT tweet.text, user.user_id, tweet_metrics.retweet_count
                    FROM tweet, user, tweet_metrics, hashtagt_tweet, hashtag
                    WHERE tweet.text NOT LIKE 'RT %%'
                    AND tweet.campaign IN %s
                    AND hashtag.hashtag IN %s
                    AND hashtagt_tweet.tweet_id = tweet.id
                    AND hashtagt_tweet.hashtag_id = hashtag.id
                    AND tweet_metrics.tweet_id = tweet.id
                    AND tweet.author_id = user.id
                    ORDER BY tweet_metrics.retweet_count DESC
                    LIMIT %s;
                """
                params = (tuple(self._campaigns), tuple(self._hashtags), self._k)
        else:
            if mode == "like":
                query = """
                    SELECT tweet.text, user.user_id, tweet_metrics.like_count
                    FROM tweet, user, tweet_metrics
                    WHERE tweet.text NOT LIKE 'RT %%'
                    AND tweet.campaign IN %s
                    AND tweet_metrics.tweet_id = tweet.id
                    AND tweet.author_id = user.id
                    ORDER BY tweet_metrics.like_count DESC
                    LIMIT %s;
                """
                params = (tuple(self._campaigns), self._k)
            else:
                query = """
                    SELECT tweet.text, user.user_id, tweet_metrics.retweet_count
                    FROM tweet, user, tweet_metrics
                    WHERE tweet.text NOT LIKE 'RT %%'
                    AND tweet.campaign IN %s
                    AND tweet_metrics.tweet_id = tweet.id
                    AND tweet.author_id = user.id
                    ORDER BY tweet_metrics.retweet_count DESC
                    LIMIT %s;
                """
                params = (tuple(self._campaigns), self._k)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        tweets["username"] = tweets.apply(self._map_username, axis=1)
        tweets["description"] = tweets.apply(self._map_description, axis=1)
        tweets.to_excel(self._writer, sheet_name=f'top_tweets_{mode}', index=False, header=True)
        return tweets

    def gen_tweets_hour(self):
        """
        Generates a line graph of the number of tweets per hour.
        """
        if self._hashtags:
            query = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num
                FROM tweet, hashtagt_tweet, hashtag
                WHERE tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num
                FROM tweet
                WHERE tweet.campaign IN %s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = (tuple(self._campaigns),)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        fig = px.line(tweets, x="dayhour", y="num", title='Tweets per hour', labels={"dayhour": "Day/Hour", "num": "Num. Tweets"})
        fig.write_image("tweets_hour.png")

    def gen_lang_dist(self):
        """
        Generates a pie chart of the language distribution of tweets.
        """
        if self._hashtags:
            query = """
                SELECT lang AS Language, COUNT(tweet.id) AS num
                FROM tweet, hashtagt_tweet, hashtag
                WHERE tweet.lang != 'und'
                AND tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                GROUP BY lang
                ORDER BY num DESC
                LIMIT 5;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query = """
                SELECT lang AS Language, COUNT(tweet.id) AS num
                FROM tweet
                WHERE tweet.lang != 'und'
                AND tweet.campaign IN %s
                GROUP BY lang
                ORDER BY num DESC
                LIMIT 5;
            """
            params = (tuple(self._campaigns),)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        fig = px.pie(tweets, values='num', names='Language', title='Language distribution')
        fig.write_image("lang_distribution.png")

    def gen_sentiment(self):
        """
        Generates a line graph of the positive and negative sentiment evolution per day/hour.
        """
        if self._hashtags:
            query_pos = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num_positive
                FROM tweet, sentiment, hashtagt_tweet, hashtag
                WHERE sentiment.tweet_id = tweet.id
                AND sentiment.positive > 0.5
                AND tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            query_neg = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num_negative
                FROM tweet, sentiment, hashtagt_tweet, hashtag
                WHERE sentiment.tweet_id = tweet.id
                AND sentiment.negative > 0.5
                AND tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query_pos = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num_positive
                FROM tweet, sentiment
                WHERE sentiment.tweet_id = tweet.id
                AND sentiment.positive > 0.5
                AND tweet.campaign IN %s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            query_neg = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS num_negative
                FROM tweet, sentiment
                WHERE sentiment.tweet_id = tweet.id
                AND sentiment.negative > 0.5
                AND tweet.campaign IN %s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = (tuple(self._campaigns),)

        tweets_pos = pd.read_sql(query_pos, con=self._db_connection, params=params)
        tweets_neg = pd.read_sql(query_neg, con=self._db_connection, params=params)
        tweets_posneg = pd.merge(tweets_pos, tweets_neg, on='dayhour', how='outer')

        fig = go.Figure(layout=go.Layout(
            title=go.layout.Title(text="Sentiment evolution per day/hour"),
            xaxis_title="Day/Hour",
            yaxis_title="Num. Tweets",
        ))
        fig.add_trace(go.Scatter(x=tweets_posneg["dayhour"], y=tweets_posneg["num_positive"],
                                 mode='lines+markers', name='Positive'))
        fig.add_trace(go.Scatter(x=tweets_posneg["dayhour"], y=tweets_posneg["num_negative"],
                                 mode='lines+markers', name='Negative'))
        fig.write_image("sentiment_evolution.png")

    def gen_treemap(self):
        """
        Generates a treemap of the entities in the tweets.
        """
        if self._hashtags:
            query = """
                SELECT domain.category, domain.name, COUNT(tweet.id) AS num
                FROM domain, tweet, annotation_tweet, hashtagt_tweet, hashtag
                WHERE tweet.id = annotation_tweet.tweet_id
                AND domain.id = annotation_tweet.domain_id
                AND tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id
                GROUP BY domain.category, domain.name
                ORDER BY num DESC;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query = """
                SELECT domain.category, domain.name, COUNT(tweet.id) AS num
                FROM domain, tweet, annotation_tweet
                WHERE tweet.id = annotation_tweet.tweet_id
                AND domain.id = annotation_tweet.domain_id
                AND tweet.campaign IN %s
                GROUP BY domain.category, domain.name
                ORDER BY num DESC;
            """
            params = (tuple(self._campaigns),)

        entities = pd.read_sql(query, con=self._db_connection, params=params)
        fig = px.treemap(entities, path=[px.Constant(""), 'category', 'name'], values='num', title="Entities map")
        fig.write_image("entities_map.png")

    def _cleaner(self, word):
        """
        Cleans the text by removing special characters and stopwords.
        """
        word = re.sub(r'http\S+', '', word)
        word = re.sub(r'www\S+', '', word)
        word = re.sub(r'[^a-zA-Z\s]', '', word)
        word = re.sub(r'\s+', ' ', word)
        word = word.strip().lower()
        return ' '.join([w for w in word.split() if w not in self._stops])

    def _plot_cloud(self, wordcloud):
        """
        Plots and saves a word cloud image.
        """
        plt.figure(figsize=(40, 30))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.savefig('word_cloud_all.png')

    def gen_wordcloud(self):
        """
        Generates a word cloud from the tweets' text.
        """
        if self._hashtags:
            query = """
                SELECT text
                FROM tweet, hashtagt_tweet, hashtag
                WHERE tweet.campaign IN %s
                AND hashtag.hashtag IN %s
                AND hashtagt_tweet.tweet_id = tweet.id
                AND hashtagt_tweet.hashtag_id = hashtag.id;
            """
            params = (tuple(self._campaigns), tuple(self._hashtags))
        else:
            query = """
                SELECT text
                FROM tweet
                WHERE tweet.campaign IN %s;
            """
            params = (tuple(self._campaigns),)

        tweets = pd.read_sql(query, con=self._db_connection, params=params)
        tweets["text_clean"] = tweets["text"].apply(self._cleaner)
        text = ' '.join(tweets["text_clean"].values)

        wordcloud = WordCloud(width=3000, height=2000, random_state=1, background_color='white', colormap='Set2',
                              collocations=False, stopwords=STOPWORDS).generate(text)
        self._plot_cloud(wordcloud)

