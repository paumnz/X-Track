"""
Module to implement the template followed by all network generators of XTRACK framework's engine.
"""


import logging
from abc import ABC, abstractmethod
from datetime import date
from typing import Tuple

import networkx as nx
from pandas import DataFrame

from xtrack_engine._utils.loggable_entity import LoggableEntity
from xtrack_engine.database_connection.db_connector import DBConnector


class NetworkGenerator(ABC, LoggableEntity):
    """
    Abstract class to generate networks based on a specific relationship criterium between users.
    """


    def __init__(self, campaigns : str | Tuple[str, ...], db_connector : DBConnector, log_level : int = logging.INFO) -> None:
        """
        Constructor method of the NetworkGenerator class.

        Args:
            campaign (str | Tuple[str, ...]): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(log_level)

        self.campaigns : Tuple[str, ...] = campaigns if type(campaigns) == tuple else (campaigns, )
        self.db_connector : DBConnector = db_connector


    def __retrieve_first_date(self, hashtags : Tuple[str, ...] | None = None) -> date:
        """
        Private method to retrieve the first date of the campaign/s given (also hashtags if provided).

        Args:
            hashtags (Tuple[str, ...] | None): an optional parameter containing hashtags to be used for filtering tweet retrieval.

        Returns:
            The date in which the first tweet of the campaign and hashtags was published.
        """
        self.logger.debug('Retrieving the first date of the campaign')

        if hashtags is None:
            query = """
                SELECT MIN(created_at) AS min_date
                FROM tweet
                WHERE campaign IN %(campaigns)s
            """
            params = {'campaigns' : tuple(self.campaigns)}
        else:
            query = """
                SELECT MIN(created_at) AS min_date
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns' : tuple(self.campaigns), 'hashtags' : hashtags}

        first_date : DataFrame = self.db_connector.retrieve_table_from_sql(query, params)['min_date'].to_list()[0]

        self.logger.debug('Retrieved the first date of the campaign')
        return first_date


    def __retrieve_last_date(self, hashtags : Tuple[str, ...] | None = None) -> date:
        """
        Private method to retrieve the last date of the campaign/s given (also hashtags if provided).

        Args:
            hashtags (Tuple[str, ...] | None): an optional parameter containing hashtags to be used for filtering tweet retrieval.

        Returns:
            The date in which the last tweet of the campaign and hashtags was published.
        """
        self.logger.debug('Retrieving the last date of the campaign')

        if hashtags is None:
            query = """
                SELECT MAX(created_at) AS max_date
                FROM tweet
                WHERE campaign IN %(campaigns)s
            """
            params = {'campaigns' : tuple(self.campaigns)}
        else:
            query = """
                SELECT MAX(created_at) AS max_date
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns' : tuple(self.campaigns), 'hashtags' : hashtags}

        last_date : DataFrame = self.db_connector.retrieve_table_from_sql(query, params)['max_date'].to_list()[0]

        self.logger.debug('Retrieved the last date of the campaign')
        return last_date


    def __filter_edges_with_non_relevant_weight(self, network : nx.DiGraph, min_threshold : int) -> None:
        """
        Module to remove edges from a network whose weight is smaller than a minimum threshold.

        Args:
            network (DiGraph): the network that will be filtered.
            min_threshold (int): the minimum weight required for an edge to exist in the network.
        """
        self.logger.debug(f'Removing edges with weight < {min_threshold}')

        # Step 1: Finding the edges that need to be removed
        edges_to_remove = [
            (node_u, node_v)
            for node_u, node_v, data in network.edges(data = True) if data['weight'] < min_threshold
        ]

        # Step 2: Removing the edges
        network.remove_edges_from(edges_to_remove)

        self.logger.debug(f'Removed edges with weight < {min_threshold}')


    @abstractmethod
    def _generate_network_dataframe(
            self,
            first_date : date = None,
            last_date : date = None,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Private method to generate a network based on a specific strategy (from an initial date to a final one).

        Args:
            first_date (date): the minimum date from which user relationships will be considered.
            last_date (date): the maximum date up to which user relationships will be considered.
            hashtags (Tuple[str, ...] | None): an optional parameter containing hashtags to be used for filtering tweet retrieval.

        Returns:
            A Pandas DataFrame containing the related users and the strength of their relationship.
        """


    def __generate_network_from_dataframe(
            self,
            network_df : DataFrame
        ) -> nx.DiGraph:
        """
        Private method to generate a network from a relationship Pandas DataFrame.

        Args:
            network_df: the Pandas DataFrame containing the relationships between users and their strength.

        Returns:
            A directed graph that connects the related users with a given strength.
        """
        self.logger.debug('Generating network from DataFrame')

        network = nx.DiGraph()

        for _, row in network_df.iterrows():
            network.add_edge(row['rter'], row['rted'], weight = row['weight'])

        self.logger.debug('Generated network from DataFrame')

        return network


    def generate_network(
            self,
            first_date : date = None,
            last_date : date = None,
            hashtags : Tuple[str, ...] | None = None,
            min_threshold : int = None
        ) -> nx.DiGraph:
        """
        Method to generate a network based on a specific strategy (from an initial date to a final one).

        Args:
            first_date (date): the minimum date from which user relationships will be considered.
            last_date (date): the maximum date up to which user relationships will be considered.
            hashtags (Tuple[str, ...] | None): an optional parameter to filter network extraction by specific hashtags.
            min_threshold (int): the minimum number of relationships required for an edge to exist between users.

        Returns:
            The generated network in the given time interval with relevant relationships (if threshold is given).
        """

        first_date = first_date if first_date is not None else self.__retrieve_first_date(hashtags)
        last_date = last_date if last_date is not None else self.__retrieve_last_date(hashtags)

        # Step 1: Extracting network
        network_df : DataFrame = self._generate_network_dataframe(first_date, last_date, hashtags)

        # Step 2: Building network from dataframe
        network : nx.DiGraph = self.__generate_network_from_dataframe(network_df)

        # Step 3: Keeping only relevant relationships
        if min_threshold is not None:
            self.__filter_edges_with_non_relevant_weight(network, min_threshold)

        return network
