"""
Module to implement the tweet creation time analysis functionality of XTRACK's engine.
"""


from typing import Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class TweetCreationTimeAnalyzer(Analyzer):
    """
    Class to implement the tweet creation time analysis functionality of XTRACK's engine.
    """


    def __retrieve_tweet_creation_time_per_hour(self, hashtags) -> DataFrame:
        """
        Method to retrieve the total number of tweets created per hour on the given campaigns and hashtags.

        Args:
            top_k: the number of most impactful tweets to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the total number of tweets created per hour on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving created tweets per hour')

        if hashtags is None:
            query = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                WHERE tweet.campaign IN %(campaigns)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT CAST(CONCAT(DAY(tweet.created_at), HOUR(tweet.created_at)) AS DECIMAL) AS dayhour, COUNT(tweet.id) AS tweet_volume
                FROM
                    tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
                GROUP BY dayhour
                ORDER BY dayhour ASC;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}

        impact_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved created tweets per hour')

        return impact_df


    def analyze(self, hashtags : Tuple[str, ...] | None = None) -> DataFrame:
        """
        Method to carry out the tweet creation time analysis of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The duplicated tweets of the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating tweets per hour of the given campaigns and hashtags')

        self.analysis_results = self.__retrieve_tweet_creation_time_per_hour(hashtags)

        self.logger.debug(f'Calculated tweets per hour of the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            dayhour_column_name : str = 'dayhour',
            tweet_volume_column_name : str = 'tweet_volume'
        ) -> DataFrame:
        """
        Method to convert the TweetCreationTimeAnalyzer results to a Pandas DataFrame.

        Args:
            dayhour_column_name: the column holding the day-hour measured.
            tweet_volume_column_name: the name of the column holding the volume of tweets in that day-hour.

        Returns:
            A Pandas DataFrame with the TweetCreationTimeAnalyzer results.
        """
        self.logger.debug('Converting TweetCreationTimeAnalyzer results into a Pandas DataFrame')

        tweet_impact_df : DataFrame = self.analysis_results.copy()
        tweet_impact_df.columns = [dayhour_column_name, tweet_volume_column_name]

        self.logger.debug('Converted TweetCreationTimeAnalyzer results into a Pandas DataFrame')

        return tweet_impact_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'black',
            x_axis_label : str = 'Hour',
            y_axis_label : str = 'Tweets',
            title : str = 'Tweet volume per hour',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the TweetCreationTimeAnalyzer results into a figure.

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
            The figure containing the results of the TweetCreationTimeAnalyzer.
        """
        self.logger.debug('Converting tweet creation time analysis results to image')

        fig = self.visualizer.create_line_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'dayhour',
            y_axis_column_name = 'tweet_volume',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted tweet creation time analysis results to image')

        return fig
