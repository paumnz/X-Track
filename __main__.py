from sqlalchemy import create_engine
import pandas as pd
import networkx as nx
import pymongo
from get_tweets import Tweets
from get_profiles import Users
from get_medias import Medias
from get_hashtags import Hashtags
from get_topics import Topics
from polarity_analysis import campaign_analysis
from config import DB_CONNECTION_STR, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

class SnowBall:
    def __init__(self, db_connection=None, pymongo_conn=None, campaigns=None, hashtags=None, k=15, output_file='analysis.xlsx'):
        self._writer = pd.ExcelWriter(output_file)
        self._campaigns = campaigns
        self._hashtags = hashtags
        self._pymongo_conn = pymongo_conn
        self._db_connection = db_connection

        self._G_rt = self._gen_graph(mode="rt")
        self._G_reply = self._gen_graph(mode="reply")

        self._tweets = Tweets(self._db_connection, self._pymongo_conn, self._campaigns, self._hashtags, k, self._writer)
        self._users = Users(self._db_connection, self._pymongo_conn, self._campaigns, self._hashtags, k, self._writer, self._G_reply, self._G_rt)
        self._medias = Medias(self._db_connection, self._pymongo_conn, self._campaigns, self._hashtags, k, self._writer)
        self._hashtag_tool = Hashtags(self._db_connection, self._pymongo_conn, self._campaigns, self._hashtags, k, self._writer)
        self._topics = Topics(self._db_connection, self._pymongo_conn, self._campaigns, self._hashtags, k, self._writer)

    def _map_username(self, x, val):
        """
        Map user ID to username using MongoDB.
        """
        username = self._pymongo_conn.find_one({"id": str(x[val])})
        if username:
            return username.get("username", "")
        return ""

    def _gen_graph(self, mode="rt"):
        """
        Generate a graph for retweet or reply relationships.
        """
        campaigns_str = "','".join(self._campaigns)
        if self._hashtags:
            hashtags_str = "','".join(self._hashtags)
            if mode == "rt":
                query = """
                SELECT user.user_id AS a, t.retweeter AS b, COUNT(retweeter) AS w
                FROM (
                    SELECT user.user_id AS retweeter, tweet.tweet_id, retweet.retweeted
                    FROM tweet
                    JOIN user ON tweet.author_id = user.id
                    JOIN retweet ON retweet.tweet_id = tweet.id
                    JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                    WHERE tweet.campaign IN (%s)
                    AND hashtag.hashtag IN (%s)
                ) AS t
                JOIN user ON t.retweeted = user.id
                JOIN tweet ON t.retweeted = tweet.id
                GROUP BY retweeter, a
                ORDER BY w DESC
                """ % (campaigns_str, hashtags_str)
            else:
                query = """
                SELECT t.retweeter AS a, t.reply_to AS b, COUNT(t.reply_to) AS w
                FROM (
                    SELECT user.user_id AS retweeter, tweet.tweet_id, reply.reply_to
                    FROM tweet
                    JOIN user ON tweet.author_id = user.id
                    JOIN reply ON reply.tweet_id = tweet.id
                    JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                    WHERE tweet.campaign IN (%s)
                    AND hashtag.hashtag IN (%s)
                ) AS t
                GROUP BY a, b
                """ % (campaigns_str, hashtags_str)
        else:
            if mode == "rt":
                query = """
                SELECT user.user_id AS a, t.retweeter AS b, COUNT(retweeter) AS w
                FROM (
                    SELECT user.user_id AS retweeter, tweet.tweet_id, retweet.retweeted
                    FROM tweet
                    JOIN user ON tweet.author_id = user.id
                    JOIN retweet ON retweet.tweet_id = tweet.id
                    JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    WHERE tweet.campaign IN (%s)
                ) AS t
                JOIN user ON t.retweeted = user.id
                JOIN tweet ON t.retweeted = tweet.id
                GROUP BY retweeter, a
                ORDER BY w DESC
                """ % campaigns_str
            else:
                query = """
                SELECT t.retweeter AS a, t.reply_to AS b, COUNT(t.reply_to) AS w
                FROM (
                    SELECT user.user_id AS retweeter, tweet.tweet_id, reply.reply_to
                    FROM tweet
                    JOIN user ON tweet.author_id = user.id
                    JOIN reply ON reply.tweet_id = tweet.id
                    WHERE tweet.campaign IN (%s)
                ) AS t
                GROUP BY a, b
                """ % campaigns_str

        network = pd.read_sql(query, con=self._db_connection).sort_values(by=['w'], ascending=False)
        network_rel = network[network["a"] != network["b"]].head(15)
        network_rel["username_a"] = network_rel.apply(lambda x: self._map_username(x, 'a'), axis=1)
        network_rel["username_b"] = network_rel.apply(lambda x: self._map_username(x, 'b'), axis=1)

        network_rel.to_excel(self._writer, sheet_name=f'main_relations_{mode}', index=False, header=True)

        G = nx.from_pandas_edgelist(network, source='a', target='b', edge_attr=True, create_using=nx.DiGraph())
        nx.write_gexf(G, f"graph_{mode}.gexf")

        return G

    def process_tweets(self):
        """
        Process tweets data.
        """
        self._tweets.get_top_tweets()
        self._tweets.get_repeated_tweets()
        self._tweets.gen_tweets_hour()
        self._tweets.gen_lang_dist()
        self._tweets.gen_sentiment()
        self._tweets.gen_treemap()
        self._tweets.gen_wordcloud()

    def process_users(self):
        """
        Process users data.
        """
        self._users.gen_top_users()
        self._users.gen_users_month()

    def process_hashtags(self):
        """
        Process hashtags data.
        """
        self._hashtag_tool.get_top_hashtags()
        self._hashtag_tool.get_top_hashtags_hate()

    def process_medias(self):
        """
        Process media data.
        """
        self._medias.get_top_domans()
        self._medias.get_top_headlines()

    def process_polarity(self):
        """
        Process polarity data.
        """
        p = campaign_analysis.Polarity(campaigns=self._campaigns, db_connection=self._db_connection, candidates=[])
        p.analyse_polarity()

    def process_topics(self):
        """
        Process topics data.
        """
        self._topics.gen_topics()

    def save_excel(self):
        """
        Save the analysis to an Excel file.
        """
        self._writer.save()

if __name__ == "__main__":
    db_connection = create_engine(DB_CONNECTION_STR)
    myclient = pymongo.MongoClient(MONGO_URI)
    mydb = myclient[MONGO_DB_NAME]
    pymongo_conn = mydb[MONGO_COLLECTION_NAME]

    campaigns = ["EXAMPLE"]
    hashtags = None

    print("[*] Campaign analysis tool")
    driver = SnowBall(db_connection, pymongo_conn, campaigns, hashtags, 15)
    driver.process_tweets()
    driver.process_medias()
    driver.process_hashtags()
    driver.process_topics()
    driver.save_excel()
    driver.process_users()
    driver.save_excel()

