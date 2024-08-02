"""
Module to implement the tweet impact analysis functionality of XTRACK's engine.
"""


from typing import Literal, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError
from xtrack_engine.errors.operational_errors import CannotConvertAnalyzerResultsToImage


class TweetImpactAnalyzer(Analyzer):
    """
    Class to implement the tweet impact analysis functionality of XTRACK's engine.
    """


    def __retrieve_most_impactful_tweets_using_retweets(self, top_k : int, hashtags) -> DataFrame:
        """
        Method to retrieve the top-K most impactful tweets based on retweet count on the given campaigns and hashtags.

        Args:
            top_k: the number of most impactful tweets to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the top-K most impactful tweets (based on retweet count) of the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving top-{top_k} most impactful tweets (retweets)')

        if hashtags is None:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, tweet_metrics.retweet_count AS impact
                    FROM
                        tweet
                        INNER JOIN user ON user.id = tweet.author_id
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                    WHERE
                        tweet.text NOT LIKE 'RT %%' AND
                        tweet.campaign IN %(campaigns)s
                    ORDER BY impact DESC
                    LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k}
        else:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, tweet_metrics.retweet_count AS impact
                    FROM
                        tweet
                        INNER JOIN user ON user.id = tweet.author_id
                        INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                        INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                    WHERE
                        tweet.text NOT LIKE 'RT %%'
                        AND tweet.campaign IN %(campaigns)s
                        AND hashtag.hashtag IN %(hashtags)s
                    ORDER BY impact DESC
                    LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags, 'top_k' : top_k}

        impact_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieving top-{top_k} most impactful tweets (retweets)')

        return impact_df


    def __retrieve_most_impactful_tweets_using_likes(self, top_k : int, hashtags) -> DataFrame:
        """
        Method to retrieve the top-K most impactful tweets based on like count on the given campaigns and hashtags.

        Args:
            top_k: the number of most impactful tweets to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the top-K most impactful tweets (based on like count) of the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving top-{top_k} most impactful tweets (likes)')

        if hashtags is None:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, tweet_metrics.like_count AS impact
                    FROM
                        tweet
                        INNER JOIN user ON user.id = tweet.author_id
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                    WHERE
                        tweet.text NOT LIKE 'RT %%' AND
                        tweet.campaign IN %(campaigns)s
                    ORDER BY impact DESC
                    LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k}
        else:
            query = """
                SELECT tweet.text AS tweet, user.user_id AS user, tweet_metrics.like_count AS impact
                    FROM
                        tweet
                        INNER JOIN user ON user.id = tweet.author_id
                        INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                        INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                    WHERE
                        tweet.text NOT LIKE 'RT %%'
                        AND tweet.campaign IN %(campaigns)s
                        AND hashtag.hashtag IN %(hashtags)s
                    ORDER BY impact DESC
                    LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags, 'top_k' : top_k}

        impact_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieving top-{top_k} most impactful tweets (likes)')

        return impact_df


    def analyze(
            self,
            top_k : int,
            hashtags : Tuple[str, ...] | None = None,
            mode : Literal['retweet', 'like'] = 'retweet'
        ) -> DataFrame:
        """
        Method to carry out the detection of most duplicated tweets of the XTRACK's engine.

        Args:
            top_k: the number of most impactful tweets to be analyzed.
            hashtags: the hashtags with which to filter the activity (if any).
            mode: the manner to account for impactful tweets (retweets or likes).

        Returns:
            The duplicated tweets of the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating top-{top_k} duplicated tweets of the given campaigns and hashtags')

        match mode:
            case 'retweet':
                self.analysis_results = self.__retrieve_most_impactful_tweets_using_retweets(top_k, hashtags)
            case 'like':
                self.analysis_results = self.__retrieve_most_impactful_tweets_using_likes(top_k, hashtags)
            case _:
                raise IllegalAnalysisConfigError(f'Illegal mode configuration for TweetImpactAnalyzer: {mode}')

        self.logger.debug(f'Calculated top-{top_k} duplicated tweets of the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            tweet_column_name : str = 'tweet',
            user_column_name : str = 'user',
            impact_column_name : str = 'impact') -> DataFrame:
        """
        Method to convert the TweetImpactAnalyzer results to a Pandas DataFrame.

        Args:
            tweet_column_name: the name of the column holding the duplicated tweet.
            user_column_name: the name of the column holding the user.
            impact_column_name: the name of the column holding the impact of the tweet (likes or retweets).

        Returns:
            A Pandas DataFrame with the TweetImpactAnalyzer results.
        """
        self.logger.debug('Converting TweetImpactAnalyzer results into a Pandas DataFrame')

        tweet_impact_df : DataFrame = self.analysis_results.copy()
        tweet_impact_df.columns = [tweet_column_name, user_column_name, impact_column_name]

        self.logger.debug('Converted TweetImpactAnalyzer results into a Pandas DataFrame')

        return tweet_impact_df


    def to_image(self) -> Figure:
        """
        Method to convert the TweetImpactAnalyzer results into a figure.

        Returns:
            The figure containing the results of the TweetImpactAnalyzer.
        """
        raise CannotConvertAnalyzerResultsToImage(f'Cannot convert {self.__class__.__name__} results to image')
