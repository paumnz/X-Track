"""
Module to implement the network analysis functionality of XTRACK's engine.
"""


from datetime import date
from logging import INFO
from typing import Any, Dict, Literal, Tuple

import networkx as nx
import pandas as pd
from matplotlib.figure import Figure

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError
from xtrack_engine.errors.operational_errors import CannotConvertAnalyzerResultsToImage
from xtrack_engine.network_analysis.network_generation.network_generator import NetworkGenerator
from xtrack_engine.network_analysis.network_generation.reply_network_generator import ReplyNetworkGenerator
from xtrack_engine.network_analysis.network_generation.retweet_network_generator import RetweetNetworkGenerator


class NetworkAnalyzer(Analyzer):
    """
    Class to implement the network analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = INFO
        ) -> None:
        """
        Constructor method for the NetworkAnalyzer class.

        Args:
            campaigns (str | Tuple[str, ...]): the campaign/s to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.retweet_network_generator = RetweetNetworkGenerator(campaigns, db_connector, log_level)
        self.reply_network_generator = ReplyNetworkGenerator(campaigns, db_connector, log_level)


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the NetworkMetricAnalyzer. """
        return """
            SELECT source, target, weight, source_sentiment, source_activity, target_sentiment, target_activity
            FROM network_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                network_type = %(network_type)s
        """


    def __select_network_generator_for_analysis(self, network_type : Literal['retweet', 'reply']) -> NetworkGenerator:
        """
        Private method to select the network generator for the network metric analysis.

        Args:
            network_type: the network type to be created for the analysis, either a retweet or a reply network.

        Returns:
            A NetworkGenerator capable of creating the required networks.
        """
        self.logger.debug('Selecting the network generator to be used')

        match network_type:
            case 'retweet':
                network_generator = self.retweet_network_generator
            case 'reply':
                network_generator = self.reply_network_generator
            case _:
                raise IllegalAnalysisConfigError(f'Illegal network type configuration for NetworkAnalyzer: {network_type}')

        self.logger.debug('Selected the network generator to be used')

        return network_generator


    def __keep_most_relevant_nodes(self, network : nx.DiGraph, top_k : int) -> nx.DiGraph:
        """
        Method to filter a network keeping only the top-K most central nodes (degree centrality).

        Args:
            network (DiGraph): the original network.
            top_k (int): the number of nodes to keep in the network (at max).

        Returns:
            A filtered version of the given network with the top-K most central nodes.
        """
        self.logger.debug(f'Filtering the network to keep the top-{top_k} most central nodes')

        # Step 1: Calculating the centrality measure
        degree_centrality = nx.degree_centrality(network)

        # Step 2: Calculating the top-K most central nodes
        top_nodes = sorted(degree_centrality, key = degree_centrality.get, reverse = True)[:top_k]

        # Step 3: Filtering the graph
        network = network.subgraph(top_nodes)

        self.logger.debug(f'Filtered the network to keep the top-{top_k} most central nodes')

        return network


    def __retrieve_node_attributes(self, nodes : Tuple[Any, ...], hashtags) -> Dict[str, Dict[Any, float | int]]:
        """
        Method to assign the sentiment to each node (color visualization in the graph).

        Args:
            nodes (Tuple[Any, ...]): the nodes whose sentiment must be obtained.
            hashtags (Tuple[str, ...]): the hashtags with which to filter user activity.

        Returns:
            A dictionary that maps each attribute to a node-value mapping.
        """
        self.logger.debug(f'Retrieving attributes from given nodes')

        if len(nodes) == 0:
            return {
                'user_sentiment' : {},
                'user_activity' : {}
            }

        if hashtags is None:
            query = """
                SELECT q1.user_network_id AS user_network_id, AVG(s.positive) AS user_sentiment, COUNT(t.id) AS user_activity
                FROM
                    tweet t
                    INNER JOIN (
                        SELECT
                            id AS user_db_id,
                            COALESCE(username, user_id) AS user_network_id
                        FROM user
                    ) AS q1 ON q1.user_db_id = t.author_id
                    INNER JOIN sentiment s ON s.tweet_id = t.id
                WHERE
                    t.campaign IN %(campaigns)s AND
                    q1.user_network_id IN %(user_network_ids)s
                GROUP BY user_network_id
            """
            params = {'campaigns' : tuple(self.campaigns), 'user_network_ids' : nodes}
        else:
            query = """
                SELECT q1.user_network_id AS user_network_id, AVG(s.positive) AS user_sentiment, COUNT(t.id) AS user_activity
                FROM
                    tweet t
                    INNER JOIN (
                        SELECT
                            id AS user_db_id,
                            COALESCE(username, user_id) AS user_network_id
                        FROM user
                    ) AS q1 ON q1.user_db_id = t.author_id
                    INNER JOIN sentiment s ON s.tweet_id = t.id
                    INNER JOIN hashtagt_tweet ht ON ht.tweet_id = t.id
                    INNER JOIN hashtag h ON h.id = ht.hashtag_id
                WHERE
                    t.campaign IN %(campaigns)s AND
                    q1.user_network_id IN %(user_network_ids)s AND
                    h.hashtag IN %(hashtags)s
                GROUP BY user_network_id
            """
            params = {'campaigns' : tuple(self.campaigns), 'user_network_ids' : nodes, 'hashtags' : hashtags}

        network_df = self.db_connector.retrieve_table_from_sql(query, params)
        network_df['user_activity'] /= max(network_df['user_activity']) # Normalize activity

        self.logger.debug(f'Retrieved attributes from given nodes')

        return network_df.set_index('user_network_id').to_dict()


    def __format_analysis_results(
            self,
            network : nx.DiGraph,
            node_attributes : Dict[Any, float],
        ) -> pd.DataFrame:
        """
        Method to format the analysis results into a Pandas DataFrame.
        """
        analysis_results_data = []

        for source_node, target_node, attrs in network.edges(data = True):
            analysis_results_data.append(
                [
                    source_node,
                    target_node,
                    attrs['weight'],
                    node_attributes['user_sentiment'].get(source_node, 0.5),
                    node_attributes['user_activity'].get(source_node, 0.0),
                    node_attributes['user_sentiment'].get(target_node, 0.5),
                    node_attributes['user_activity'].get(target_node, 0.0),
                ]
            )

        return pd.DataFrame(
            analysis_results_data,
            columns = ['source', 'target', 'weight', 'source_sentiment', 'source_activity', 'target_sentiment', 'target_activity']
        )


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None,
            network_type : Literal['retweet', 'reply'] = 'retweet',
            first_date : date = None,
            last_date : date = None,
            top_k : int = 50
        ) -> pd.DataFrame:
        """
        Method to carry out the network analysis over time of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results in the database.
            hashtags: the hashtags with which to filter the activity (if any).
            network_type: the type of network to be used, either a retweet or a reply network.
            first_date: the first date to be considered for analyzing the network.
            last_date: the last date considered for analyzing the network.
            window_size_in_days: the size in days of the time windows to study.
            top_k: the number of most central nodes to keep (at max).

        Returns:
            The network analysis of the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Executing network metric analysis on the given campaigns and hashtags')

        # Step 1: Setting up the network generator to be used and the time interval to cover
        network_generator = self.__select_network_generator_for_analysis(network_type)

        # Step 2: Network extraction
        network = network_generator.generate_network(first_date, last_date, hashtags)

        # Step 3: Filtering the network to keep the top-K most central nodes
        if len(network.nodes) > 0:
            network = self.__keep_most_relevant_nodes(network, top_k = top_k)

        # Step 4: Retrieving node attributes
        nodes_attributes = self.__retrieve_node_attributes(tuple(network.nodes), hashtags)

        # Step 5: Formatting the results
        self.analysis_results : pd.DataFrame = self.__format_analysis_results(network, nodes_attributes)

        # Step 6: Storing the results in the database
        edge_df = self.analysis_results.copy()
        edge_df['campaign_analysis_id'] = campaign_analysis_id
        edge_df['network_type'] = network_type
        edge_df = edge_df[['campaign_analysis_id', 'source', 'target', 'weight', 'source_sentiment', 'source_activity', 'target_sentiment', 'target_activity', 'network_type']]
        self.db_connector.store_table_to_sql(edge_df, 'network_analysis_results', 'append')

        self.logger.debug(f'Executed network metric analysis on the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the networks formed during the given campaign/hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing TweetRedundancyAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A DataFrame describing the network (of the given type) formed during the given campaign/hashtags.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(self) -> pd.DataFrame:
        """
        Method to convert the NetworkAnalyzer results to a Pandas DataFrame.

        Returns:
            A Pandas DataFrame with the NetworkAnalyzer results.
        """
        self.logger.debug('Converting NetworkAnalyzer results into a Pandas DataFrame')

        network_df : pd.DataFrame = self.analysis_results.copy()
 
        self.logger.debug('Converted NetworkAnalyzer results into a Pandas DataFrame')

        return network_df


    def to_image(self) -> Figure:
        """
        Method to convert the NetworkAnalyzer results into a figure.

        Returns:
            The figure containing the results of the NetworkAnalyzer.
        """
        raise CannotConvertAnalyzerResultsToImage(f'Cannot convert {self.__class__.__name__} results to image')
