"""
Module to implement the influence analysis functionality of XTRACK's engine.
"""


import logging
from collections import Counter
from typing import Any, List, Dict, Literal, Tuple

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
        self.reply_network_generator : ReplyNetworkGenerator = ReplyNetworkGenerator(campaigns, db_connector, log_level)


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the InfluenceAnalyzer. """
        return """
            SELECT user, top_k_appareances
            FROM user_influence_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                network_type = %(network_type)s
        """


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


    def build_new_results(
            self,
            campaign_analysis_id : int,
            top_k : int,
            hashtags : Tuple[str, ...] | None = None,
            network_type : Literal['retweet', 'reply'] = 'retweet'
        ) -> Tuple[Any, ...]:
        """
        Method to carry out the influence analysis of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results into the database.
            top_k: the number of most influential users to be retrieved.
            hashtags: the hashtags with which to filter the network creation.
            network_type: the type of network to be created.

        Returns:
            The top_k most influential users of the network.
        """
        self.logger.debug(f'Calculating top-{top_k} most influential users by all centrality measures')

        retweet_min_threshold = 0 if hashtags is not None else 3

        match network_type:
            case 'retweet':
                network : nx.DiGraph = self.retweet_network_generator.generate_network(hashtags = hashtags, min_threshold = retweet_min_threshold)
            case 'reply':
                network : nx.DiGraph = self.reply_network_generator.generate_network(hashtags = hashtags)
            case _:
                raise IllegalAnalysisConfigError(f'Illegal network_type configuration for InfluenceAnalyzer: {network_type}')

        isolated_nodes = [node for node in network.nodes() if network.in_degree(node) == 0 and network.out_degree(node) == 0]
        network.remove_nodes_from(isolated_nodes)

        # Step 1: Calculating the top-K most influential users by individual per centrality measure
        bc_ranking = self.__calculate_betweenness_centrality(network, top_k)
        ec_ranking = self.__calculate_eigenvector_centrality(network, top_k)
        cc_ranking = self.__calculate_closeness_centrality(network, top_k)

        # Step 2: Calculating the top-K most influential users across the different rankings
        self.analysis_results : Tuple[Tuple[Any, int], ...] = tuple(Counter(bc_ranking + ec_ranking + cc_ranking).most_common(top_k))

        # Step 3: Storing the results into the database
        influence_df = DataFrame(self.analysis_results, columns = ['user', 'top_k_appareances'])
        influence_df['campaign_analysis_id'] = campaign_analysis_id
        influence_df['network_type'] = network_type
        influence_df = influence_df[['campaign_analysis_id', 'user', 'top_k_appareances', 'network_type']]
        self.db_connector.store_table_to_sql(influence_df, 'user_influence_analysis_results', 'append')

        self.logger.debug(f'Calculated top-{top_k} most influential users by all centrality measures')

        return self.analysis_results


    def __format_analysis_results(self, user_influence_df : DataFrame) -> Tuple[Tuple[Any, int], ...]:
        """
        Method to format the results as expected by the front-end.

        Args:
            user_influence_df (DataFrame): the Pandas DataFrame to be formatted.

        Returns:
            A tuple containing (user, top_k_appareances) tuples representing the number of top-k ranking appareances of each user.
        """
        self.logger.debug('Formatting the results of the user influence DataFrame')

        formatted_result = tuple([(row['user'], row['top_k_appareances']) for _, row in user_influence_df.iterrows()])

        self.logger.debug('Formatting the results of the user influence DataFrame')
        return formatted_result


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the most influential users of the given campaigns and hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing UserAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple of tuples (motto, frequency) describing the top-K most influential users.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, self.__format_analysis_results, new_computation_kwargs)


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
