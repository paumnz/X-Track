"""
Module to implement the user tweet activity analysis functionality of XTRACK's engine.
"""


from typing import Any, List, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class UserTweetActivityAnalyzer(Analyzer):
    """
    Class to implement the user tweet activity analysis functionality of XTRACK's engine.
    """


    def __retrieve_most_active_users(self, top_k : int, hashtags : Tuple[str, ...]) -> DataFrame:
        """
        Method to retrieve the most active users on the given campaigns and hashtags.

        Args:
            top_k: the number of most active users to be retrieved.
            hashtags: the hashtags with which to filter user tweet activity (if any).

        Returns:
            The Pandas DataFrame containing the top-K most active users on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving {top_k} most active users')

        query = """
            SELECT COALESCE(user.username, user.user_id) AS user, COUNT(tweet.id) AS frequency 
            FROM tweet
                INNER JOIN user ON tweet.author_id = user.id
                LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s AND
                (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            GROUP BY user
            ORDER BY frequency DESC
            LIMIT %(top_k)s;
        """

        activity_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns': tuple(self.campaigns),
                'hashtags': hashtags if hashtags is not None else (hashtags, ),
                'top_k': top_k
            }
        )

        self.logger.debug(f'Retrieved {top_k} most active users')

        return activity_df


    def __format_analysis_results(
            self,
            analysis_df : DataFrame
        ) -> Tuple[Tuple[str, int], ...]:
        """
        Private method to format the results of the analysis.

        Args:
            analysis_df: the Pandas DataFrame containing the results of the analysis performed on most active users.

        Returns:
            A tuple containing tuples (user, activity) representing the top-K most active users retrieved.
        """
        self.logger.debug('Formatting user tweet activity analysis results')

        analysis_results : List[Tuple[str, int]] = list()

        for _, row in analysis_df.iterrows():
            analysis_results.append((row['user'], row['frequency']))

        self.logger.debug('Formatted user tweet activity analysis results')

        return tuple(analysis_results)


    def analyze(self, top_k : int, hashtags : Tuple[str, ...] | None = None) -> Tuple[Any, ...]:
        """
        Method to carry out the user tweet activity analysis of the XTRACK's engine.

        Args:
            top_k: the number of most active users to be retrieved.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The top_k most active users on the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating top-{top_k} most active users')

        # Step 1: Retrieving the Pandas DataFrame with the most active users
        activity_df = self.__retrieve_most_active_users(top_k, hashtags)

        # Step 2: Formatting the results
        self.analysis_results : Tuple[Tuple[Any, int], ...] = self.__format_analysis_results(activity_df)

        self.logger.debug(f'Calculated top-{top_k} most active users')

        return self.analysis_results


    def to_pandas_dataframe(self, user_column_name : str = 'user', user_activity_column_name : str = 'num_tweets') -> DataFrame:
        """
        Method to convert the UserTweetActivityAnalyzer results to a Pandas DataFrame.

        Args:
            user_column_name: the name of the column holding the users.
            user_activity_column_name: the name of the column containing the number of tweets of the user.

        Returns:
            A Pandas DataFrame with the UserTweetActivityAnalyzer results.
        """
        self.logger.debug('Converting UserTweetActivityAnalyzer results into a Pandas DataFrame')

        influence_df = DataFrame(data = self.analysis_results, columns = [user_column_name, user_activity_column_name])

        self.logger.debug('Converted UserTweetActivityAnalyzer results into a Pandas DataFrame')

        return influence_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Users',
            y_axis_label : str = 'Number of tweets',
            title : str = 'Most active users',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the UserTweetActivityAnalyzer results into a figure.

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
            The figure containing the results of the UserTweetActivityAnalyzer.
        """
        self.logger.debug('Converting user tweet activity analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'user',
            y_axis_column_name = 'num_tweets',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted user tweet activity analysis results to image')

        return fig
