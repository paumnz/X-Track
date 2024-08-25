"""
Module to implement the LIWC analysis functionality of XTRACK's engine.
"""


import logging
import re
from collections import Counter
from typing import Any, Dict, List, Tuple

import liwc
from matplotlib.figure import Figure
from pandas import DataFrame
from tqdm.auto import tqdm

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector


class LIWCAnalyzer(Analyzer):
    """
    Class to implement the LIWC analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            liwc_dict_filepath : str,
            log_level: int = logging.INFO,
        ) -> None:
        """
        Constructor method for the LIWCAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            liwc_dict_filepath (str): the path to the LIWC dictionary file.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.liwc_parse, _ = liwc.load_token_parser(liwc_dict_filepath)
        self.liwc_dict_filepath = liwc_dict_filepath


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the LIWCAnalyzer. """
        return """
            SELECT liwc_category, frequency, liwc_dict
            FROM liwc_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                liwc_dict = %(liwc_dict)s
        """


    def __retrieve_tweets_without_liwc(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with no LIWC calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have no LIWC calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets without LIWC calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    LEFT JOIN liwc_2015 ON liwc_2015.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    liwc_2015.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    LEFT JOIN liwc_2015 ON liwc_2015.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s AND
                    liwc_2015.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved the tweets without LIWC calculated published on the campaign')

        return tweet_df


    def __tokenize_tweet(self, tweet_text : str):
        """
        Private method to tokenize a given tweet.
        """
        for match in re.finditer(r'\w+', tweet_text, re.UNICODE):
            yield match.group(0)


    def __calculate_tweet_liwc_per_tweet(self, tweet_id : int, tweet_text : str) -> Tuple[int, float, float, float]:
        """
        Private method to calculate the LIWC of a given tweet found in the given campaign and hashtags.

        Args:
            tweet_id (int): the identifier of the tweet whose LIWC will be computed.
            tweet_text (str): the tweet text to compute the LIWC.

        Returns:
            A tuple (tweet_id, positive, negative, neutral) with the probability of each LIWC type for the given tweet.
        """
        self.logger.debug(f'Calculating the LIWC of the tweets published on the campaign')

        tweet_tokens = self.__tokenize_tweet(tweet_text)
        liwc_category_counts = Counter(category for token in tweet_tokens for category in self.liwc_parse(token))

        liwc_results : Tuple[int, ...] = (
            tweet_id,
            liwc_category_counts['pronoun'],
            liwc_category_counts['ppron'],
            liwc_category_counts['i'],
            liwc_category_counts['we'],
            liwc_category_counts['you'],
            liwc_category_counts['shehe'],
            liwc_category_counts['they'],
            liwc_category_counts['ipron'],
            liwc_category_counts['article'],
            liwc_category_counts['prep'],
            liwc_category_counts['auxverb'],
            liwc_category_counts['adverb'],
            liwc_category_counts['conj'],
            liwc_category_counts['negate'],
            liwc_category_counts['othergram'],
            liwc_category_counts['verb'],
            liwc_category_counts['adj'],
            liwc_category_counts['compare'],
            liwc_category_counts['interrog'],
            liwc_category_counts['number'],
            liwc_category_counts['quant'],
            liwc_category_counts['affect'],
            liwc_category_counts['posemo'],
            liwc_category_counts['negemo'],
            liwc_category_counts['anx'],
            liwc_category_counts['anger'],
            liwc_category_counts['sad'],
            liwc_category_counts['social'],
            liwc_category_counts['family'],
            liwc_category_counts['friend'],
            liwc_category_counts['female'],
            liwc_category_counts['male'],
            liwc_category_counts['cogproc'],
            liwc_category_counts['insight'],
            liwc_category_counts['cause'],
            liwc_category_counts['discrep'],
            liwc_category_counts['tentat'],
            liwc_category_counts['certain'],
            liwc_category_counts['differ'],
            liwc_category_counts['percept'],
            liwc_category_counts['see'],
            liwc_category_counts['hear'],
            liwc_category_counts['feel'],
            liwc_category_counts['bio'],
            liwc_category_counts['body'],
            liwc_category_counts['health'],
            liwc_category_counts['sexual'],
            liwc_category_counts['ingest'],
            liwc_category_counts['drives'],
            liwc_category_counts['affiliation'],
            liwc_category_counts['achieve'],
            liwc_category_counts['power'],
            liwc_category_counts['reward'],
            liwc_category_counts['risk'],
            liwc_category_counts['timeorient'],
            liwc_category_counts['focuspast'],
            liwc_category_counts['focuspresent'],
            liwc_category_counts['focusfuture'],
            liwc_category_counts['relativ'],
            liwc_category_counts['motion'],
            liwc_category_counts['space'],
            liwc_category_counts['time'],
            liwc_category_counts['persconc'],
            liwc_category_counts['work'],
            liwc_category_counts['leisure'],
            liwc_category_counts['home'],
            liwc_category_counts['money'],
            liwc_category_counts['relig'],
            liwc_category_counts['death'],
            liwc_category_counts['informal'],
            liwc_category_counts['swear'],
            liwc_category_counts['netspeak'],
            liwc_category_counts['assent'],
            liwc_category_counts['nonflu'],
            liwc_category_counts['filler'],
            liwc_category_counts['funct'],
        )

        self.logger.debug(f'Calculated the LIWC of the tweets published on the campaign')

        return liwc_results


    def __calculate_tweet_liwc_all_tweets(self, tweet_df : DataFrame) -> DataFrame:
        """
        Private method to calculate the LIWC of the tweets found in the given campaign and hashtags.

        Args:
            tweet_df (DataFrame): the Pandas DataFrame containing the tweets whose LIWC must be computed.

        Returns:
            A Pandas DataFrame containing the calculated LIWC for each tweet in the given campaigns and hashtags.
        """
        self.logger.debug(f'Calculating the LIWC of the tweets published on the campaign')

        liwc_data : List[Tuple[int, ...]] = []

        tqdm_bar = tqdm(range(len(tweet_df)), desc = 'Calculating tweet LIWC')

        for _, row in tweet_df.iterrows():
            liwc_data.append(self.__calculate_tweet_liwc_per_tweet(row['tweet_id'], row['tweet_text']))
            tqdm_bar.update(1)

        self.logger.debug(f'Calculated the LIWC of the tweets published on the campaign')

        return DataFrame(
            data = liwc_data,
            columns =  [
                'pronoun',
                'ppron',
                'i',
                'we',
                'you',
                'shehe',
                'they',
                'ipron',
                'article',
                'prep',
                'auxverb',
                'adverb',
                'conj',
                'negate',
                'othergram',
                'verb',
                'adj',
                'compare',
                'interrog',
                'number',
                'quant',
                'affect',
                'posemo',
                'negemo',
                'anx',
                'anger',
                'sad',
                'social',
                'family',
                'friend',
                'female',
                'male',
                'cogproc',
                'insight',
                'cause',
                'discrep',
                'tentat',
                'certain',
                'differ',
                'percept',
                'see',
                'hear',
                'feel',
                'bio',
                'body',
                'health',
                'sexual',
                'ingest',
                'drives',
                'affiliation',
                'achieve',
                'power',
                'reward',
                'risk',
                'timeorient',
                'focuspast',
                'focuspresent',
                'focusfuture',
                'relativ',
                'motion',
                'space',
                'time',
                'persconc',
                'work',
                'leisure',
                'home',
                'money',
                'relig',
                'death',
                'informal',
                'swear',
                'netspeak',
                'assent',
                'nonflu',
                'filler',
                'funct'
            ]
        )


    def __setup_liwc_calculation(self, hashtags) -> None:
        """
        Private method to calculate the LIWC of the given campaigns and hashtags (if provided).

        Args:
            hashtags: the hashtags with which to filter the activity (if any).
        """
        self.logger.debug(f'Calculating tweet LIWC on tweets published during the given campaigns and hashtags')

        # Step 1: Retrieving tweets with no sentiment computed in the given campaigns and hashtags
        tweets_df = self.__retrieve_tweets_without_liwc(hashtags)

        # Step 2: Calculating tweet LIWC
        liwc_df : DataFrame = self.__calculate_tweet_liwc_all_tweets(tweets_df)

        # Step 3: Uploading results to database
        self.db_connector.store_table_to_sql(liwc_df, 'liwc_2015')

        self.logger.debug(f'Calculated LIWC on tweets published during the given campaigns and hashtags')


    def __retrieve_tweets_with_liwc(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with LIWC calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have LIWC calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets with LIWC calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT
                    AVG(pronoun) AS pronoun,
                    AVG(ppron) AS ppron,
                    AVG(i) AS i,
                    AVG(we) AS we,
                    AVG(you) AS you,
                    AVG(shehe) AS shehe,
                    AVG(they) AS they,
                    AVG(ipron) AS ipron,
                    AVG(article) AS article,
                    AVG(prep) AS prep,
                    AVG(auxverb) AS auxverb,
                    AVG(adverb) AS adverb,
                    AVG(conj) AS conj,
                    AVG(negate) AS negate,
                    AVG(othergram) AS othergram,
                    AVG(verb) AS verb,
                    AVG(adj) AS adj,
                    AVG(compare) AS compare,
                    AVG(interrog) AS interrog,
                    AVG(number) AS number,
                    AVG(quant) AS quant,
                    AVG(affect) AS affect,
                    AVG(posemo) AS posemo,
                    AVG(negemo) AS negemo,
                    AVG(anx) AS anx,
                    AVG(anger) AS anger,
                    AVG(sad) AS sad,
                    AVG(social) AS social,
                    AVG(family) AS family,
                    AVG(friend) AS friend,
                    AVG(female) AS female,
                    AVG(male) AS male,
                    AVG(cogproc) AS cogproc,
                    AVG(insight) AS insight,
                    AVG(cause) AS cause,
                    AVG(discrep) AS discrep,
                    AVG(tentat) AS tentat,
                    AVG(certain) AS certain,
                    AVG(differ) AS differ,
                    AVG(percept) AS percept,
                    AVG(see) AS see,
                    AVG(hear) AS hear,
                    AVG(feel) AS feel,
                    AVG(bio) AS bio,
                    AVG(body) AS body,
                    AVG(health) AS health,
                    AVG(sexual) AS sexual,
                    AVG(ingest) AS ingest,
                    AVG(drives) AS drives,
                    AVG(affiliation) AS affiliation,
                    AVG(achieve) AS achieve,
                    AVG(power) AS power,
                    AVG(reward) AS reward,
                    AVG(risk) AS risk,
                    AVG(timeorient) AS timeorient,
                    AVG(focuspast) AS focuspast,
                    AVG(focuspresent) AS focuspresent,
                    AVG(focusfuture) AS focusfuture,
                    AVG(relativ) AS relativ,
                    AVG(motion) AS motion,
                    AVG(space) AS space,
                    AVG(time) AS time,
                    AVG(persconc) AS persconc,
                    AVG(work) AS work,
                    AVG(leisure) AS leisure,
                    AVG(home) AS home,
                    AVG(money) AS money,
                    AVG(relig) AS relig,
                    AVG(death) AS death,
                    AVG(informal) AS informal,
                    AVG(swear) AS swear,
                    AVG(netspeak) AS netspeak,
                    AVG(assent) AS assent,
                    AVG(nonflu) AS nonflu,
                    AVG(filler) AS filler,
                    AVG(funct) AS funct
                FROM tweet
                    INNER JOIN liwc_2015 ON liwc_2015.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT
                    AVG(pronoun) AS pronoun,
                    AVG(ppron) AS ppron,
                    AVG(i) AS i,
                    AVG(we) AS we,
                    AVG(you) AS you,
                    AVG(shehe) AS shehe,
                    AVG(they) AS they,
                    AVG(ipron) AS ipron,
                    AVG(article) AS article,
                    AVG(prep) AS prep,
                    AVG(auxverb) AS auxverb,
                    AVG(adverb) AS adverb,
                    AVG(conj) AS conj,
                    AVG(negate) AS negate,
                    AVG(othergram) AS othergram,
                    AVG(verb) AS verb,
                    AVG(adj) AS adj,
                    AVG(compare) AS compare,
                    AVG(interrog) AS interrog,
                    AVG(number) AS number,
                    AVG(quant) AS quant,
                    AVG(affect) AS affect,
                    AVG(posemo) AS posemo,
                    AVG(negemo) AS negemo,
                    AVG(anx) AS anx,
                    AVG(anger) AS anger,
                    AVG(sad) AS sad,
                    AVG(social) AS social,
                    AVG(family) AS family,
                    AVG(friend) AS friend,
                    AVG(female) AS female,
                    AVG(male) AS male,
                    AVG(cogproc) AS cogproc,
                    AVG(insight) AS insight,
                    AVG(cause) AS cause,
                    AVG(discrep) AS discrep,
                    AVG(tentat) AS tentat,
                    AVG(certain) AS certain,
                    AVG(differ) AS differ,
                    AVG(percept) AS percept,
                    AVG(see) AS see,
                    AVG(hear) AS hear,
                    AVG(feel) AS feel,
                    AVG(bio) AS bio,
                    AVG(body) AS body,
                    AVG(health) AS health,
                    AVG(sexual) AS sexual,
                    AVG(ingest) AS ingest,
                    AVG(drives) AS drives,
                    AVG(affiliation) AS affiliation,
                    AVG(achieve) AS achieve,
                    AVG(power) AS power,
                    AVG(reward) AS reward,
                    AVG(risk) AS risk,
                    AVG(timeorient) AS timeorient,
                    AVG(focuspast) AS focuspast,
                    AVG(focuspresent) AS focuspresent,
                    AVG(focusfuture) AS focusfuture,
                    AVG(relativ) AS relativ,
                    AVG(motion) AS motion,
                    AVG(space) AS space,
                    AVG(time) AS time,
                    AVG(persconc) AS persconc,
                    AVG(work) AS work,
                    AVG(leisure) AS leisure,
                    AVG(home) AS home,
                    AVG(money) AS money,
                    AVG(relig) AS relig,
                    AVG(death) AS death,
                    AVG(informal) AS informal,
                    AVG(swear) AS swear,
                    AVG(netspeak) AS netspeak,
                    AVG(assent) AS assent,
                    AVG(nonflu) AS nonflu,
                    AVG(filler) AS filler,
                    AVG(funct) AS funct
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    INNER JOIN liwc_2015 ON liwc_2015.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)
        tweet_df = tweet_df.transpose().reset_index()
        tweet_df.columns = ['liwc_category', 'frequency']

        tweet_df = tweet_df.sort_values(by = 'frequency', ascending = False)

        self.logger.debug(f'Retrieved the tweets with LIWC calculated published on the campaign')

        return tweet_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Method to carry out LIWC analysis in the given campaign/s of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results into the database.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The average LIWC category usage of the given campaigns and hashtags (if provided).
        """

        # Step 1: Calculating LIWC categories
        self.logger.debug('Setting up the LIWC of tweets of the given campaigns and hashtags')

        self.__setup_liwc_calculation(hashtags)

        self.logger.debug('Finished setting up the LIWC of tweets of the given campaigns and hashtags')

        # Step 2: Calculating average LIWC usage
        self.logger.debug('Retrieving average LIWC of tweets of the given campaigns and hashtags')

        self.analysis_results : DataFrame = self.__retrieve_tweets_with_liwc(hashtags)

        # Step 3: Storing the results
        liwc_df = self.analysis_results.copy()
        liwc_df['campaign_analysis_id'] = campaign_analysis_id
        liwc_df['liwc_dict'] = self.liwc_dict_filepath
        liwc_df = liwc_df[['campaign_analysis_id', 'liwc_category', 'frequency', 'liwc_dict']]
        self.db_connector.store_table_to_sql(liwc_df, 'liwc_analysis_results', 'append')

        self.logger.debug('Retrieved average LIWC of tweets of the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the LIWC usage in the tweets of the given campaign.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing LIWCAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A DataFrame describing the usage of each LIWC category in the tweets of the given campaign.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            category_column_name : str = 'liwc_category',
            frequency_column_name : str = 'frequency'
        ) -> DataFrame:
        """
        Method to convert the LIWCAnalyzer results to a Pandas DataFrame.

        Args:
            category_column_name: the name of the column holding the LIWC category analyzed.
            frequency_column_name: the name of the column holding the average frequency of each category across all campaign tweets.

        Returns:
            A Pandas DataFrame with the LIWCAnalyzer results.
        """
        self.logger.debug('Converting LIWCAnalyzer results into a Pandas DataFrame')

        tweet_sentiment_df : DataFrame = self.analysis_results.copy()
        tweet_sentiment_df.columns = [
            category_column_name,
            frequency_column_name
        ]

        self.logger.debug('Converted LIWCAnalyzer results into a Pandas DataFrame')

        return tweet_sentiment_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'LIWC Categories',
            y_axis_label : str = 'Average frequency',
            title : str = 'Average LIWC category usage per tweet',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the LIWCAnalyzer results into a figure.

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
            The figure containing the results of the LIWCAnalyzer.
        """
        self.logger.debug('Converting LIWC analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'liwc_category',
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

        self.logger.debug('Converted LIWC analysis results to image')

        return fig
