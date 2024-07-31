"""
Module to implement a database connector for the `engine` module of `X-TRACK`.
"""


import configparser
import logging
from typing import Any, Dict, Literal, Tuple

import pandas as pd
from sqlalchemy import Engine, create_engine

from xtrack_engine._utils.loggable_entity import LoggableEntity


class DBConnector(LoggableEntity):
    """
    A class to implement a connector to a database for inserting and/or retrieving information.
    """


    def __init__(
            self,
            db_config_filepath : str,
            log_level : int = logging.INFO
        ) -> None:
        """
            Constructor method for the `DBConnector` class.

            Args:
                db_config_filepath (str): the filepath containing database configurations.
                log_level (int): the logging level to be used for filtering logs.
        """
        super().__init__(log_level)

        self.engine : Engine = None
        self.conn_params : Dict[str, Any] = self.__read_db_config_file(db_config_filepath)


    def __read_db_config_file(self, db_config_filepath : str) -> Dict[str, Any]:
        """
        Private method to read database configurations from a given configuration file.

        Args:
            db_config_filepath (str): the path to the database configuration file.

        Returns:
            A dictionary that contains the database configurations read from the file.
        """
        self.logger.debug('Loading database configurations')

        db_config_dict : Dict[str, Any] = {}

        config_parser = configparser.ConfigParser()
        config_parser.read(db_config_filepath)

        db_config_dict['dialect'] = config_parser.get('database', 'dialect')
        db_config_dict['driver'] = config_parser.get('database', 'driver')
        db_config_dict['host'] = config_parser.get('database', 'host')
        db_config_dict['port'] = config_parser.get('database', 'port')
        db_config_dict['username'] = config_parser.get('database', 'username')
        db_config_dict['password'] = config_parser.get('database', 'password')
        db_config_dict['db_name'] = config_parser.get('database', 'db_name')

        self.logger.debug('Loaded database configurations')

        return db_config_dict


    def __connect(self) -> None:
        """
        Private method to setup the connection to the database.
        """
        if self.engine is None:
            try:
                self.logger.debug('Connecting to the database')
                self.engine = create_engine(
                    f"{self.conn_params['dialect']}+{self.conn_params['driver']}://"
                    f"{self.conn_params['username']}:{self.conn_params['password']}@"
                    f"{self.conn_params['host']}:{self.conn_params['port']}/{self.conn_params['db_name']}"
                )
                self.logger.debug('Connected to the database')
            except Exception as exc:
                raise ConnectionError(f'[{self.__class__.__name__}] Cannot set up connection with DB: {exc}')


    def __disconnect(self) -> None:
        """
        Private method to close the connection to the database.
        """
        self.logger.debug('Closing the database connection')

        if self.engine:
            self.engine.dispose()
            self.engine = None
            self.logger.debug("Database connection successfully closed.")


    def retrieve_table_from_sql(
            self,
            query_text : str,
            query_params : Dict[str, Any] | Tuple[Any, ...]
        ) -> pd.DataFrame:
        """
        Method to retrieve a table using its name and its location on a schema.

        Args:
            query_text: the query to be executed on the connected database.
            query_params: the parameters of the query (if any).

        Returns:
            A Pandas DataFrame containing the data from the specified table.
        """
        self.logger.debug(f'Executing query: {query_text}')

        # Step 1: Establishing connection to the database
        self.__connect()

        # Step 2: Retrieving the desired table
        table_df = pd.read_sql(query_text, con = self.engine, params = query_params)

        self.logger.debug(f'Executed query: {query_text}')

        # Step 3: Disconnecting from the database
        self.__disconnect()

        return table_df


    def store_table_to_sql(
            self,
            table_df : pd.DataFrame,
            table_name : str,
            if_exists_mode : Literal['append', 'replace', 'fail'] = 'append',
            schema_name : str = None
        ) -> None:
        """
        Method to store a table into the database.

        Args:
            table_df: the dataframe to be stored.
            table_name: the name of the table where data will be stored.
            schema_name: the schema where the table will be stored. If `None`, the database name will be used.
        """
        schema_name = schema_name if schema_name else self.conn_params['db_name']

        self.__connect()

        self.logger.debug(f'Storing dataframe @ {schema_name}.{table_name}')
        table_df.to_sql(
            name = table_name,
            con = self.engine,
            schema = schema_name,
            if_exists = if_exists_mode,
            index = False
        )
        self.logger.debug(f'Stored dataframe @ {schema_name}.{table_name}')

        self.__disconnect()
