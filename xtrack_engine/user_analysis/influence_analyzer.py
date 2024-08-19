"""
Module to implement the influence analysis functionality of XTRACK's engine.
"""


import logging
from collections import Counter
from typing import Any, List, Literal, Tuple

import networkx as nx
from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError
from xtrack_engine.network_analysis.network_generation.retweet_network_generator import RetweetNetworkGenerator
from xtrack_engine.network_analysis.network_generation.reply_network_generator import ReplyNetworkGenerator


class InfluenceAnalyzer(Analyzer):
    """
    Class to implement the influencers detection functionality of XTRACK's engine.
    """


    def __init__(self, campaigns : str | Tuple[str, ...], db_connector : DBConnector, log_level : int = logging.INFO) -> None:
        """
        Constructor method of the NetworkGenerator class.

        Args:
            campaign (str | Tuple[str, ...]): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.campaigns : Tuple[str, ...] = campaigns if type(campaigns) == tuple else (campaigns, )
        self.db_connector : DBConnector = db_connector
        self.retweet_network_generator : RetweetNetworkGenerator = RetweetNetworkGenerator(campaigns, db_connector, log_level)
        self.reply_network_generator : RetweetNetworkGenerator = RetweetNetworkGenerator(campaigns, db_connector, log_level)


    def __calculate_betweenness_centrality(self, network : nx.Graph, top_k : int) -> Tuple[Any, ...]:
        """
        Method to calculate the top-K most influential users computed through betweenness centrality.
        Args:
            network: the network whose betweenness centrality will be computed.
            top_k: the number of most influential users to be retrieved by the method.

        Returns:
            A dictionary that maps each user of the network with its betweenness centrality.
        """
        top_influencers : List[Any] = []

        self.logger.debug(f'Calculating top-{top_k} most influential users by betweenness centrality')

        try:
            betweenness_centrality_scores = nx.betweenness_centrality(network, normalized = True, weight = 'weight', endpoints = True)
            top_influencers = [
                node
                for node, _ in sorted(
                    betweenness_centrality_scores.items(),
                    key = lambda item_tuple: item_tuple[1],
                    reverse = True
                )[:top_k]
            ]
        except Exception as exc:
            self.logger.error(f'Error found when computing betweenness centrality @ graph {network}: {exc}')

        self.logger.debug(f'Calculated top-{top_k} most influential users by betweenness centrality')

        return tuple(top_influencers)


    def __calculate_eigenvector_centrality(self, network : nx.Graph, top_k : int) -> Tuple[Any, ...]:
        """
        Method to calculate the top-K most influential users computed through eigenvector centrality.
        Args:
            network: the network whose eigenvector centrality will be computed.
            top_k: the number of most influential users to be retrieved by the method.

        Returns:
            A dictionary that maps each user of the network with its eigenvector centrality.
        """
        top_influencers : List[Any] = []

        self.logger.debug(f'Calculating top-{top_k} most influential users by eigenvector centrality')

        try:
            eigenvector_centrality_scores = nx.eigenvector_centrality(network, weight = 'weight')
            top_influencers = [
                node
                for node, _ in sorted(
                    eigenvector_centrality_scores.items(),
                    key = lambda item_tuple: item_tuple[1],
                    reverse = True
                )[:top_k]
            ]
        except Exception as exc:
            self.logger.error(f'Error found when computing eigenvector centrality @ graph {network}: {exc}')

        self.logger.debug(f'Calculated top-{top_k} most influential users by eigenvector centrality')

        return tuple(top_influencers)


    def __calculate_closeness_centrality(self, network : nx.Graph, top_k : int) -> Tuple[Any, ...]:
        """
        Method to calculate the top-K most influential users computed through closeness centrality.
        Args:
            network: the network whose closeness centrality will be computed.
            top_k: the number of most influential users to be retrieved by the method.

        Returns:
            A dictionary that maps each user of the network with its closeness centrality.
        """
        top_influencers : List[Any] = []

        self.logger.debug(f'Calculating top-{top_k} most influential users by closeness centrality')

        try:
            closeness_centrality_scores = nx.closeness_centrality(network)
            top_influencers = [
                node
                for node, _ in sorted(
                    closeness_centrality_scores.items(),
                    key = lambda item_tuple: item_tuple[1],
                    reverse = True
                )[:top_k]
            ]
        except Exception as exc:
            self.logger.error(f'Error found when computing closeness centrality @ graph {network}: {exc}')

        self.logger.debug(f'Calculated top-{top_k} most influential users by closeness centrality')

        return tuple(top_influencers)


    def analyze(
            self, 
            top_k : int,
            hashtags : Tuple[str, ...] | None = None,
            network_type : Literal['retweet', 'reply'] = 'retweet'
        ) -> Tuple[Any, ...]:
        """
        Method to carry out the influence analysis of the XTRACK's engine.

        Args:
            top_k: the number of most influential users to be retrieved.
            hashtags: the hashtags with which to filter the network creation.
            network_type: the type of network to be created.

        Returns:
            The top_k most influential users of the network.
        """
        self.logger.debug(f'Calculating top-{top_k} most influential users by all centrality measures')

        match network_type:
            case 'retweet':
                network : nx.DiGraph = self.retweet_network_generator.generate_network(hashtags = hashtags)
            case 'reply':
                network : nx.DiGraph = self.reply_network_generator.generate_network(hashtags = hashtags)
            case _:
                raise IllegalAnalysisConfigError(f'Illegal network_type configuration for InfluenceAnalyzer: {network_type}')

        # Step 1: Calculating the top-K most influential users by individual per centrality measure
        bc_ranking = self.__calculate_betweenness_centrality(network, top_k)
        ec_ranking = self.__calculate_eigenvector_centrality(network, top_k)
        cc_ranking = self.__calculate_closeness_centrality(network, top_k)

        # Step 2: Calculating the top-K most influential users across the different rankings
        self.analysis_results : Tuple[Tuple[Any, int], ...] = tuple(Counter(bc_ranking + ec_ranking + cc_ranking).most_common(top_k))

        self.logger.debug(f'Calculated top-{top_k} most influential users by all centrality measures')

        return self.analysis_results


    def to_pandas_dataframe(self, user_column_name : str = 'user', top_k_appareances_column_name : str = 'top_k_appareances') -> DataFrame:
        """
        Method to convert the InfluenceAnalyzer results to a Pandas DataFrame.

        Args:
            user_column_name: the name of the column holding the users.
            top_k_appareances_column_name: the name of the column containing the number of top-k influence ranking appeareances of the user.

        Returns:
            A Pandas DataFrame with the InfluenceAnalyzer results.
        """
        self.logger.debug('Converting InfluenceAnalyzer results into a Pandas DataFrame')

        influence_df = DataFrame(data = self.analysis_results, columns = [user_column_name, top_k_appareances_column_name])

        self.logger.debug('Converted InfluenceAnalyzer results into a Pandas DataFrame')

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
        Method to convert the InfluenceAnalyzer results into a figure.

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
            The figure containing the results of the InfluenceAnalyzer.
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
