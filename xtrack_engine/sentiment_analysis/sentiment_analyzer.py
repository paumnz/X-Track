"""
Module to implement the sentiment analysis functionality of XTRACK's engine.
"""


import logging
from typing import Dict, List, Tuple

from matplotlib.figure import Figure
from pandas import DataFrame
from pysentimiento import create_analyzer
from tqdm.auto import tqdm

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector


class SentimentAnalyzer(Analyzer):
    """
    Class to implement the sentiment analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = logging.INFO,
            language : str = 'es'
        ) -> None:
        """
        Constructor method for the SentimentAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
            language (str): the language to be used for sentiment analysis.
        """
        super().__init__(campaigns, db_connector, log_level)

        self.sentiment_analyzer = create_analyzer(task = 'sentiment', lang = language)


    def __retrieve_tweets_without_sentiment(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with no sentiment calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have no sentiment calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets without sentiment calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    LEFT JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    sentiment.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT tweet.id AS tweet_id, tweet.text AS tweet_text
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    LEFT JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s AND
                    sentiment.tweet_id IS NULL;
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved the tweets without sentiment calculated published on the campaign')

        return tweet_df


    def __calculate_tweet_sentiment_per_tweet(self, tweet_id : int, tweet_text : str) -> Tuple[int, float, float, float]:
        """
        Private method to calculate the sentiment of a given tweet found in the given campaign and hashtags.

        Args:
            tweet_id (int): the identifier of the tweet whose sentiment will be computed.
            tweet_text (str): the tweet text to compute the sentiment.

        Returns:
            A tuple (tweet_id, positive, negative, neutral) with the probability of each sentiment type for the given tweet.
        """
        self.logger.debug(f'Calculating the sentiment of the tweets published on the campaign')

        tweet_sentiment : Dict[str, float] = self.sentiment_analyzer.predict(tweet_text).probas
        sentiment_results : Tuple[int, float, float, float] = (tweet_id, tweet_sentiment['POS'], tweet_sentiment['NEG'], tweet_sentiment['NEU'])

        self.logger.debug(f'Calculated the sentiment of the tweets published on the campaign')

        return sentiment_results


    def __calculate_tweet_sentiment_all_tweets(self, tweet_df : DataFrame) -> DataFrame:
        """
        Private method to calculate the sentiment of the tweets found in the given campaign and hashtags.

        Args:
            tweet_df (DataFrame): the Pandas DataFrame containing the tweets whose sentiment must be computed.

        Returns:
            A Pandas DataFrame containing the calculated sentiment for each tweet in the given campaigns and hashtags.
        """
        self.logger.debug(f'Calculating the sentiment of the tweets published on the campaign')

        sentiment_data : List[Tuple[int, float, float, float]] = []

        tqdm_bar = tqdm(range(len(tweet_df)), desc = 'Calculating tweet sentiment')

        for _, row in tweet_df.iterrows():
            sentiment_data.append(self.__calculate_tweet_sentiment_per_tweet(row['tweet_id'], row['tweet_text']))
            tqdm_bar.update(1)

        self.logger.debug(f'Calculated the sentiment of the tweets published on the campaign')

        return DataFrame(data = sentiment_data, columns = ['tweet_id', 'positive', 'negative', 'neutral'])


    def __setup_sentiment_calculation(self, hashtags) -> None:
        """
        Private method to calculate the sentiment of the given campaigns and hashtags (if provided).

        Args:
            hashtags: the hashtags with which to filter the activity (if any).
        """
        self.logger.debug(f'Calculating tweet sentiment on tweets published during the given campaigns and hashtags')

        # Step 1: Retrieving tweets with no sentiment computed in the given campaigns and hashtags
        tweets_df = self.__retrieve_tweets_without_sentiment(hashtags)

        # Step 2: Calculating tweet sentiment
        sentiment_df : DataFrame = self.__calculate_tweet_sentiment_all_tweets(tweets_df)

        # Step 3: Uploading results to database
        self.db_connector.store_table_to_sql(sentiment_df, 'sentiment')

        self.logger.debug(f'Calculated tweet sentiment on tweets published during the given campaigns and hashtags')


    def __retrieve_tweets_with_sentiment(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets with sentiment calculated of the given campaigns and filtered by hashtags if provided.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval.

        Returns:
            A Pandas DataFrame containing the tweets that have sentiment calculated in the current campaign and hashtags (if any).
        """
        self.logger.debug(f'Retrieving the tweets with sentiment calculated published on the campaign')

        if hashtags is None:
            query = """
                SELECT AVG(sentiment.positive) AS positive, AVG(sentiment.neutral) AS neutral, AVG(sentiment.negative) AS negative
                FROM tweet
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT AVG(sentiment.positive) AS positive, AVG(sentiment.neutral) AS neutral, AVG(sentiment.negative) AS negative
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                    INNER JOIN sentiment ON sentiment.tweet_id = tweet.id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}
        
        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)
        tweet_df = tweet_df.transpose().reset_index()
        tweet_df.columns = ['sentiment', 'probability']

        self.logger.debug(f'Retrieved the tweets with sentiment calculated published on the campaign')

        return tweet_df


    def analyze(self, hashtags : Tuple[str, ...] | None = None) -> DataFrame:
        """
        Method to carry out sentiment analysis in the given campaign/s of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The average probability per sentiment of the given campaigns and hashtags (if provided).
        """
        self.logger.debug('Setting up the sentiment of tweets of the given campaigns and hashtags')

        self.__setup_sentiment_calculation(hashtags)

        self.logger.debug('Finished setting up the sentiment of tweets of the given campaigns and hashtags')

        self.logger.debug('Retrieving average sentiment of tweets of the given campaigns and hashtags')

        self.analysis_results : DataFrame = self.__retrieve_tweets_with_sentiment(hashtags)

        self.logger.debug('Retrieved average sentiment of tweets of the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(
            self,
            sentiment_column_name : str = 'sentiment',
            average_probability_column_name : str = 'probability'
        ) -> DataFrame:
        """
        Method to convert the SentimentAnalyzer results to a Pandas DataFrame.

        Args:
            sentiment_column_name: the name of the column holding the sentiment being analyzed.
            average_probability_column_name: the name of the column holding the average probability of each sentiment across all campaign tweets.

        Returns:
            A Pandas DataFrame with the SentimentAnalyzer results.
        """
        self.logger.debug('Converting SentimentAnalyzer results into a Pandas DataFrame')

        tweet_sentiment_df : DataFrame = self.analysis_results.copy()
        tweet_sentiment_df.columns = [
            sentiment_column_name,
            average_probability_column_name
        ]

        self.logger.debug('Converted SentimentAnalyzer results into a Pandas DataFrame')

        return tweet_sentiment_df


    def to_image(
            self,
            width : float = 10,
            height : float = 7,
            color : str = 'lightblue',
            x_axis_label : str = 'Sentiment',
            y_axis_label : str = 'Average sentiment probability per tweet',
            title : str = 'Average sentiment distribution',
            grid : bool = True,
            x_ticks_rotation : float = 0
        ) -> Figure:
        """
        Method to convert the SentimentAnalyzer results into a figure.

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
            The figure containing the results of the SentimentAnalyzer.
        """
        self.logger.debug('Converting sentiment analysis results to image')

        fig = self.visualizer.create_bar_plot(
            data = self.to_pandas_dataframe(),
            x_axis_column_name = 'sentiment',
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

        self.logger.debug('Converted sentiment analysis results to image')

        return fig
