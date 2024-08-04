"""
Module to implement the reply network extraction functionality of XTRACK framework's engine.
"""


from datetime import date
from typing import Tuple

from pandas import DataFrame

from xtrack_engine.network_analysis.network_generation.network_generator import NetworkGenerator


class ReplyNetworkGenerator(NetworkGenerator):
    """
    A class to implement the reply network extraction functionality of XTrack's engine.
    """


    def _generate_network_dataframe(
            self,
            first_date : date,
            last_date : date,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Private method to generate a Pandas DataFrame with reply relationships from the given campaign and hashtags (if provided).

        Args:
            first_date (date): the minimum date from which user relationships will be considered.
            last_date (date): the maximum date up to which user relationships will be considered.
            hashtags (Tuple[str, ...] | None): an optional parameter containing hashtags to be used for filtering tweet retrieval.

        Returns:
            A pandas DataFrame with the reply relationships between users and their strengths.
        """
        self.logger.debug(f'Retrieving reply network from {first_date} to {last_date}')

        if hashtags is None:
            query = """
                SELECT
                    COALESCE(u_rter.username, u_rter.user_id) AS rter,
                    COALESCE(u_rted.username, u_rted.user_id) AS rted,
                    COUNT(*) AS weight
                FROM
                    reply rt
                    INNER JOIN tweet t_rter ON t_rter.id = rt.tweet_id
                    INNER JOIN tweet t_rted ON t_rted.id = rt.reply_to
                    INNER JOIN user u_rter ON u_rter.id = t_rter.author_id
                    INNER JOIN user u_rted ON u_rted.id = t_rted.author_id
                WHERE
                    (t_rter.campaign IN %(campaigns)s OR t_rted.campaign IN %(campaigns)s) AND
                    t_rter.created_at >= %(first_date)s AND
                    t_rter.created_at < %(last_date)s
                GROUP BY rter, rted
            """
            params = {'campaigns' : tuple(self.campaigns), 'first_date' : first_date, 'last_date' : last_date}
        else:
            query = """
                SELECT
                    COALESCE(u_rter.username, u_rter.user_id) AS rter,
                    COALESCE(u_rted.username, u_rted.user_id) AS rted,
                    COUNT(*) AS weight
                FROM
                    reply rt
                    INNER JOIN tweet t_rter ON t_rter.id = rt.tweet_id
                    INNER JOIN tweet t_rted ON t_rted.id = rt.reply_to
                    INNER JOIN user u_rter ON u_rter.id = t_rter.author_id
                    INNER JOIN user u_rted ON u_rted.id = t_rted.author_id
                    INNER JOIN hashtagt_tweet ht_rter ON ht_rter.tweet_id = t_rter.id
                    INNER JOIN hashtag h_rter ON h_rter.id = ht_rter.hashtag_id
                    INNER JOIN hashtagt_tweet ht_rted ON ht_rted.tweet_id = t_rted.id
                    INNER JOIN hashtag h_rted ON h_rted.id = ht_rted.hashtag_id
                WHERE
                    (t_rter.campaign IN %(campaigns)s OR t_rted.campaign IN %(campaigns)s) AND
                    t_rter.created_at >= %(first_date)s AND
                    t_rter.created_at < %(last_date)s AND
                    (h_rter.hashtag IN %(hashtags)s OR h_rted.hashtag IN %(hashtags)s)
                GROUP BY rter, rted
            """
            params = {'campaigns' : tuple(self.campaigns), 'first_date' : first_date, 'last_date' : last_date, 'hashtags' : hashtags}

        network_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved reply network from {first_date} to {last_date}')

        return network_df
