import networkx as nx
import networkx.algorithms.community as nx_comm
import nxmetis
import random
from sqlalchemy import create_engine
import pandas as pd
import collections
import math 
from itertools import combinations
import plotly.graph_objects as go



class polarity_scores:

    def __init__(self, engine) -> None:
        
        self._db_connection = engine



    def map_col(x, partitions, field="a") -> str:
        author = x[field]

        if author in partitions[1][0]:
            return "left"
        else:
            return "right"

    def _get_reply_sentiment(self, user_id, part):

        q=''' 
        SELECT avg(sentiment.positive) as pos, avg(sentiment.negative) as neg from tweet, user, reply, sentiment 
        where tweet.author_id=user.id 
        and sentiment.tweet_id=tweet.id 
        and reply.tweet_id=tweet.id
        and user.user_id="%s"
        and reply.reply_to in ('%s')
        ''' %(user_id,"','".join(part))

        reply_sentiment = pd.read_sql(q, con=self._db_connection)

        if list(reply_sentiment["pos"])[0] and list(reply_sentiment["neg"])[0]:
            return list(reply_sentiment["pos"])[0], list(reply_sentiment["neg"])[0]
        else:
            return 0,0


    def _gen_graph_from_query(self, q, directed=False):
        network_sample = pd.read_sql(q, con=self._db_connection)
        if directed:
            G = nx.from_pandas_edgelist(network_sample, 'a', 'b', ["w"], create_using=nx.DiGraph())

        else:
            G = nx.from_pandas_edgelist(network_sample, 'a', 'b', ["w"])
        return G
        
    def count_topic_appears(self, campaign, topics, date=None):

        if date:
            pass
        else:
            pass

    def gen_graph(self, category="retweet", connected=True, remove_isolated=True, topics=[], date=None, directed=False):

        # IF A RT B: CONNECT A - B
        if category=="retweet":
            q = '''select user.user_id as a, t.retweeter as b, count(retweeter) as w from 
            (SELECT user.user_id as retweeter, tweet.tweet_id, retweet.retweeted FROM tweet, user,retweet,hashtag,hashtagt_tweet 
            WHERE tweet.author_id=user.id 
            and hashtagt_tweet.hashtag_id=hashtag.id and hashtagt_tweet.tweet_id=tweet.id
            and hashtag in ('%s') 
            and DATE_FORMAT(tweet.start_time,"%%%%Y-%%%%m-%%%%d")="%s" 
            and retweet.tweet_id=tweet.id) as t, user, tweet where t.retweeted=tweet.tweet_id 
            and tweet.author_id=user.id group by retweeter, a order by w desc''' %("','".join(topics), date)

            G=self._gen_graph_from_query(q, directed=directed)


        # IF A RT B AND C RT B: CONNECT A - B and B - C    
        elif category=="retweet_full":

            q='''SELECT DISTINCT(retweet.retweeted) FROM retweet, tweet,hashtag,hashtagt_tweet  where retweet.retweeted = tweet.tweet_id and DATE_FORMAT(tweet.start_time,"%%%%Y-%%%%m-%%%%d")="%s" and hashtagt_tweet.hashtag_id=hashtag.id and hashtagt_tweet.tweet_id=tweet.id
            and hashtag in ('%s') 
            ''' % (date,"','".join(topics))

            network_sample = pd.read_sql(q, con=self._db_connection)
            network_sample=list(network_sample["retweeted"])
            if directed:
                G = nx.DiGraph()
            else:
                G = nx.Graph() 
            for retweet in network_sample:
                q_rt='select DISTINCT(user.user_id) from user, retweet, tweet where retweet.tweet_id=tweet.id and tweet.author_id=user.id and retweet.retweeted='+retweet+''
                rt_network = pd.read_sql(q_rt, con=self._db_connection)
                if directed:
                    Grt = nx.DiGraph()
                else:
                    Grt = nx.Graph()                 
                nodes = [retweet]
                nodes += list(rt_network["user_id"])
                edges = list(combinations(nodes, 2))

                Grt.add_edges_from(edges)
                
                G = nx.compose(G,Grt)


        # IF A REPLY B: CONNECT A - B
        elif category=="reply":
            q = '''select t.retweeter as a, t.reply_to as b, count(t.reply_to) as w from 
            (SELECT user.user_id as retweeter, tweet.tweet_id, reply.reply_to FROM tweet, user,reply,hashtag,hashtagt_tweet 
            WHERE tweet.author_id=user.id 
            and hashtagt_tweet.hashtag_id=hashtag.id and hashtagt_tweet.tweet_id=tweet.id
            and hashtag in ('%s')
            and DATE_FORMAT(tweet.start_time,"%%%%Y-%%%%m-%%%%d")="%s" 
            and reply.tweet_id=tweet.id) as t GROUP by a,b''' %("','".join(topics), date)

            G=self._gen_graph_from_query(q, directed=directed)

        if remove_isolated:
            G.remove_nodes_from(list(nx.isolates(G)))

        if connected:
            Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
            G = G.subgraph(Gcc[0])

        return G

    def gen_partitions(self, G, mode="metis"):
        part=None
        if mode=="metis":

            part = list(nxmetis.partition(G, 2))
            part[0]=2

        if mode=="modularity":
            part = nx_comm.greedy_modularity_communities(G)
            modularity = nx_comm.modularity(G, part)
            communities = list(part)
            com=[len(communities),[]]
            for c in communities:
                com[1].append(list(c))

            part=com

        
        return part, modularity

    def get_influencer_matrix(self, G, parts, metric="degree_centrality", k=10):

        influencers_list = []

        for part in parts[1]:
            # part = community in G

            influencers = []
            H = G.subgraph(part)
            if metric=="betweenness_centrality":
                score = nx.betweenness_centrality(H, normalized=True, endpoints=True)
            elif metric=="eigenvector_centrality":
                score = nx.eigenvector_centrality(H)
            elif metric=="closeness_centrality":
                score = nx.closeness_centrality(H)
            else:
                score = nx.degree_centrality(H)

            k = math.ceil((k * len(H.nodes()) ) / 100)

            nodes_metric = [a_tuple[0] for a_tuple in list(collections.OrderedDict(sorted(score.items())).items())]

            influencers_list.append(nodes_metric[:k])

        return influencers_list


    def get_influencers(self, G, parts, metric="degree_centrality", k=10):

        k = math.ceil((k * len(G.nodes()) ) / 100)

        if metric=="betweenness_centrality":
            score = nx.betweenness_centrality(G, normalized=True, endpoints=True)

        elif metric=="eigenvector_centrality":
            score = nx.eigenvector_centrality(G)

        elif metric=="closeness_centrality":
            score = nx.closeness_centrality(G)

        else:
            score = nx.degree_centrality(G)


        influencers = [a_tuple[0] for a_tuple in list(collections.OrderedDict(sorted(score.items())).items())]

        influencers_a = []
        influencers_b = []

        i = 0

        while len(influencers_a) < k or len(influencers_b) < k:
            if influencers[i] in parts[1][0]:
                if len(influencers_a) < k:
                    influencers_a.append(influencers[i])
            elif influencers[i] in parts[1][1]:
                if len(influencers_b) < k:
                    influencers_b.append(influencers[i])
            i+=1

        return influencers_a, influencers_b


    def _random_walk_multi(self, G, node, parts, influencers_matrix):
        flag=0
        side = None
        sentiment_parts = [ 0.0 for i in range(len(parts))]
        j = 1
        while flag != 1:
            node_neighbors=[n for n in G.neighbors(node)]
            node = random.choice(node_neighbors)
            # check replies of node
            # reply - sentiment
            
            for i in range(0, len(parts)):
                sentiment = self._get_reply_sentiment(node, parts[i])
                # if positive > negative add 1 else add -1 
                if sentiment[1] > sentiment[0]:
                    sentiment = 1
                elif sentiment[0] > sentiment[1]:
                    sentiment = -1
                else:
                    sentiment = 0
                sentiment_parts[i] += sentiment
            j+=1
            i=0
            for row in influencers_matrix:
                if node in row:
                    side = i
                    flag = 1
                i+=1
        
        return side, sentiment_parts



    def polarity_score_multi(self, G, parts, influencers_matrix, iterations=100, restart=False):

        n = parts[0]
        rwc_matrix = [ [ 0.0 for i in range(n) ] for j in range(n) ]
        rwc_matrix_sentiment = [ [ 0.0 for i in range(n) ] for j in range(n) ]
        parts=parts[1]

        for x in range(0, iterations):
            k=0
            for k in range(0,n):

                part = parts[k]

                node=random.sample(part,1)[0]
                side, sentiment = self._random_walk_multi(G, node, parts, influencers_matrix)

                for j in range(0, len(sentiment)):

                    rwc_matrix_sentiment[k][j] += max(sentiment[j] / iterations, 0)
                    # avoid numbers > 1.0 due to floating point operations
                    #rwc_matrix_sentiment[k][j] = min(1, rwc_matrix_sentiment[k][j])

                rwc_matrix[k][side] += 1/iterations
        print("interaction matrix:")
        print(rwc_matrix)
        print("sentiment matrix:")
        print(rwc_matrix_sentiment)
        polarity_score = self._calc_polarity(rwc_matrix, rwc_matrix_sentiment)

        return polarity_score, rwc_matrix, rwc_matrix_sentiment


    def _calc_polarity(self, rwc_matrix, rwc_matrix_sentiment):
        
        v=0
        vs = 0
        n = len(rwc_matrix)

        for i in range(n):
    
            for k in range(n):
                
                v +=  pow( ((1/n) - rwc_matrix[i][k]) ,2)
                vs += pow(rwc_matrix_sentiment[i][k],2)


        pscore = ((v * (1/(n-1))) + (vs * (1/ pow(n,2)))) / 2
        return pscore










