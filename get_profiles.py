import operator
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import networkx as nx
import pymongo
from networkx.algorithms.community import greedy_modularity_communities

class Users:

    def __init__(self, db_connection, pymongo_conn, campaigns, hashtags, k, writer, G_reply, G_rt):
        self._db_connection = db_connection
        self._pymongo_conn = pymongo_conn
        self._campaigns = campaigns
        self._hashtags = hashtags
        self._k = k
        self._writer = writer
        self._G_reply = G_reply
        self._G_rt = G_rt

    def _map_field(self, x, field):
        user = self._pymongo_conn.find_one({"id": str(x["user_id"])})
        if user:
            return user.get(field, "")
        return ""

    def _map_username(self, x):
        return self._map_field(x, "username")

    def _map_description(self, x):
        return self._map_field(x, "description")

    def _map_user_created(self, x):
        return self._map_field(x, "created_at")

    def _map_month(self, x):
        return x["created_at"][:7]

    def get_influencers(self, G, k=20):
        """
        Calculate and return the top influencers in the given graph based on various centrality measures.
        """
        try:
            score_btc = nx.betweenness_centrality(G, normalized=True, weight="w", endpoints=True)
            btc_list = [node for node, _ in sorted(score_btc.items(), key=operator.itemgetter(1), reverse=True)[:k]]
        except Exception as e:
            btc_list = []
            print(f"Error in betweenness_centrality: {e}")

        try:
            score_evc = nx.eigenvector_centrality(G, weight="w")
            evc_list = [node for node, _ in sorted(score_evc.items(), key=operator.itemgetter(1), reverse=True)[:k]]
        except Exception as e:
            evc_list = []
            print(f"Error in eigenvector_centrality: {e}")

        try:
            score_csc = nx.closeness_centrality(G)
            csc_list = [node for node, _ in sorted(score_csc.items(), key=operator.itemgetter(1), reverse=True)[:k]]
        except Exception as e:
            csc_list = []
            print(f"Error in closeness_centrality: {e}")

        try:
            score_dgc = nx.degree_centrality(G)
            dgc_list = [node for node, _ in sorted(score_dgc.items(), key=operator.itemgetter(1), reverse=True)[:k]]
        except Exception as e:
            dgc_list = []
            print(f"Error in degree_centrality: {e}")

        all_scores = dgc_list + btc_list + csc_list + evc_list
        return Counter(all_scores)

    def _execute_query(self, query, params):
        return pd.read_sql(query, con=self._db_connection, params=params)

    def get_top_posters(self):
        """
        Retrieve the top posters for the specified campaigns and hashtags.
        """
        query = """
            SELECT user_id, COUNT(tweet.id) AS num 
            FROM tweet
            JOIN user ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            GROUP BY user_id
            ORDER BY num DESC
            LIMIT %(limit)s;
        """
        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None,
            'limit': self._k
        }
        tweets = self._execute_query(query, params)
        tweets["username"] = tweets.apply(lambda x: self._map_username(x), axis=1)
        tweets["description"] = tweets.apply(lambda x: self._map_description(x), axis=1)
        tweets.to_excel(self._writer, sheet_name='top_posters', index=False, header=True)
        return tweets["user_id"].to_list()

    def get_top_repliers(self):
        """
        Retrieve the top repliers for the specified campaigns and hashtags.
        """
        query = """
            SELECT user_id, COUNT(reply.id) AS num
            FROM tweet
            JOIN reply ON reply.tweet_id = tweet.id
            JOIN user ON user.id = tweet.author_id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            GROUP BY user_id
            ORDER BY num DESC
            LIMIT %(limit)s;
        """
        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None,
            'limit': self._k
        }
        tweets = self._execute_query(query, params)
        tweets["username"] = tweets.apply(lambda x: self._map_username(x), axis=1)
        tweets["description"] = tweets.apply(lambda x: self._map_description(x), axis=1)
        tweets.to_excel(self._writer, sheet_name='top_repliers', index=False, header=True)
        return tweets["user_id"].to_list()

    def get_top_authors_tweets(self, mode="rt"):
        """
        Retrieve the top tweet authors based on retweets or replies for the specified campaigns and hashtags.
        """
        if mode == "rt":
            query = """
                SELECT user_id, tweet_metrics.retweet_count + like_count AS general_interactions, tweet.text
                FROM tweet
                JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                JOIN user ON tweet.author_id = user.id
                LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                WHERE tweet.campaign IN %(campaigns)s
                AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
                AND tweet.text NOT LIKE 'RT %%'
                ORDER BY general_interactions DESC
                LIMIT %(limit)s;
            """
        else:
            query = """
                SELECT user_id, tweet_metrics.quote_count + reply_count AS replies, tweet.text
                FROM tweet
                JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                JOIN user ON tweet.author_id = user.id
                LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                WHERE tweet.campaign IN %(campaigns)s
                AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
                AND tweet.text NOT LIKE 'RT %%'
                ORDER BY replies DESC
                LIMIT %(limit)s;
            """
        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None,
            'limit': self._k
        }
        tweets = self._execute_query(query, params)
        tweets["username"] = tweets.apply(lambda x: self._map_username(x), axis=1)
        tweets["description"] = tweets.apply(lambda x: self._map_description(x), axis=1)
        tweets.to_excel(self._writer, sheet_name='top_tweet_authors', index=False, header=True)
        return tweets["user_id"].to_list()

    def gen_top_users(self):
        """
        Generate and export the top users based on various criteria.
        """
        print("[+] Generating top users")
        influencers_rt = self.get_influencers(self._G_rt)
        influencers_reply = self.get_influencers(self._G_reply)

        top_authors = Counter(self.get_top_authors_tweets())
        top_authors_reply = Counter(self.get_top_authors_tweets(mode="reply"))

        repliers = Counter(self.get_top_repliers())
        posters = Counter(self.get_top_posters())

        top_centrality = influencers_rt + influencers_reply
        influencers_central = pd.DataFrame.from_dict(top_centrality, orient='index').reset_index()
        influencers_central = influencers_central.rename(columns={'index': 'user_id', 0: 'count'}).sort_values(by=['count'], ascending=False)
        influencers_central["username"] = influencers_central.apply(lambda x: self._map_username(x), axis=1)
        influencers_central.to_excel(self._writer, sheet_name='top_influencers_centrality', index=False, header=True)

        all_influencers = influencers_rt + influencers_reply + top_authors + top_authors_reply + repliers + posters
        influencers = pd.DataFrame.from_dict(all_influencers, orient='index').reset_index()
        influencers = influencers.rename(columns={'index': 'user_id', 0: 'count'}).sort_values(by=['count'], ascending=False)
        influencers["username"] = influencers.apply(lambda x: self._map_username(x), axis=1)
        print("[+] Dumping users to excel")
        influencers.to_excel(self._writer, sheet_name='top_influencers', index=False, header=True)

    def gen_users_month(self):
        """
        Generate and export the number of user accounts created each month.
        """
        query = """
            SELECT DISTINCT user.user_id
            FROM user
            JOIN tweet ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s);
        """
        params = {
            'campaigns': tuple(self._campaigns),
            'hashtags': tuple(self._hashtags) if self._hashtags else None
        }
        tweets = self._execute_query(query, params)
        tweets["username"] = tweets.apply(lambda x: self._map_username(x), axis=1)
        tweets["created_at"] = tweets.apply(lambda x: self._map_user_created(x), axis=1)
        tweets["month"] = tweets.apply(lambda x: self._map_month(x), axis=1)
        users_group = tweets.groupby(by=tweets['month'])["user_id"].count().sort_index(ascending=True).to_frame().reset_index()
        users_group.to_excel(self._writer, sheet_name='accounts_month', index=False, header=True)
        fig = px.line(users_group, x="month", y="user_id", title='Accounts created by month', labels={"month": "Month", "user_id": "Num. Accounts"})
        fig.write_image("accounts_month.png")

