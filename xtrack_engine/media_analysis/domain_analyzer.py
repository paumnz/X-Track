"""
Module to implement the XTRACK framework's engine capability to analyze media outlets' domains from Twitter.
"""


from typing import Any, Dict, List, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class DomainAnalyzer(Analyzer):
    """
    A class to implement the analysis functionality of XTRACK's engine on media outlets' domains.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the DomainAnalyzer. """
        return """
            SELECT domain, frequency
            FROM media_domain_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


    def __format_analysis_results(
            self,
            analysis_df : DataFrame
        ) -> Tuple[Tuple[str, int], ...]:
        """
        Private method to format the results of the analysis.

        Args:
            analysis_df: the Pandas DataFrame containing the results of the analysis performed on most shared domains.

        Returns:
            A tuple containing tuples (domain, frequency) representing the top-K most shared domains obtained.
        """
        self.logger.debug('Formatting domain analysis results')

        analysis_results : List[Tuple[str, int]] = list()

        for _, row in analysis_df.iterrows():
            analysis_results.append((row['domain'], row['frequency']))

        self.logger.debug('Formatted domain analysis results')

        return tuple(analysis_results)


    def __analyze_most_shared_domains(
            self,
            top_k : int,
            hashtags : Tuple[str, ...] | None
        ) -> DataFrame:
        """
        Private method to analyze the most shared media outlet domains on Twitter activity.

        Args:
            top_k: the number of most shared media outlet domains to be retrieved.
            hashtags: the hashtags (if any) to be used for filtering Twitter activity when analyzing most shared media outlets.

        Returns:
            A Pandas DataFrame containing the name and frequency of the most shared media outlet domains.
        """
        self.logger.debug(f'Retrieving {top_k} most shared media outlet domains')

        query = """
        SELECT url.domain AS domain, COUNT(tweet.id) AS frequency 
            FROM tweet
            INNER JOIN url_tweet ON url_tweet.tweet_id = tweet.id
            INNER JOIN url ON url_tweet.url_id = url.id
            INNER JOIN user ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
            WHERE tweet.campaign IN %(campaigns)s
            AND (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s)
            AND url.domain NOT IN ('youtube.com','twitter.com','ift.tt','fb.me','ctt.ec','bit.ly','youtu.be',
                                   'www.youtube.com','t.me','goo.gl','t.co','buff.ly','www.facebook.com','facebook.com',
                                   'support.twitter.com','vk.ru','vk.cc','vk.com','ow.ly','instagram.com','wp.me',
                                   'www.pscp.tv','www.instagram.com','www.fiverr.com','patreon.com','rplr.co','open.spotify.com')
            GROUP BY url.domain 
            ORDER BY frequency DESC 
            LIMIT %(top_k)s
        """

        domains_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns' : tuple(self.campaigns),
                'top_k' : top_k,
                'hashtags' : hashtags if hashtags is not None else (hashtags, )
            }
        )

        self.logger.debug(f'Retrieved {top_k} most shared media outlet domains')

        return domains_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            top_k : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> Tuple[Tuple[str, int], ...]:
        """
        Method to analyze most shared media outlet domains in the Twitter conversation.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results.
            top_k: the number of "most-frequent" media outlet domains to be retrieved.
            hashtags: the hashtags with which to filter the tweets when applying the analysis.

        Returns:
            A tuple that contains tuples (domain, frequency) containing the top-K most shared media outlet domains.
        """
        self.analysis_results : Dict[str, Tuple[Tuple[str, int], ...]] = {}

        self.logger.info(f'Analyzing top-{top_k} most employed media outlet domains (hashtags = {hashtags})')

        # Step 1: Analyzing most used domains given the provided hashtags
        domains_df = self.__analyze_most_shared_domains(top_k, hashtags)

        # Step 2: Storing the results
        domains_df['campaign_analysis_id'] = campaign_analysis_id
        domains_df = domains_df[['campaign_analysis_id', 'domain', 'frequency']]
        self.db_connector.store_table_to_sql(domains_df, 'media_domain_analysis_results', 'append')

        # Step 3: Formatting the results
        self.analysis_results = self.__format_analysis_results(domains_df)

        self.logger.info(f'Analyzed top-{top_k} most employed media outlet domains (hashtags = {hashtags})')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the most employed domains per sentiment on the given campaigns and hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing DomainAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple of tuples (domain, frequency) describing the top-K most employed domains.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, self.__format_analysis_results, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            domain_column_name : str = 'domain',
            frequency_column_name : str = 'frequency'
        ) -> DataFrame:
        """
        Method to convert the media outlet domain analysis results into a Pandas DataFrame.

        Args:
            domain_column_name: the name of the column that will contain the most shared domains found.
            frequency_column_name: the name of the column that will contain the frequency of the most shared domains.

        Returns:
            A Pandas DataFrame containing the most shared domains found and their frequencies.
        """
        self.logger.debug('Converting DomainAnalyzer results into a Pandas DataFrame')

        domains_df = DataFrame(data = self.analysis_results, columns = [domain_column_name, frequency_column_name])

        self.logger.debug('Converted DomainAnalyzer results into a Pandas DataFrame')

        return domains_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Domains',
            y_axis_label : str = 'Frequency',
            title : str = 'Most shared domains',
            grid : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to convert the media outlet domain analysis results into an image.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            color: the color to be used for the barplot.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.
        """
        self.logger.debug('Converting media domain analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'domain',
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

        self.logger.debug('Converted media domain analysis results to image')

        return fig
