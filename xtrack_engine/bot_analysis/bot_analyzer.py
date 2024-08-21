"""
Module to implement the bot detection functionality of XTRACK's engine.
"""


import configparser
import logging
from datetime import datetime
from typing import Any, Dict, List, Tuple

import botometer
from matplotlib.figure import Figure
from pandas import DataFrame

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector


class BotAnalyzer(Analyzer):
    """
    Class to implement the bot detection functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            config_filepath : str,
            log_level: int = logging.INFO
        ) -> None:
        """
        Constructor method for the BotAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        botometer_configs : Dict[str, Any] = self.__read_botometer_config_file(config_filepath)
        self.rapid_api_key : str = botometer_configs['rapid_api_key']


    def __read_botometer_config_file(self, botometer_config_filepath : str) -> Dict[str, Any]:
        """
        Private method to read the Botometer X API configurations from a given configuration file.

        Args:
            botometer_config_filepath (str): the path to the Botometer X configuration file.

        Returns:
            A dictionary that contains the database configurations read from the file.
        """
        self.logger.debug('Loading botometer configurations')

        db_config_dict : Dict[str, Any] = {}

        config_parser = configparser.ConfigParser()
        config_parser.read(botometer_config_filepath)

        db_config_dict['rapid_api_key'] = config_parser.get('botometer', 'rapid_api_key')

        self.logger.debug('Loaded botometer configurations')

        return db_config_dict


    def __retrieve_active_users_without_bot_analysis(
            self,
            top_k : int | None = None,
            hashtags : Tuple[str, ...] | None = None
        ) -> Dict[str, int]:
        """
        Private method to retrieve users active without performed bot analysis on the given campaigns and hashtags.

        Args:
            top_k: the maximum number of users to analyze. If not specified, all users will be analyzed.
            hashtags: the hashtags with which to filter user activity (if any).

        Returns:
            A dictionary twitter id<-> user id of users with no bot analysis performed and who are active in the given campaign and hashtags.
        """
        self.logger.debug('Retrieving users without bot analysis performed')

        top_k_param : str = f'LIMIT {top_k}' if top_k is not None else ''

        if hashtags is None:
            query = f"""
                SELECT u.user_id AS twitter_user_id, u.id AS db_user_id
                FROM
                    tweet t
                    INNER JOIN user u ON u.id = t.author_id
                    LEFT JOIN user_botometer ub ON ub.user_id = u.id
                WHERE
                    t.campaign IN %(campaigns)s AND
                    ub.user_id IS NULL
                {top_k_param}
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k_param}
        else:
            query = f"""
                SELECT u.user_id AS twitter_user_id, u.id AS db_user_id
                FROM
                    tweet t
                    INNER JOIN user u ON u.id = t.author_id
                    INNER JOIN hashtagt_tweet ht ON ht.tweet_id = t.id
                    INNER JOIN hashtag h ON h.id = ht.hashtag_id
                    LEFT JOIN user_botometer ub ON ub.user_id = u.id
                WHERE
                    t.campaign IN %(campaigns)s AND
                    h.hashtag IN %(hashtags)s AND
                    ub.user_id IS NULL
                {top_k_param}
            """
            params = {'campaigns': tuple(self.campaigns), 'top_k' : top_k_param, 'hashtags' : hashtags}

        bots_df : DataFrame = self.db_connector.retrieve_table_from_sql(query, params)
        users_to_analyze : Dict[str, int] = bots_df.set_index('twitter_user_id')['db_user_id'].to_dict()

        self.logger.debug('Retrieved users without bot analysis performed')

        return users_to_analyze


    def __apply_bot_analysis(self, users_to_analyze : Dict[str, int]) -> DataFrame:
        """
        Method to carry out bot analysis on the active users of the given campaigns and hashtags.

        Args:
            users_to_analyze: a dictionary with information related to the users to identify (Twitter user id and DB user id).

        Returns:
            A Pandas DataFrame containing one row per user indicating the bot score of the user and whether it is a bot (1) or not (0).
        """
        self.logger.debug('Calling Botometer X API to determine whether given users are bots or not')

        botometer_x = botometer.BotometerX(rapidapi_key = self.rapid_api_key)
        botometer_results = botometer_x.get_botscores_in_batch(user_ids = list(users_to_analyze.keys()))

        user_bot_data : List[Tuple[Any, ...]] = [
            (
                users_to_analyze[str(user_bot_data['user_id'])],
                user_bot_data['bot_score'],
                user_bot_data['bot_score'] > 0.5,
                datetime.strptime(user_bot_data['timestamp'], '%a, %d %b %Y %H:%M:%S %Z')
            )
            for user_bot_data in botometer_results
        ]

        user_bot_df : DataFrame = DataFrame(data = user_bot_data, columns = ['user_id', 'bot_score', 'bot', 'retrieved_at'])

        self.logger.debug('Called Botometer X API to determine whether given users are bots or not')

        self.logger.debug('Uploading results to the database')

        self.db_connector.store_table_to_sql(user_bot_df, 'user_botometer', 'append')

        self.logger.debug('Uploading results to the database')

        return user_bot_df


    def __retrieve_bot_analysis(self, hashtags : Tuple[str, ...] | None = None) -> DataFrame:
        """
        Private method to retrieve the results of the performed bot analysis on the given campaigns and hashtags.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            A Pandas DataFrame containing the analyzed active users on the given campaigns and hashtags.
        """
        self.logger.debug('Retrieving bot analysis results')

        if hashtags is None:
            query = """
                SELECT DISTINCT u.user_id, ub.bot_score, ub.bot
                FROM 
                    tweet t
                    INNER JOIN user u ON u.id = t.author_id
                    INNER JOIN user_botometer ub ON ub.user_id = u.id
                WHERE
                    t.campaign IN %(campaigns)s;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT DISTINCT u.user_id, ub.bot_score, ub.bot
                FROM 
                    tweet t
                    INNER JOIN user u ON u.id = t.author_id
                    INNER JOIN user_botometer ub ON ub.user_id = u.id
                    INNER JOIN hashtagt_tweet ht ON ht.tweet_id = t.id
                    INNER JOIN hashtag h ON h.id = ht.hashtag_id
                WHERE
                    t.campaign IN %(campaigns)s AND
                    h.hashtag IN %(hashtags)s;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}


        bots_df : DataFrame = self.db_connector.retrieve_table_from_sql(query, params)
        analysis_df : DataFrame = DataFrame(
            data = {
                'bot' : ['No bot', 'Bot'],
                'frequency' : [len(bots_df[bots_df['bot'] == 0]), len(bots_df[bots_df['bot'] == 1])]
            }
        )

        self.logger.debug('Retrieved bot analysis results')

        return analysis_df


    def analyze(
            self,
            top_k : int | None = None,
            hashtags : Tuple[str, ...] | None = None,
        ) -> DataFrame:
        """
        Method to carry out the bot detection and analysis on active users of the XTRACK's engine.

        Args:
            top_k: the maximum number of users on which the bot detection tool will be applied. All users are analyzed by default.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            A Pandas DataFrame containing the analyzed users and whether they are bots.
        """
        self.logger.debug(f'Applying bot detection on the given campaigns and hashtags')

        # Step 1: Retrieving users that need to be analyzed
        users_to_analyze : Dict[str, int] = self.__retrieve_active_users_without_bot_analysis(top_k, hashtags)

        # Step 2: Applying bot detection (storing results in the database)
        if len(users_to_analyze) > 0:
            self.__apply_bot_analysis(users_to_analyze)

        # Step 3: Retrieving bot analysis
        self.analysis_results : DataFrame = self.__retrieve_bot_analysis(hashtags)

        self.logger.debug(f'Applied bot detection on the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            bot_column_name : str = 'bot',
            frequency_column_name : str = 'frequency'
        ) -> DataFrame:
        """
        Method to convert the BotAnalyzer results to a Pandas DataFrame.

        Args:
            bot_column_name: the column holding the bot label being analyzed (0 stands for non-bot and 1 stands for bot).
            frequency_column_name: the name of the column holding the number of users of the given bot label (0 or 1).

        Returns:
            A Pandas DataFrame with the BotAnalyzer results.
        """
        self.logger.debug('Converting BotAnalyzer results into a Pandas DataFrame')

        tweet_language_df : DataFrame = self.analysis_results.copy()
        tweet_language_df.columns = [bot_column_name, frequency_column_name]

        self.logger.debug('Converted BotAnalyzer results into a Pandas DataFrame')

        return tweet_language_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            title : str = 'Distribution of bots on Twitter conversation',
        ) -> Figure:
        """
        Method to convert the BotAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            The figure containing the results of the BotAnalyzer.
        """
        self.logger.debug('Converting bot analysis results to image')

        fig = self.visualizer.create_pie_plot(
            data = self.to_pandas_dataframe(),
            category_column_name = 'bot',
            value_column_name = 'frequency',
            width = width,
            height = height,
            title = title,
        )

        self.logger.debug('Converted bot analysis results to image')

        return fig
