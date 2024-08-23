"""
Module to implement the tweet creation time per sentiment analysis functionality of XTRACK's engine.
"""


from typing import Any, Dict, Tuple

from matplotlib.figure import Figure
import pandas as pd

from xtrack_engine._analyzer import Analyzer


class TweetSentimentCreationTimeAnalyzer(Analyzer):
    """
    Class to implement the tweet creation time per sentiment analysis functionality of XTRACK's engine.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the UserReplyActivityAnalyzer. """
        return """
            SELECT dayhour, tweet_volume, sentiment
            FROM tweet_sentiment_creation_time_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


    def __retrieve_positive_tweet_volume_per_hour(self, hashtags = None) -> pd.DataFrame:
        """
        Method to retrieve the volume of positive tweets per hour filtered by the given campaigns and hashtags.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the total number of positive tweets created per hour on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving tweet volume per hour (positive)')

        if hashtags is None:
            query = """
                SELECT CONCAT(DATE_FORMAT(tweet.created_at, '%%Y-%%m-%%d'), CONCAT(' ', DATE_FORMAT(tweet.created_at, '%%H'))) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    sentiment.positive > 0.5 AND
                    tweet.campaign IN %(campaigns)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT CONCAT(DATE_FORMAT(tweet.created_at, '%%Y-%%m-%%d'), CONCAT(' ', DATE_FORMAT(tweet.created_at, '%%H'))) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    sentiment.positive > 0.5 AND
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}

        tweet_volume_df = self.db_connector.retrieve_table_from_sql(query, params)
        tweet_volume_df['sentiment'] = 'positive'

        self.logger.debug(f'Retrieving tweet volume per hour (positive)')

        return tweet_volume_df


    def __retrieve_negative_tweet_volume_per_hour(self, hashtags = None) -> pd.DataFrame:
        """
        Method to retrieve the volume of negative tweets per hour filtered by the given campaigns and hashtags.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the total number of negative tweets created per hour on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving tweet volume per hour (negative)')

        if hashtags is None:
            query = """
                SELECT CONCAT(DATE_FORMAT(tweet.created_at, '%%Y-%%m-%%d'), CONCAT(' ', DATE_FORMAT(tweet.created_at, '%%H'))) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    sentiment.negative > 0.5 AND
                    tweet.campaign IN %(campaigns)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT CONCAT(DATE_FORMAT(tweet.created_at, '%%Y-%%m-%%d'), CONCAT(' ', DATE_FORMAT(tweet.created_at, '%%H'))) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    sentiment.negative > 0.5 AND
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}

        tweet_volume_df = self.db_connector.retrieve_table_from_sql(query, params)
        tweet_volume_df['sentiment'] = 'negative'

        self.logger.debug(f'Retrieving tweet volume per hour (negative)')

        return tweet_volume_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> pd.DataFrame:
        """
        Method to carry out the sentiment tweet volume per hour analysis of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The tweet volume per sentiment and hour filtered by the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Calculating tweet volume per sentiment and hour on the given campaigns and hashtags')

        # Step 1: Calculating the tweet creation time per sentiment
        positive_tweet_volume_df : pd.DataFrame = self.__retrieve_positive_tweet_volume_per_hour(hashtags)
        negative_tweet_volume_df : pd.DataFrame = self.__retrieve_negative_tweet_volume_per_hour(hashtags)

        self.analysis_results : pd.DataFrame = pd.concat(
            [
                positive_tweet_volume_df,
                negative_tweet_volume_df
            ]
        )

        # Step 2: Storing the results in the database
        tweet_df = self.analysis_results.copy()
        tweet_df['campaign_analysis_id'] = campaign_analysis_id
        self.db_connector.store_table_to_sql(tweet_df, 'tweet_sentiment_creation_time_analysis_results', 'append')

        self.logger.debug(f'Calculated tweet volume per sentiment and hour on the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the creation time of tweets per sentiment in the given campaigns and hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing TweetSentimentCreationTimeAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple of tuples (user, interactions) describing the tweet creation time per sentiment in the given campaign.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            dayhour_column_name : str = 'dayhour',
            tweet_volume_column_name : str = 'tweet_volume',
            sentiment_column_name : str = 'sentiment'
        ) -> pd.DataFrame:
        """
        Method to convert the TweetSentimentCreationTimeAnalyzer results to a Pandas DataFrame.

        Args:
            dayhour_column_name: the column holding the day-hour measured.
            tweet_volume_column_name: the name of the column holding the volume of tweets in that dayhour and sentiment.
            sentiment_column_name: the name of the column holding the sentiment related to the tweet volume measurement.

        Returns:
            A Pandas DataFrame with the TweetSentimentCreationTimeAnalyzer results.
        """
        self.logger.debug('Converting TweetSentimentCreationTimeAnalyzer results into a Pandas DataFrame')

        tweet_sentiment_volume_df : pd.DataFrame = self.analysis_results.copy()
        tweet_sentiment_volume_df.columns = [dayhour_column_name, tweet_volume_column_name, sentiment_column_name]

        self.logger.debug('Converted TweetSentimentCreationTimeAnalyzer results into a Pandas DataFrame')

        return tweet_sentiment_volume_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            colors : Tuple[str, ...] = None,
            x_axis_label : str = 'Hour',
            y_axis_label : str = 'Tweets',
            title : str = 'Tweets per hour and sentiment',
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the TweetSentimentCreationTimeAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            colors: the color to be used for each of the two sentiments (a tuple of two elements is expected).
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            legend: a flag that indicates whether a legend should be included or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            The figure containing the results of the TweetSentimentCreationTimeAnalyzer.
        """
        self.logger.debug('Converting tweet sentiment creation time results to image')

        fig = self.visualizer.create_comparative_line_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'dayhour',
            y_axis_column_name = 'tweet_volume',
            category_column_name = 'sentiment',
            width = width,
            height = height,
            colors = colors,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            legend = legend,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted tweet sentiment creation time analysis results to image')

        return fig
