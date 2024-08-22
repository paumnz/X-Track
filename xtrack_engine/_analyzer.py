"""
Module to implement an abstract analyzer of XTRACK-engine.
"""


import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame, ExcelWriter

from xtrack_engine._utils.loggable_entity import LoggableEntity
from xtrack_engine.database_connection.db_connector import DBConnector
from xtrack_engine.visualization.visualizer import Visualizer


class Analyzer(ABC, LoggableEntity):
    """
    A class to implement an abstract analyzer to be used within the XTRACK framework's engine.
    """


    def __init__(self, campaigns : str | Tuple[str, ...], db_connector : DBConnector, log_level : int = logging.INFO) -> None:
        """
        Constructor method for the `Analyzer` class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(log_level)

        self.campaigns : Tuple[str, ...] = campaigns if type(campaigns) == tuple else (campaigns, )
        self.db_connector : DBConnector = db_connector
        self.analysis_results : Any = None
        self.visualizer : Visualizer = Visualizer(log_level)


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the Analyzer. """
        raise NotImplementedError('Feature not yet implemented')


    def check_for_pre_computed_results(
            self,
            query_params : Dict[str, Any],
            formatting_function : Callable[[DataFrame], Any] | None = None
        ) -> bool:
        """
        Method that checks if there exists a previously computed result for the queried campaign/hashtags.

        Args:
            query_params (Dict[str, Any]): the query parameters to be used.
            formatting_function (Callable[[DataFrame], Any] | None): the function to format the resulting DataFrame (if any).

        Returns:
            A flag indicating if pre-computed results are available.
        """
        self.logger.debug(f'Checking for pre-computed analysis results')

        analysis_df = self.db_connector.retrieve_table_from_sql(
            query_text = self.pre_computed_results_query,
            query_params = query_params
        )

        found_precomputed_results = len(analysis_df) > 0

        if found_precomputed_results and formatting_function is not None:
            self.analysis_results = formatting_function(analysis_df)

        self.logger.debug(f'Checked for pre-computed analysis results')

        return found_precomputed_results


    @abstractmethod
    def build_new_results(self, campaign_analysis_id : int, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> Any:
        """
        Method to carry out an analysis on the given campaigns/hashtags from scratch.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            *args: the arguments to be used for carrying out the analysis (if any).
            **kwargs: the keyword arguments to be used for carrying out the analysis (if any).

        Returns:
            The result of the analysis.
        """


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            pre_computation_formatting_function : Callable[[DataFrame], Any] | None = None,
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze a specific aspect of the given campaign.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing pre-computed results.
            pre_computation_formatting_function: the function that formats the pre-computed output into the analysis results (if any).
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.
        """
        is_precomputed = self.check_for_pre_computed_results(
            query_params = {'campaign_analysis_id' : campaign_analysis_id, **pre_computation_query_params},
            formatting_function = pre_computation_formatting_function
        )

        if not is_precomputed:
            self.analysis_results = self.build_new_results(campaign_analysis_id = campaign_analysis_id, **new_computation_kwargs)

        return self.analysis_results


    @abstractmethod
    def to_pandas_dataframe(self, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> DataFrame:
        """
        Method to transform the results of the analysis into a Pandas DataFrame.

        Args:
            *args: the arguments to be used for generating the Pandas DataFrame (if any).
            **kwargs: the keyword arguments to be used for generating the Pandas DataFrame (if any).

        Returns:
            A Pandas DataFrame containing the results of the performed analysis.
        """


    @abstractmethod
    def to_image(self, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> Figure:
        """
        Method to transform the results of the analysis into a Pandas DataFrame.

        Returns:
            A Pandas DataFrame containing the results of the performed analysis.
        """


    def to_csv(self, output_path : str, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> None:
        """
        Method to store the results of the analysis into a CSV file.

        Args:
            output_path: the path where the CSV file with the results will be stored.
            *args: the arguments to be used for generating the Pandas DataFrame (if any).
            **kwargs: the keyword arguments to be used for generating the Pandas DataFrame (if any).
        """
        results_df = self.to_pandas_dataframe(*args, **kwargs)
        results_df.to_csv(output_path, index = False, header = True)


    def to_excel(self, output_path : str, sheet_name : str, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> None:
        """
        Method to store the results of the analysis into a CSV file.

        Args:
            output_path: the path where the Excel file with the results will be stored.
            sheet_name: the name of the excel sheet where the results will be stored.
            *args: the arguments to be used for generating the Pandas DataFrame (if any).
            **kwargs: the keyword arguments to be used for generating the Pandas DataFrame (if any).
        """
        results_df = self.to_pandas_dataframe(*args, **kwargs)

        write_mode = 'a' if Path(output_path).is_file() else 'w'

        with ExcelWriter(output_path, engine = 'openpyxl', mode = write_mode) as writer:
            results_df.to_excel(writer, sheet_name = sheet_name, index = False, header = True)


    def to_png(self, output_path : str, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> None:
        """
        Method to store the results of the analysis into a PNG image.

        Args:
            output_path: the path where the PNG file with the results will be stored.
            *args: the arguments to be used for generating the Pandas DataFrame (if any).
            **kwargs: the keyword arguments to be used for generating the Pandas DataFrame (if any).
        """
        analysis_figure = self.to_image(*args, **kwargs)
        analysis_figure.savefig(output_path)
