"""
Module to implement the user tweet impact analysis functionality of XTRACK's engine.
"""


from typing import Any, Dict, List, Literal, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError


class TweetImpactAnalyzer(Analyzer):
    """
    Class to implement the user tweet impact analysis functionality of XTRACK's engine.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the TweetImpactAnalyzer. """
        return """
            SELECT user, interactions
            FROM user_tweet_impact_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                tweet_impact_mode = %(mode)s
        """


    def __retrieve_users_with_highest_impact(
            self,
            top_k : int,
            hashtags : Tuple[str, ...],
            mode : Literal['rt+like', 'reply+quote'] = 'rt+like'
        ) -> DataFrame:
        """
        Method to retrieve the top-K users with highest impact on their tweets measured by retweets or replies.

        Args:
            top_k: the number of users with highest impact to be retrieved.
            hashtags: the hashtags with which to filter user tweet impact (if any).
            mode: the mode with which most impactful users will be retrieved.

        Returns:
            The Pandas DataFrame containing the top-K users with highest impact on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving {top_k} users with highest impact (mode = {mode})')

        match mode:
            case 'rt+like':
                query = """
                    SELECT COALESCE(user.username, user.user_id) AS user, AVG(tweet_metrics.retweet_count + like_count) AS interactions
                    FROM tweet
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                        INNER JOIN user ON tweet.author_id = user.id
                        LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                        LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                    WHERE tweet.campaign IN %(campaigns)s AND
                        (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s) AND
                        tweet.text NOT LIKE 'RT %%'
                    GROUP BY user
                    ORDER BY interactions DESC
                    LIMIT %(top_k)s;
                """
            case 'reply+quote':
                query = """
                    SELECT COALESCE(user.username, user.user_id) AS user, AVG(tweet_metrics.quote_count + reply_count) AS interactions
                    FROM tweet
                        INNER JOIN tweet_metrics ON tweet_metrics.tweet_id = tweet.id
                        INNER JOIN user ON tweet.author_id = user.id
                        LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                        LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
                    WHERE tweet.campaign IN %(campaigns)s AND
                        (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s) AND
                        tweet.text NOT LIKE 'RT %%'
                    GROUP BY user
                    ORDER BY interactions DESC
                    LIMIT %(top_k)s;
                """
            case _:
                raise IllegalAnalysisConfigError(f'Illegal mode configuration for TweetImpactAnalyzer: {mode}')

        activity_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns': tuple(self.campaigns),
                'hashtags': hashtags if hashtags is not None else (hashtags, ),
                'top_k': top_k
            }
        )

        self.logger.debug(f'Retrieved {top_k} users with highest impact (mode = {mode})')

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
        self.logger.debug('Formatting user tweet impact analysis results')

        analysis_results : List[Tuple[str, int]] = list()

        for _, row in analysis_df.iterrows():
            analysis_results.append((row['user'], row['interactions']))

        self.logger.debug('Formatted user tweet impact analysis results')

        return tuple(analysis_results)


    def build_new_results(
            self,
            campaign_analysis_id : int,
            top_k : int,
            hashtags : Tuple[str, ...] | None = None,
            mode : Literal['rt+like', 'reply+quote'] = 'rt+like'
        ) -> Tuple[Any, ...]:
        """
        Method to carry out the user tweet impact analysis of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results into the database.
            top_k: the number of users with highest impact to be retrieved.
            hashtags: the hashtags with which to filter the activity (if any).
            mode: the mode with which most impactful users will be retrieved.

        Returns:
            The top_k most users with highest impact on the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating top-{top_k} users with highest impact mode = {mode}')

        # Step 1: Retrieving the Pandas DataFrame with the most active users
        activity_df = self.__retrieve_users_with_highest_impact(top_k, hashtags, mode)

        # Step 2: Storing the results into the database
        activity_df['campaign_analysis_id'] = campaign_analysis_id
        activity_df['tweet_impact_mode'] = mode
        activity_df = activity_df[['campaign_analysis_id', 'user', 'interactions', 'tweet_impact_mode']]
        self.db_connector.store_table_to_sql(activity_df, 'user_tweet_impact_analysis_results', 'append')

        # Step 3: Formatting the results
        self.analysis_results : Tuple[Tuple[Any, int], ...] = self.__format_analysis_results(activity_df)

        self.logger.debug(f'Calculated top-{top_k} users with highest impact mode = {mode}')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the most users with highest tweet impact of the given campaigns and hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing TweetImpactAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple of tuples (user, interactions) describing the top-K users with highest tweet impact.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, self.__format_analysis_results, new_computation_kwargs)


    def to_pandas_dataframe(self, user_column_name : str = 'user', interactions_column_name : str = 'interactions') -> DataFrame:
        """
        Method to convert the TweetImpactAnalyzer results to a Pandas DataFrame.

        Args:
            user_column_name: the name of the column holding the users.
            interactions_column_name: the name of the column containing the interactions received by the user.

        Returns:
            A Pandas DataFrame with the TweetImpactAnalyzer results.
        """
        self.logger.debug('Converting TweetImpactAnalyzer results into a Pandas DataFrame')

        influence_df = DataFrame(data = self.analysis_results, columns = [user_column_name, interactions_column_name])

        self.logger.debug('Converted TweetImpactAnalyzer results into a Pandas DataFrame')

        return influence_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Users',
            y_axis_label : str = 'Generated interactions',
            title : str = 'Users with highest impact',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the TweetImpactAnalyzer results into a figure.

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
            The figure containing the results of the TweetImpactAnalyzer.
        """
        self.logger.debug('Converting user tweet impact analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'user',
            y_axis_column_name = 'interactions',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted user tweet impact analysis results to image')

        return fig
