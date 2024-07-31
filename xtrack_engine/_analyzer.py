"""
Module to implement an abstract analyzer of XTRACK-engine.
"""


import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Tuple

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


    @abstractmethod
    def analyze(self, *args : Tuple[Any, ...], **kwargs : Dict[str, Any]) -> Any:
        """
        Method to analyze a specific aspect of the given campaign.

        Args:
            *args: the arguments to be used for carrying out the analysis (if any).
            **kwargs: the keyword arguments to be used for carrying out the analysis (if any).
        """


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
