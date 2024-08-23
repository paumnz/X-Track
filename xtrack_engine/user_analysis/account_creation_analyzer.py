"""
Module to implement the account creation analysis functionality of XTRACK's engine.
"""


from typing import Any, Dict, Tuple

import networkx as nx
from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer


class AccountCreationAnalyzer(Analyzer):
    """
    Class to implement the account creation analysis functionality of XTRACK's engine.
    """


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the DomainAnalyzer. """
        return """
            SELECT month, accounts
            FROM user_account_creation_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


    def __retrieve_user_accounts_per_month(
            self,
            hashtags : Tuple[str, ...],
        ) -> DataFrame:
        """
        Method to retrieve the months with more created accounts filtered by hashtag usage (if provided).

        Args:
            hashtags: the hashtags with which to filter user account creation (if provided).

        Returns:
            The Pandas DataFrame containing the number of created accounts per month.
        """
        self.logger.debug(f'Retrieving the number of created accounts per month')

        query = """
        SELECT DISTINCT user.user_id AS user, user.creation_date AS created_at
        FROM user
            INNER JOIN tweet ON tweet.author_id = user.id
            LEFT JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
            LEFT JOIN hashtag ON hashtagt_tweet.hashtag_id = hashtag.id
        WHERE tweet.campaign IN %(campaigns)s AND
            user.creation_date IS NOT NULL AND
            (%(hashtags)s IS NULL OR hashtag.hashtag IN %(hashtags)s);
        """

        account_df = self.db_connector.retrieve_table_from_sql(
            query,
            {
                'campaigns': tuple(self.campaigns),
                'hashtags': hashtags if hashtags is not None else (hashtags, ),
            }
        )

        # Processing the Pandas DataFrame to obtain the count of accounts per month
        account_df['created_at'] = account_df['created_at'].astype(str).apply(lambda row: row[:7])
        account_df = account_df.groupby(by = account_df['created_at'])['user'].count().sort_index(ascending=True).to_frame().reset_index()
        account_df.columns = ['month', 'accounts']

        self.logger.debug(f'Retrieving the number of created accounts per month')

        return account_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None,
        ) -> DataFrame:
        """
        Method to carry out the account creation analysis of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store results in the database.
            hashtags: the hashtags with which to filter the created user accounts (if any).

        Returns:
            The user accounts created per month.
        """
        self.logger.debug(f'Calculating created user accounts per month')

        # Step 1: Retrieving the Pandas DataFrame with the number of accounts created per month
        activity_df = self.__retrieve_user_accounts_per_month(hashtags)

        # Step 2: Storing the results in the database
        activity_df['campaign_analysis_id'] = campaign_analysis_id
        activity_df = activity_df[['campaign_analysis_id', 'month', 'accounts']]
        self.db_connector.store_table_to_sql(activity_df, 'user_account_creation_analysis_results', 'append')

        # Step 3: Formatting the results
        self.analysis_results : DataFrame = activity_df

        self.logger.debug(f'Calculating created user accounts per month')

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
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(self, month_column_name : str = 'month', created_user_accounts_column_name : str = 'accounts') -> DataFrame:
        """
        Method to convert the AccountCreationAnalyzer results to a Pandas DataFrame.

        Args:
            month_column_name: the name of the column holding the month.
            created_user_accounts_column_name: the name of the column containing the number of accounts created in that month.

        Returns:
            A Pandas DataFrame with the AccountCreationAnalyzer results.
        """
        self.logger.debug('Converting AccountCreationAnalyzer results into a Pandas DataFrame')

        account_creation_df = self.analysis_results.copy()
        account_creation_df.columns = [month_column_name, created_user_accounts_column_name]

        self.logger.debug('Converted AccountCreationAnalyzer results into a Pandas DataFrame')

        return account_creation_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'black',
            x_axis_label : str = 'Months',
            y_axis_label : str = 'Created accounts',
            title : str = 'Created accounts per month',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the AccountCreationAnalyzer results into a figure.

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
            The figure containing the results of the AccountCreationAnalyzer.
        """
        self.logger.debug('Converting account creation analysis results to image')

        fig = self.visualizer.create_line_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'month',
            y_axis_column_name = 'accounts',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted account creation analysis results to image')

        return fig
