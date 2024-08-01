"""
Module to analyze the motto employed in the Twitter conversation.
"""


from typing import Any, Dict, Tuple, List, Literal

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError


class MottoAnalyzer(Analyzer):
    """
    A class to implement a motto analyzer to extract most impactful motto on Twitter's conversation.
    """


    def __analyze_most_employed_mottos(self, top_k : int = 10) -> DataFrame:
        """
        Method to carry out motto analysis on the given campaigns for all mottos (no sentiment filter applied).

        Args:
            top_k: the number of top-used mottos to be retrieved as a result.

        Returns:
            A Pandas DataFrame containing the results of a query with the most employed mottos in the given campaigns.
        """
        self.logger.debug(f'Retrieving {top_k} most employed mottos (all sentiments)')

        # Step 1: Query definition
        query = """
        SELECT hashtag.hashtag AS motto, COUNT(tweet.id) AS frequency 
        FROM tweet 
            INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id 
            INNER JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id 
        WHERE tweet.campaign IN %(campaigns)s
        GROUP BY hashtag.hashtag 
        ORDER BY frequency DESC 
        LIMIT %(top_k)s;
        """

        # Step 2: Query execution
        mottos_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns' : self.campaigns,
                'top_k' : top_k
            }
        )

        self.logger.debug(f'Retrieved {top_k} most employed mottos (all sentiments)')

        return mottos_df


    def __analyze_most_employed_negative_mottos(self, top_k : int = 10) -> DataFrame:
        """
        Method to carry out motto analysis on the given campaigns for negative sentiment mottos.

        Args:
            top_k: the number of top-used negative mottos to be retrieved as a result.

        Returns:
            A Pandas DataFrame containing the results of a query with the most employed negative mottos in the given campaigns.
        """
        self.logger.debug(f'Retrieving {top_k} most employed negative mottos')

        # Step 1: Query definition
        query = """
        SELECT hashtag.hashtag AS motto, COUNT(tweet.id) AS frequency, AVG(sentiment.negative) AS negative 
        FROM tweet 
            INNER JOIN sentiment ON sentiment.tweet_id = tweet.id 
            INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id 
            INNER JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id 
        WHERE tweet.campaign IN %(campaigns)s
        GROUP BY hashtag.hashtag 
        ORDER BY negative DESC 
        LIMIT %(top_k)s;
        """

        # Step 2: Query execution
        mottos_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns' : self.campaigns,
                'top_k' : top_k
            }
        )

        self.logger.debug(f'Retrieved {top_k} most employed negative mottos')

        return mottos_df


    def __analyze_most_employed_positive_mottos(self, top_k : int = 10) -> DataFrame:
        """
        Method to carry out motto analysis on the given campaigns for positive sentiment mottos.

        Args:
            top_k: the number of top-used positive mottos to be retrieved as a result.

        Returns:
            A Pandas DataFrame containing the results of a query with the most employed positive mottos in the given campaigns.
        """
        self.logger.debug(f'Retrieving {top_k} most employed positive mottos')

        # Step 1: Query definition
        query = """
        SELECT hashtag.hashtag AS motto, COUNT(tweet.id) AS frequency, AVG(sentiment.positive) AS positive 
        FROM tweet 
            INNER JOIN sentiment ON sentiment.tweet_id = tweet.id 
            INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id 
            INNER JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id 
        WHERE tweet.campaign IN %(campaigns)s
        GROUP BY hashtag.hashtag 
        ORDER BY positive DESC 
        LIMIT %(top_k)s;
        """

        # Step 2: Query execution
        mottos_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns' : tuple(self.campaigns),
                'top_k' : top_k
            }
        )

        self.logger.debug(f'Retrieved {top_k} most employed positive mottos')

        return mottos_df


    def __format_analysis_results(self, mottos_df : DataFrame) -> Tuple[Tuple[str, int], ...]:
        """
        Method to format the DataFrame containing most employed mottos as a tuple of tuples (motto, usage count).

        Args:
            mottos_df (DataFrame): the Pandas DataFrame containing the most employed mottos and their usage.

        Returns:
            A tuple of tuples describing the most employed mottos and their absolute frequencies.
        """
        self.logger.debug('Formatting mottos analysis results')

        analysis_results : List[Tuple[str, int]] = list()

        for _, row in mottos_df.iterrows():
            analysis_results.append((row['motto'], row['frequency']))

        self.logger.debug('Formatted mottos analysis results')

        return tuple(analysis_results)


    def analyze(
            self,
            sentiment : Literal['both', 'negative', 'positive'],
            top_k : int = 10,
        ) -> Tuple[Tuple[str, int], ...]:
        """
        Method to carry out motto analysis on the given campaigns.

        Args:
            sentiment: the sentiment to be used for filtering the mottos' analysis.
            top_k: the number of top-used mottos to be retrieved as a result.

        Returns:
            A tuple of tuples (motto, usage count) including the top_k most used mottos in the given sentiment.
        """
        self.logger.info(f'Analyzing top-{top_k} most employed mottos (sentiment = {sentiment})')

        # Step 1: Retrieving the Pandas DataFrame with most employed mottos
        match sentiment:
            case 'both':
                mottos_df = self.__analyze_most_employed_mottos(top_k)
            case 'negative':
                mottos_df = self.__analyze_most_employed_negative_mottos(top_k)
            case 'positive':
                mottos_df = self.__analyze_most_employed_positive_mottos(top_k)
            case _:
                raise IllegalAnalysisConfigError(f'Illegal sentiment configuration for MottoAnalyzer: {sentiment}')

        # Step 2: Formatting the results
        self.analysis_results = self.__format_analysis_results(mottos_df)

        self.logger.info(f'Analyzed top-{top_k} most employed mottos (sentiment = {sentiment})')

        return self.analysis_results


    def to_pandas_dataframe(self, motto_column_name : str = 'motto', frequency_column_name : str = 'frequency') -> DataFrame:
        """
        Method to transform the motto analysis results into a Pandas DataFrame.

        Args:
            motto_column_name: the name of the column of the Pandas DataFrame containing the motto.
            frequency_column_name: the name of the column of the Pandas DataFrame containing the frequency of the motto.

        Returns:
            A Pandas DataFrame containing the 
        """
        self.logger.debug('Converting MottoAnalyzer results into a Pandas DataFrame')

        mottos_df = DataFrame(data = self.analysis_results, columns = [motto_column_name, frequency_column_name])

        self.logger.debug('Converted MottoAnalyzer results into a Pandas DataFrame')

        return mottos_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Mottos',
            y_axis_label : str = 'Frequency',
            title : str = 'Most employed mottos',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the motto analysis results into a figure.

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
            The figure containing the results of the MottoAnalyzer.
        """
        self.logger.debug('Converting motto analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'motto',
            y_axis_column_name = 'frequency',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted motto analysis results to image')

        return fig
