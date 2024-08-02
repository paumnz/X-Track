"""
Module to implement the tweet (named) entity analysis functionality of XTRACK's engine.
"""


from typing import Tuple

import plotly.graph_objects as go
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class TweetEntityAnalyzer(Analyzer):
    """
    Class to implement the tweet (named) entity analysis functionality of XTRACK's engine.
    """


    def __retrieve_most_employed_tweet_entities(self, top_k : int, hashtags) -> DataFrame:
        """
        Method to retrieve the most used tweet named entities on the given campaigns and hashtags.

        Args:
            top_k: the number of named entities to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the top-K most used named entities in the tweets of the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving the top-{top_k} most used named entities of the campaign')

        if hashtags is None:
            query = """
                SELECT domain.category AS category, domain.name AS entity, COUNT(tweet.id) AS frequency
                FROM annotation_tweet
                    INNER JOIN domain ON domain.id = annotation_tweet.domain_id
                    INNER JOIN tweet ON tweet.id = annotation_tweet.tweet_id
                WHERE
                    tweet.campaign IN %(campaigns)s
                GROUP BY domain.category, domain.name
                ORDER BY frequency DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k}
        else:
            query = """
                SELECT domain.category AS category, domain.name AS entity, COUNT(tweet.id) AS frequency
                FROM annotation_tweet
                    INNER JOIN tweet ON tweet.id = annotation_tweet.tweet_id
                    INNER JOIN domain ON domain.id = annotation_tweet.domain_id
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
                GROUP BY category, entity
                ORDER BY frequency DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags, 'top_k' : top_k}

        redundancy_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved the top-{top_k} most used named entities of the campaign')

        return redundancy_df


    def analyze(self, top_k : int, hashtags : Tuple[str, ...] | None = None) -> DataFrame:
        """
        Method to carry out the detection of most used named entities in tweets of the given campaign/s of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The top-K most used named entities in the tweets of the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Calculating top-{top_k} most used named entities in the tweets of the given campaigns and hashtags')

        self.analysis_results : DataFrame = self.__retrieve_most_employed_tweet_entities(top_k, hashtags)

        self.logger.debug(f'Calculated top-{top_k} most used named entities in the tweets of the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            entity_category_column_name : str = 'category',
            entity_column_name : str = 'entity',
            frequency_column_name : str = 'frequency') -> DataFrame:
        """
        Method to convert the TweetEntityAnalyzer results to a Pandas DataFrame.

        Args:
            entity_category_column_name: the name of the column holding the category of the named entity being described.
            entity_column_name: the name of the column holding the entity being described.
            frequency_column_name: the name of the column holding the frequency of usage of the named entity being described.

        Returns:
            A Pandas DataFrame with the TweetEntityAnalyzer results.
        """
        self.logger.debug('Converting TweetEntityAnalyzer results into a Pandas DataFrame')

        repeated_tweets_df : DataFrame = self.analysis_results.copy()
        repeated_tweets_df.columns = [entity_category_column_name, entity_column_name, frequency_column_name]

        self.logger.debug('Converted TweetEntityAnalyzer results into a Pandas DataFrame')

        return repeated_tweets_df


    def to_image(
            self,
            width : float = 15,
            height : float = 10,
            title : str = 'Entity treemap',
        ) -> go.Figure:
        """
        Method to convert the TweetEntityAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            The figure containing the results of the TweetEntityAnalyzer.
        """
        self.logger.debug('Converting tweet named entity analysis results to image')

        fig = self.visualizer.create_tree_map_plot(
            data = self.to_pandas_dataframe(),
            category_column_name = 'category',
            subcategory_column_name = 'entity',
            value_column_name = 'frequency',
            width = width,
            height = height,
            title = title,
        )

        self.logger.debug('Converted tweet named entity analysis results to image')

        return fig
