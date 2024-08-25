"""
Module to implement the tweet language analysis functionality of XTRACK's engine.
"""


from typing import Any, Dict, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class TweetLanguageAnalyzer(Analyzer):
    """
    Class to implement the tweet language analysis functionality of XTRACK's engine.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the TweetLanguageAnalyzer. """
        return """
            SELECT language, tweet_volume
            FROM tweet_language_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


    def __retrieve_tweet_volume_per_lang(self, top_k : int = 5, hashtags = None) -> DataFrame:
        """
        Method to retrieve the total number of tweets created per language on the given campaigns and hashtags.

        Args:
            top_k: the number of most impactful tweets to be retrieved.
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the total number of tweets created per hour on the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving top-{top_k} languages with more tweets')

        if hashtags is None:
            query = """
                SELECT lang AS language, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                WHERE
                    tweet.lang != 'und' AND
                    tweet.campaign IN %(campaigns)s
                GROUP BY language
                ORDER BY tweet_volume DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k}
        else:
            query = """
                SELECT lang AS language, COUNT(tweet.id) AS tweet_volume
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.lang != 'und'
                    AND tweet.campaign IN %(campaigns)s
                    AND hashtag.hashtag IN %(hashtags)s
                GROUP BY language
                ORDER BY tweet_volume DESC
                LIMIT %(top_k)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags, 'top_k' : top_k}

        tweets_per_lang_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved top-{top_k} languages with more tweets')

        return tweets_per_lang_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            top_k : int = 5,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Method to carry out the tweet language analysis of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The duplicated tweets of the given campaigns and hashtags (if any).
        """
        self.logger.debug(f'Calculating tweets per language on the given campaigns and hashtags')

        # Step 1: Calculate the most employed languages
        self.analysis_results : DataFrame = self.__retrieve_tweet_volume_per_lang(top_k, hashtags)

        # Step 2: Store the results into the database
        language_df = self.analysis_results.copy()
        language_df['campaign_analysis_id'] = campaign_analysis_id
        language_df = language_df[['campaign_analysis_id', 'language', 'tweet_volume']]
        self.db_connector.store_table_to_sql(language_df, 'tweet_language_analysis_results', 'append')

        self.logger.debug(f'Calculated tweets per language on the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the most employed languages in the given campaigns/hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing TweetLanguageAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple of tuples (user, interactions) describing the top-K most employed languages in the given campaign/hashtags.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            language_column_name : str = 'language',
            tweet_volume_column_name : str = 'tweet_volume'
        ) -> DataFrame:
        """
        Method to convert the LanguageAnalyzer results to a Pandas DataFrame.

        Args:
            dayhour_column_name: the column holding the day-hour measured.
            tweet_volume_column_name: the name of the column holding the volume of tweets of that language.

        Returns:
            A Pandas DataFrame with the LanguageAnalyzer results.
        """
        self.logger.debug('Converting LanguageAnalyzer results into a Pandas DataFrame')

        tweet_language_df : DataFrame = self.analysis_results.copy()
        tweet_language_df.columns = [language_column_name, tweet_volume_column_name]

        self.logger.debug('Converted LanguageAnalyzer results into a Pandas DataFrame')

        return tweet_language_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            title : str = 'Tweet volume per hour',
        ) -> Figure:
        """
        Method to convert the LanguageAnalyzer results into a figure.

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
            The figure containing the results of the LanguageAnalyzer.
        """
        self.logger.debug('Converting tweet language analysis results to image')

        fig = self.visualizer.create_pie_plot(
            data = self.to_pandas_dataframe(),
            category_column_name = 'language',
            value_column_name = 'tweet_volume',
            width = width,
            height = height,
            title = title,
        )

        self.logger.debug('Converted tweet language analysis results to image')

        return fig
