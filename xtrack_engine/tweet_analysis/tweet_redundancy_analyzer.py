"""
Module to implement the duplicated tweet detection functionality of XTRACK's engine.
"""


from typing import Any, Dict, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.errors.operational_errors import CannotConvertAnalyzerResultsToImage


class TweetRedundancyAnalyzer(Analyzer):
    """
    Class to implement the duplicated tweet detection functionality of XTRACK's engine.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the TweetRedundancyAnalyzer. """
        return """
            SELECT tweet, user, frequency
            FROM tweet_redundancy_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


    def __retrieve_duplicated_tweets(self, top_k : int, hashtags) -> DataFrame:
        """
        Method to retrieve the most repeated tweets on the given campaigns and hashtags.

        Args:
            top_k: the number of repeated tweets to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the top-K most repeated tweets of the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving duplicated tweets')

        if hashtags is None:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, COUNT(tweet.id) AS frequency
                FROM tweet
                    INNER JOIN user ON tweet.author_id = user.id
                WHERE
                    tweet.campaign IN %(campaigns)s
                    AND tweet.text NOT LIKE 'RT %%'
                GROUP BY tweet.text, user.user_id
                ORDER BY frequency DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k}
        else:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, COUNT(tweet.id) AS frequency
                FROM
                    tweet
                    INNER JOIN user ON user.id = tweet.author_id
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s
                    AND hashtag.hashtag IN %(hashtags)s
                    AND tweet.text NOT LIKE 'RT %%'
                GROUP BY tweet.text, user.user_id
                ORDER BY frequency DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags, 'top_k' : top_k}

        redundancy_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved duplicated tweets')

        return redundancy_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            top_k : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Method to carry out the detection of most duplicated tweets of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results into the database.
            top_k: the number of most duplicated tweets to retrieve.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The duplicated tweets of the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating top-{top_k} duplicated tweets of the given campaigns and hashtags')

        # Step 1: Calculating the duplicated tweets
        self.analysis_results : DataFrame = self.__retrieve_duplicated_tweets(top_k, hashtags)

        # Step 2: Storing the results into the database
        duplication_df = self.analysis_results.copy()
        duplication_df['campaign_analysis_id'] = campaign_analysis_id
        duplication_df = duplication_df[['campaign_analysis_id', 'tweet', 'user', 'frequency']]
        self.db_connector.store_table_to_sql(duplication_df, 'tweet_redundancy_analysis_results', 'append')

        self.logger.debug(f'Calculated top-{top_k} duplicated tweets of the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the tweets with highest duplication in the given campaign/hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing TweetRedundancyAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A DataFrame describing the top-K tweets with highest duplication.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            tweet_column_name : str = 'tweet',
            user_column_name : str = 'user',
            duplication_count_column_name : str = 'frequency') -> DataFrame:
        """
        Method to convert the TweetRedundancyAnalyzer results to a Pandas DataFrame.

        Args:
            tweet_column_name: the name of the column holding the duplicated tweet.
            user_column_name: the name of the column holding the user.
            duplication_count_column_name: the name of the column holding the duplication of the tweet by the user.

        Returns:
            A Pandas DataFrame with the TweetRedundancyAnalyzer results.
        """
        self.logger.debug('Converting TweetRedundancyAnalyzer results into a Pandas DataFrame')

        repeated_tweets_df : DataFrame = self.analysis_results.copy()
        repeated_tweets_df.columns = [tweet_column_name, user_column_name, duplication_count_column_name]

        self.logger.debug('Converted TweetRedundancyAnalyzer results into a Pandas DataFrame')

        return repeated_tweets_df


    def to_image(self) -> Figure:
        """
        Method to convert the TweetRedundancyAnalyzer results into a figure.

        Returns:
            The figure containing the results of the TweetRedundancyAnalyzer.
        """
        raise CannotConvertAnalyzerResultsToImage(f'Cannot convert {self.__class__.__name__} results to image')
