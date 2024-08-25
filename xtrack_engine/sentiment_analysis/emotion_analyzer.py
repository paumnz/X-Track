"""
Module to implement the emotion analysis functionality of XTRACK's engine.
"""


import logging
from typing import Any, Dict, List, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame
from pysentimiento import create_analyzer
from tqdm.auto import tqdm

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector


class EmotionAnalyzer(Analyzer):
    """
    Class to implement the emotion analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = logging.INFO,
            language : str = 'es'
        ) -> None:
        """
        Constructor method for the EmotionAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
            language (str): the language to be used for emotion analysis.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.emotion_analyzer = create_analyzer(task = 'emotion', lang = language)
        self.language = language


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the EmotionAnalyzer. """
        return """
            SELECT emotion, probability, language
            FROM emotion_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s AND
                language = %(language)s
        """


    def __retrieve_tweets_without_emotion(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with no emotion calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have no emotion calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets without emotion calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    LEFT JOIN emotion ON emotion.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    emotion.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    LEFT JOIN emotion ON emotion.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s AND
                    emotion.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved the tweets without emotion calculated published on the campaign')

        return tweet_df


    def __calculate_tweet_emotion_per_tweet(
            self,
            tweet_id : int,
            tweet_text : str
        ) -> Tuple[int, float, float, float, float, float, float, float]:
        """
        Private method to calculate the emotion of a given tweet found in the given campaign and hashtags.

        Args:
            tweet_id (int): the identifier of the tweet whose emotion will be computed.
            tweet_text (str): the tweet text to compute the emotion.

        Returns:
            A tuple (tweet_id, anger, disgust, fear, joy, sadness, surprise, others) with the probability of each emotion for the given tweet.
        """
        self.logger.debug(f'Calculating the emotion of the tweets published on the campaign')

        tweet_emotion : Dict[str, float] = self.emotion_analyzer.predict(tweet_text).probas
        emotion_results : Tuple[int, float, float, float, float, float, float, float] = (
            tweet_id,
            tweet_emotion['anger'],
            tweet_emotion['disgust'],
            tweet_emotion['fear'],
            tweet_emotion['joy'],
            tweet_emotion['sadness'],
            tweet_emotion['surprise'],
            tweet_emotion['others'],
        )

        self.logger.debug(f'Calculated the emotion of the tweets published on the campaign')

        return emotion_results


    def __calculate_tweet_emotion_all_tweets(self, tweet_df : DataFrame) -> DataFrame:
        """
        Private method to calculate the emotion of the tweets found in the given campaign and hashtags.

        Args:
            tweet_df (DataFrame): the Pandas DataFrame containing the tweets whose emotion must be computed.

        Returns:
            A Pandas DataFrame containing the calculated emotion for each tweet in the given campaigns and hashtags.
        """
        self.logger.debug(f'Calculating the emotion of the tweets published on the campaign')

        emotion_data : List[Tuple[int, float, float, float]] = []

        tqdm_bar = tqdm(range(len(tweet_df)), desc = 'Calculating tweet emotion')

        for _, row in tweet_df.iterrows():
            emotion_data.append(self.__calculate_tweet_emotion_per_tweet(row['tweet_id'], row['tweet_text']))
            tqdm_bar.update(1)

        self.logger.debug(f'Calculated the emotion of the tweets published on the campaign')

        return DataFrame(
            data = emotion_data,
            columns = ['tweet_id', 'anger', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'others']
        )


    def __setup_emotion_calculation(self, hashtags) -> None:
        """
        Private method to calculate the emotion of the given campaigns and hashtags (if provided).

        Args:
            hashtags: the hashtags with which to filter the activity (if any).
        """
        self.logger.debug(f'Calculating tweet emotion on tweets published during the given campaigns and hashtags')

        # Step 1: Retrieving tweets with no emotion computed in the given campaigns and hashtags
        tweets_df = self.__retrieve_tweets_without_emotion(hashtags)

        # Step 2: Calculating tweet emotion
        emotion_df : DataFrame = self.__calculate_tweet_emotion_all_tweets(tweets_df)

        # Step 3: Uploading results to database
        self.db_connector.store_table_to_sql(emotion_df, 'emotion')

        self.logger.debug(f'Calculated tweet emotion on tweets published during the given campaigns and hashtags')


    def __retrieve_tweets_with_emotion(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with emotion calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have emotion calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets with emotion calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT
                    AVG(emotion.anger) AS anger,
                    AVG(emotion.disgust) AS disgust,
                    AVG(emotion.fear) AS fear,
                    AVG(emotion.joy) AS joy,
                    AVG(emotion.sadness) AS sadness,
                    AVG(emotion.surprise) AS surprise,
                    AVG(emotion.others) AS others
                FROM tweet
                    INNER JOIN emotion ON emotion.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT
                    AVG(emotion.anger) AS anger,
                    AVG(emotion.disgust) AS disgust,
                    AVG(emotion.fear) AS fear,
                    AVG(emotion.joy) AS joy,
                    AVG(emotion.sadness) AS sadness,
                    AVG(emotion.surprise) AS surprise,
                    AVG(emotion.others) AS others
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    INNER JOIN emotion ON emotion.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)
        tweet_df = tweet_df.transpose().reset_index()
        tweet_df.columns = ['emotion', 'probability']

        tweet_df = tweet_df.sort_values(by = 'probability', ascending = False)

        self.logger.debug(f'Retrieved the tweets with emotion calculated published on the campaign')

        return tweet_df


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> DataFrame:
        """
        Method to carry out emotion analysis in the given campaign/s of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store the results in the database.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The average probability per emotion of the given campaigns and hashtags (if provided).
        """

        # Step 1: Calculating emotion per tweet
        self.logger.debug('Setting up the emotion of tweets of the given campaigns and hashtags')

        self.__setup_emotion_calculation(hashtags)

        self.logger.debug('Finished setting up the emotion of tweets of the given campaigns and hashtags')

        # Step 2: Calculating average probability per emotion
        self.logger.debug('Retrieving average emotion of tweets of the given campaigns and hashtags')

        self.analysis_results : DataFrame = self.__retrieve_tweets_with_emotion(hashtags)

        # Step 3: Storing the results in the DB
        emotion_df = self.analysis_results.copy()
        emotion_df['campaign_analysis_id'] = campaign_analysis_id
        emotion_df['language'] = self.language
        emotion_df = emotion_df[['campaign_analysis_id', 'emotion', 'probability', 'language']]
        self.db_connector.store_table_to_sql(emotion_df, 'emotion_analysis_results', 'append')

        self.logger.debug('Retrieved average emotion of tweets of the given campaigns and hashtags')

        return self.analysis_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the emotion probability in the tweets of the given campaign.

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing EmotionAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A DataFrame describing the probability of each emotion in the tweets of the given campaign.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, None, new_computation_kwargs)


    def to_pandas_dataframe(
            self,
            emotion_column_name : str = 'emotion',
            average_probability_column_name : str = 'probability'
        ) -> DataFrame:
        """
        Method to convert the EmotionAnalyzer results to a Pandas DataFrame.

        Args:
            emotion_column_name: the name of the column holding the emotion being analyzed.
            average_probability_column_name: the name of the column holding the average probability of each emotion across all campaign tweets.

        Returns:
            A Pandas DataFrame with the EmotionAnalyzer results.
        """
        self.logger.debug('Converting EmotionAnalyzer results into a Pandas DataFrame')

        tweet_emotion_df : DataFrame = self.analysis_results.copy()
        tweet_emotion_df.columns = [
            emotion_column_name,
            average_probability_column_name
        ]

        self.logger.debug('Converted EmotionAnalyzer results into a Pandas DataFrame')

        return tweet_emotion_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Emotion',
            y_axis_label : str = 'Average emotion probability per tweet',
            title : str = 'Average emotion distribution',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the EmotionAnalyzer results into a figure.

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
            The figure containing the results of the EmotionAnalyzer.
        """
        self.logger.debug('Converting emotion analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'emotion',
            y_axis_column_name = 'probability',
            width = width,
            height = height,
            color = color,
            x_axis_label = x_axis_label,
            y_axis_label = y_axis_label,
            title = title,
            grid = grid,
            x_ticks_rotation = x_ticks_rotation
        )

        self.logger.debug('Converted emotion analysis results to image')

        return fig
