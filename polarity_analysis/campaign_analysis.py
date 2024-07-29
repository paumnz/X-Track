from .polarity_scores import polarity_scores
from .topic_detection import topic_detection
from pathlib import Path
import pandas as pd
import networkx as nx
import plotly.express as px
import json

class Polarity:
    def __init__(self, db_connection, campaigns, candidates=[], outdir="./results/"):


        self._engine = db_connection
        self._campaigns = "','".join(campaigns)
        self._topic_detection = topic_detection(engine=self._engine)
        self._polarity_detection = polarity_scores(engine=self._engine)
        self._out_dir = self._create_out_dir(outdir)
        self._campaign_analysis = {}

    def _create_out_dir(self, outdir):


        Path(outdir).mkdir(parents=True, exist_ok=True)
        return outdir

    def _get_dates(self):

        query_dates = '''
            SELECT DISTINCT(DATE_FORMAT(tweet.start_time,"%%%%Y-%%%%m-%%%%d")) as dates
            FROM tweet
            WHERE tweet.campaign IN ('%s')
        ''' % (self._campaigns)
        campaign_dates = list(pd.read_sql(query_dates, con=self._engine)["dates"])
        return campaign_dates

    def _gen_polarization_chart(self, polarization_scores):

        df_scores = pd.DataFrame(polarization_scores, columns=['date', 'polarization_score'])
        fig = px.line(df_scores, x="date", y="polarization_score", title='Polarization per topic over campaign dates')
        fig.write_image(self._out_dir + "polarization_score_chart.png")

    def _process_charts(self, campaign_data):

        pscores, mscores, dates = [], [], []

        for date, data in campaign_data.items():
            for idx in data.keys():
                dates.append(date)
                pscores.append(data[idx]["pscore"])
                mscores.append(data[idx]["modularity"])

        df = pd.DataFrame({"dates": dates, "mscores": mscores, "pscores": pscores}).sort_values(by=['dates'])
        
        fig_polarization = px.line(df, x="dates", y="pscores", title='Polarization levels per day 0-1', labels={"dates": "Date", "pscores": "Polarization score"})
        fig_polarization.write_image(self._out_dir + "polarization_hour.png")

        fig_fragmentation = px.line(df, x="dates", y="mscores", title='Fragmentation levels in the conversation per day 0-1', labels={"dates": "Date", "mscores": "Fragmentation score"})
        fig_fragmentation.write_image(self._out_dir + "fragmentation_hour.png")

    def analyse_polarity(self, max_topics=10, topic_method="top_hashtags_all", graph_method="retweet"):

        campaign_dates = self._get_dates()
        date_topics = []
        campaign_data = {}

        if topic_method == "top_hashtags_all":
            date_topics = [self._topic_detection.gen_tags_all(campaign=self._campaigns, max_topics=max_topics)]

        for date in campaign_dates:
            if topic_method == "top_hashtags_day":
                date_topics = [self._topic_detection.gen_day_tags(campaign=self._campaigns, date=date, max_topics=max_topics)]
            
            campaign_data[date] = {}

            for i, topic in enumerate(date_topics):
                G = self._polarity_detection.gen_graph(category=graph_method, topics=topic, date=date)
                output_dir = self._out_dir + date + "_" + str(i) + "/"
                Path(output_dir).mkdir(parents=True, exist_ok=True)
                nx.write_edgelist(G, output_dir + 'graph_' + date + "_" + str(topic) + ".csv", data=False)

                if nx.is_empty(G):
                    campaign_data[date][i] = {
                        "topic_words": topic,
                        "pscore": 0.0,
                        "num_communities": 0,
                        "modularity": 0.0,
                        "rwc_matrix_sentiment": [],
                        "rwc_matrix": [],
                        "influencers": []
                    }
                    continue

                parts, modularity = self._polarity_detection.gen_partitions(G, mode="modularity")
                num_communities = parts[0]

                if num_communities > 1:
                    influencers = self._polarity_detection.get_influencer_matrix(G, parts)
                    pscore, rwc_matrix, rwc_matrix_sentiment = self._polarity_detection.polarity_score_multi(G, parts, influencers)
                else:
                    pscore, rwc_matrix, rwc_matrix_sentiment, influencers = 0.0, [[]], [[]], [[]]

                campaign_data[date][i] = {
                    "topic_words": topic,
                    "pscore": pscore,
                    "num_communities": num_communities,
                    "modularity": modularity,
                    "rwc_matrix_sentiment": rwc_matrix_sentiment,
                    "rwc_matrix": rwc_matrix,
                    "influencers": influencers
                }

        self._process_charts(campaign_data)

        with open(self._out_dir + str(self._campaigns) + '_campaign_analysis.json', 'w') as fp:
            json.dump(campaign_data, fp)

