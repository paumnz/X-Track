"""
Module to implement the network metric analysis functionality of XTRACK's engine.
"""


from collections.abc import Iterable
from datetime import date, timedelta
from logging import INFO
from typing import Any, Dict, List, Literal, Tuple

import networkx as nx
import pandas as pd
from matplotlib.figure import Figure
from tqdm.auto import tqdm

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.errors.config_errors import IllegalAnalysisConfigError
from xtrack_engine.network_analysis.network_generation.network_generator import NetworkGenerator
from xtrack_engine.network_analysis.network_generation.reply_network_generator import ReplyNetworkGenerator
from xtrack_engine.network_analysis.network_generation.retweet_network_generator import RetweetNetworkGenerator
from xtrack_engine.network_analysis.network_metric_calculation.network_metric_calculator import NetworkMetricCalculator

class NetworkMetricAnalyzer(Analyzer):
    """
    Class to implement the network metric analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = INFO
        ) -> None:
        """
        Constructor method for the NetworkMetricAnalyzer class.

        Args:
            campaigns (str | Tuple[str, ...]): the campaign/s to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.retweet_network_generator = RetweetNetworkGenerator(campaigns, db_connector, log_level)
        self.reply_network_generator = ReplyNetworkGenerator(campaigns, db_connector, log_level)


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the NetworkMetricAnalyzer. """
        return """
            SELECT network_metric, value, date
            FROM network_metric_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                network_type = %(network_type)s AND
                network_metric IN %(network_metrics)s
        """


    def __select_network_generator_for_analysis(self, network_type : Literal['retweet', 'reply']) -> NetworkGenerator:
        """
        Private method to select the network generator for the network metric analysis.

        Args:
            network_type: the network type to be created for the analysis, either a retweet or a reply network.

        Returns:
            A NetworkGenerator capable of creating the required networks.
        """
        self.logger.debug('Selecting the network generator to be used')

        match network_type:
            case 'retweet':
                network_generator = self.retweet_network_generator
            case 'reply':
                network_generator = self.reply_network_generator
            case _:
                raise IllegalAnalysisConfigError(f'Illegal network type configuration for NetworkMetricAnalyzer: {network_type}')

        self.logger.debug('Selected the network generator to be used')

        return network_generator


    def __apply_network_metric(self, networks_per_window : Tuple[nx.DiGraph], metric_name : str) -> Tuple[float | int, ...]:
        """
        Private method to apply a network metric on each of the extracted networks per time window.

        Args:
            networks_per_window: the networks extracted per time window.
            metric_name: the name of the metric to be executed.
        """
        self.logger.debug(f'Calculating network metric "{metric_name}" on all extracted networks per window')

        metric_results : List[float | int] = []

        metric_calculator = NetworkMetricCalculator(self.logger.level)

        for network in tqdm(networks_per_window, desc = f'Calculating {metric_name} on all networks'):
            match metric_name:
                case NetworkMetricCalculator.DENSITY_METRIC:
                    metric_result = metric_calculator.calculate_network_density(network)
                case NetworkMetricCalculator.IN_DEGREE_METRIC:
                    metric_result = metric_calculator.calculate_average_in_degree(network)
                case NetworkMetricCalculator.OUT_DEGREE_METRIC:
                    metric_result = metric_calculator.calculate_average_out_degree(network)
                case NetworkMetricCalculator.EFFICIENCY_METRIC:
                    metric_result = metric_calculator.calculate_network_efficiency(network)
                case NetworkMetricCalculator.EIGENVECTOR_CENTRALITY_METRIC:
                    metric_result = metric_calculator.calculate_average_eigenvector_centrality(network)
                case NetworkMetricCalculator.MODULARITY_METRIC:
                    metric_result = metric_calculator.calculate_network_modularity(network)
                case NetworkMetricCalculator.DIAMETER_METRIC:
                    metric_result = metric_calculator.calculate_network_diameter(network)
                case NetworkMetricCalculator.CLUSTERING_COEFFICIENT_METRIC:
                    metric_result = metric_calculator.calculate_average_clustering_coefficient(network)
                case NetworkMetricCalculator.NODE_NUMBER_METRIC:
                    metric_result = metric_calculator.calculate_network_node_number(network)
                case NetworkMetricCalculator.EDGE_NUMBER_METRIC:
                    metric_result = metric_calculator.calculate_network_edge_number(network)
                case _:
                    raise IllegalAnalysisConfigError(f'Illegal metric name configuration for NetworkMetricAnalyzer: {metric_name}')

            metric_results.append(metric_result)

        self.logger.debug(f'Calculated network metric "{metric_name}" on all extracted networks per window')

        return tuple(metric_results)


    def __aply_all_network_metrics(
            self,
            networks_per_time_window : Tuple[nx.DiGraph],
            metric_names : Tuple[str, ...],
            first_date : date,
            last_date : date,
            window_size : int
        ) -> pd.DataFrame:
        """
        Private method to apply all network metrics on the extracted networks per time window.

        Args:
            networks_per_time_window: the extracted networks for each of the studied time windows.
            metric_names: the names of the network metrics to calculate per network.
            first_date: the first date to study.
            last_date: the date up to which network relationships will be extracted.
            window_size: the size of the time windows to study.

        Returns:
            A Pandas DataFrame containing as many columns as metric names and as many rows as time windows.
        """
        self.logger.debug('Calculating network metrics on the extracted networks per time window')

        metric_data : Dict[str, Tuple[Any, ...]]  = {}
        date_column : List[date] = []

        # Step 1: Calculating the date column of the resulting Pandas DataFrame
        while first_date < last_date:
            date_column.append(first_date)
            first_date += timedelta(days = window_size)

        metric_data['date'] = tuple(date_column)

        # Step 2: Calculating metric results
        for metric_name in metric_names:
            metric_data[metric_name] = self.__apply_network_metric(networks_per_time_window, metric_name)

        results_df = pd.DataFrame(data = metric_data)

        self.logger.debug('Calculated network metrics on the extracted networks per time window')

        return results_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            network_metrics : str | Tuple[str, ...],
            hashtags : Tuple[str, ...] | None = None,
            network_type : Literal['retweet', 'reply'] = 'retweet',
            first_date : date = None,
            last_date : date = None,
            window_size_in_days : int = 1,
        ) -> pd.DataFrame:
        """
        Method to carry out the network metric analysis over time of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier to be used for storing data into the database.
            network_metrics: the network metric/s to be computed.
            hashtags: the hashtags with which to filter the activity (if any).
            network_type: the type of network to be used, either a retweet or a reply network.
            first_date: the first date to be considered for analyzing network metrics.
            last_date: the last date considered for analyzing network metrics.
            window_size_in_days: the size in days of the time windows to study.

        Returns:
            The network metric analysis over time of the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Executing network metric analysis on the given campaigns and hashtags')

        # Step 1: Setting up the network metrics to be computed as a tuple of strings
        network_metrics = network_metrics if isinstance(network_metrics, Iterable) else (network_metrics, )

        # Step 2: Setting up the network generator to be used and the time interval to cover
        network_generator = self.__select_network_generator_for_analysis(network_type)

        # Step 3: Network extraction per time window
        networks_per_window = network_generator.generate_networks_per_time_window(window_size_in_days, hashtags, first_date, last_date)

        first_date = network_generator.min_date
        last_date = network_generator.max_date

        # Step 4: Execution of network metrics
        self.analysis_results : pd.DataFrame = self.__aply_all_network_metrics(networks_per_window, network_metrics, first_date, last_date, window_size_in_days)

        # Step 5: Storing results into the database
        network_metric_df = self.analysis_results.copy()
        network_metric_df = network_metric_df.melt(id_vars = ['date'], var_name = 'network_metric', value_name = 'value')
        network_metric_df['campaign_analysis_id'] = campaign_analysis_id
        network_metric_df['network_type'] = network_type
        network_metric_df = network_metric_df[['campaign_analysis_id', 'network_metric', 'value', 'date', 'network_type']]
        self.db_connector.store_table_to_sql(network_metric_df, 'network_metric_analysis_results', 'append')

        self.logger.debug(f'Executed network metric analysis on the given campaigns and hashtags')

        return self.analysis_results


    def __format_analysis_results(self, network_metric_df : pd.DataFrame) -> pd.DataFrame:
        """
        Method to format the analysis pre-computed results to the format expected by the front-end.

        Args:
            network_metric_df (DataFrame): the Pandas DataFrame containing the pre-computed results of the analyzer.

        Returns:
            A Pandas DataFrame with the expected format by the front-end.
        """
        self.logger.debug('Formatting the pre-computed network metric results')

        formatted_df = network_metric_df.pivot(index='date', columns='network_metric', values='value').reset_index()

        self.logger.debug('Formatted the pre-computed network metric results')

        return formatted_df


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the network metrics during the given campaign/hashtags.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing NetworkMetricAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A DataFrame containing the network metrics measurement for the given campaign/hashtags.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, self.__format_analysis_results, new_computation_kwargs)


    def to_pandas_dataframe(self) -> pd.DataFrame:
        """
        Method to convert the NetworkMetricAnalyzer results to a Pandas DataFrame.

        Returns:
            A Pandas DataFrame with the NetworkMetricAnalyzer results.
        """
        self.logger.debug('Converting NetworkMetricAnalyzer results into a Pandas DataFrame')

        metrics_df : pd.DataFrame = self.analysis_results.copy()
 
        self.logger.debug('Converted NetworkMetricAnalyzer results into a Pandas DataFrame')

        return metrics_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            colors : Tuple[str, ...] = None,
            x_axis_label : str = 'Date',
            y_axis_label : str = 'Network metrics',
            title : str = 'Network metric evolution over time',
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the NetworkMetricAnalyzer results into a figure.

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
            The figure containing the results of the NetworkMetricAnalyzer.
        """
        self.logger.debug('Converting network metric analysis results to image')

        data : pd.DataFrame = self.to_pandas_dataframe()
        metric_names : List[str] = list(data.columns)
        metric_names.remove('date')

        fig = self.visualizer.create_multi_line_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'date',
            y_axis_column_names = metric_names,
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

        self.logger.debug('Converted network metric analysis results to image')

        return fig
