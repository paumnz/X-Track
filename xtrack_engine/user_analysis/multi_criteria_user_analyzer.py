"""
Module to implement the functionality to detect relevant users through several criteria of XTRACK's engine.
"""


import logging
from collections import Counter
from typing import Any, List, Tuple

import networkx as nx
from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.user_analysis.influence_analyzer import InfluenceAnalyzer
from xtrack_engine.user_analysis.tweet_impact_analyzer import TweetImpactAnalyzer
from xtrack_engine.user_analysis.user_tweet_activity_analyzer import UserTweetActivityAnalyzer
from xtrack_engine.user_analysis.user_reply_activity_analyzer import UserReplyActivityAnalyzer

class MultiCriteriaUserAnalyzer(Analyzer):
    """
    Class to implement the multi-criteria relevant user detection functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = logging.INFO
        ) -> None:
        """
        Constructor method of the MultiCriteriaUserAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.influence_analyzer = InfluenceAnalyzer(campaigns, db_connector, log_level)
        self.tweet_impact_analyzer = TweetImpactAnalyzer(campaigns, db_connector, log_level)
        self.user_tweet_activity_analyzer = UserTweetActivityAnalyzer(campaigns, db_connector, log_level)
        self.user_reply_activity_analyzer = UserReplyActivityAnalyzer(campaigns, db_connector, log_level)


    def analyze(self, top_k : int, hashtags : Tuple[str, ...], retweet_network : nx.Graph, reply_network : nx.Graph) -> Tuple[Any, ...]:
        """
        Method to detect most relevant users of the given campaigns analysis of the XTRACK's engine.

        Args:
            top_k: the number of most influential users to be retrieved.
            hashtags: the hashtags with which to filter the activity to carry out relevant user detection.
            retweet_network: the network that interconnects users based on their retweets.
            reply_network: the network that interconnects users based on their replies.

        Returns:
            The top_k most influential users of the network.
        """
        self.logger.debug(f'Calculating top-{top_k} most influential users by various criteria')

        # Step 1: Calculating influential users based on centrality measures
        top_centrality_users_retweet = self.influence_analyzer.analyze(retweet_network, top_k)
        top_centrality_users_reply = self.influence_analyzer.analyze(reply_network, top_k)

        # Step 2: Calculating influential users based on their activity
        top_posters = self.user_tweet_activity_analyzer.analyze(top_k, hashtags)
        top_repliers = self.user_reply_activity_analyzer.analyze(top_k, hashtags)

        # Step 3: Calculating influential users based on their impact
        users_with_highest_rt_like_impact = self.tweet_impact_analyzer.analyze(top_k, hashtags, 'rt+like')
        users_with_highest_reply_quote_impact = self.tweet_impact_analyzer.analyze(top_k, hashtags, 'reply+quote')

        # Step 4: Calculating overall influential users
        top_users = top_centrality_users_retweet + \
                    top_centrality_users_reply + \
                    top_posters + \
                    top_repliers + \
                    users_with_highest_rt_like_impact + \
                    users_with_highest_reply_quote_impact

        top_users = [user for user, _ in top_users]
        self.analysis_results : Tuple[Tuple[Any, int], ...] = tuple(Counter(top_users).most_common())

        self.logger.debug(f'Calculated top-{top_k} most influential users by various criteria')

        return self.analysis_results


    def to_pandas_dataframe(self, user_column_name : str = 'user', top_k_appareances_column_name : str = 'top_k_appareances') -> DataFrame:
        """
        Method to convert the MultiCriteriaUserAnalyzer results to a Pandas DataFrame.

        Args:
            user_column_name: the name of the column holding the users.
            top_k_appareances_column_name: the name of the column containing the number of top-k influence ranking appeareances of the user.

        Returns:
            A Pandas DataFrame with the MultiCriteriaUserAnalyzer results.
        """
        self.logger.debug('Converting MultiCriteriaUserAnalyzer results into a Pandas DataFrame')

        influence_df = DataFrame(data = self.analysis_results, columns = [user_column_name, top_k_appareances_column_name])

        self.logger.debug('Converted MultiCriteriaUserAnalyzer results into a Pandas DataFrame')

        return influence_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Users',
            y_axis_label : str = 'Top-N Ranking Appareances',
            title : str = 'Most influential users',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the MultiCriteriaUserAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            color: the color to be used for the barplot.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            The figure containing the results of the MultiCriteriaUserAnalyzer.
        """
        self.logger.debug('Converting influence analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'user',
            y_axis_column_name = 'top_k_appareances',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted influence analysis results to image')

        return fig
