"""
Module to implement the word usage analysis functionality of XTRACK's engine.
"""


import logging
import re
from typing import Tuple

import plotly.graph_objects as go
from nltk.corpus import stopwords
from pandas import DataFrame
from wordcloud import WordCloud, STOPWORDS

from xtrack_engine._analyzer import Analyzer
from xtrack_engine.database_connection.db_connector import DBConnector


class WordCloudAnalyzer(Analyzer):
    """
    Class to implement the word usage analysis functionality of XTRACK's engine.
    """


    def __init__(
            self,
            campaigns: str | Tuple[str],
            db_connector: DBConnector,
            log_level: int = logging.INFO
        ) -> None:
        """
        Constructor method for the WordCloudAnalyzer class.

        Args:
            campaign (str): the campaign to be analyzed.
            db_connector (DBConnector): the database connector to be used for the analysis.
            log_level (int): the log level to be used for filtering logs in the runtime.
        """
        super().__init__(campaigns, db_connector, log_level)

        # Setting up the stopwords to be used
        self.stopwords = set(stopwords.words('spanish'))
        self.stopwords.update(set(stopwords.words('english')))
        self.stopwords.update(set(stopwords.words('arabic')))
        self.stopwords.update(set(stopwords.words('french')))


    def __preprocess_tweet(self, tweet : str) -> Tuple[str, ...]:
        """
        Preprocess the given tweet by removing URLs, numbers and other unwanted characters.

        Args:
            tweet: the tweet to be preprocessed.

        Returns:
            The tokenized and preprocessed version of the tweet.
        """
        tweet = re.sub(r'http\S+', '', tweet)
        tweet = re.sub(r'www\S+', '', tweet)
        tweet = re.sub(r'[^a-zA-Z\s]', '', tweet)
        tweet = re.sub(r'\s+', ' ', tweet)
        tweet = tweet.strip().lower()

        return tuple([word for word in tweet.split() if word not in self.stopwords])


    def __retrieve_tweets(self, hashtags) -> DataFrame:
        """
        Method to retrieve the tweets published on the given campaigns and hashtags.

        Args:
            hashtags: the hashtags with which to filter tweet retrieval (if any).

        Returns:
            The Pandas DataFrame containing the tweets of the given campaigns and hashtags.
        """
        self.logger.debug(f'Retrieving the tweets published on the campaign')

        if hashtags is None:
            query = """
                SELECT text AS tweet_text
                FROM tweet
                WHERE tweet.campaign IN %(campaigns)s;
            """
            params = {'campaigns': tuple(self.campaigns)}
        else:
            query = """
                SELECT text AS tweet_text
                FROM tweet
                    INNER JOIN hashtagt_tweet ON hashtagt_tweet.tweet_id = tweet.id
                    INNER JOIN hashtag ON hashtag.id = hashtagt_tweet.hashtag_id
                WHERE
                    tweet.campaign IN %(campaigns)s AND
                    hashtag.hashtag IN %(hashtags)s
            """
            params = {'campaigns': tuple(self.campaigns), 'hashtags' : hashtags}

        tweet_df = self.db_connector.retrieve_table_from_sql(query, params)

        self.logger.debug(f'Retrieved the tweets published on the campaign')

        return tweet_df


    def analyze(self, hashtags : Tuple[str, ...] | None = None) -> str:
        """
        Method to carry out the analysis of most used words in the given campaign/s of the XTRACK's engine.

        Args:
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The most employed words of the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Calculating relevant words employed in the tweets of the given campaigns and hashtags')

        # Step 1: Retrieving tweets from the given campaigns and hashtags
        tweets_df = self.__retrieve_tweets(hashtags)

        # Step 2: Calculating word usage from retrieved tweets
        self.analysis_results : Tuple[Tuple[str, ...], ...] = tuple(tweets_df['tweet_text'].apply(self.__preprocess_tweet).to_list())
        self.analysis_df = tweets_df

        self.logger.debug(f'Calculated relevant words employed in the tweets of the given campaigns and hashtags')

        return self.analysis_results


    def to_pandas_dataframe(self, tweet_column_name : str = 'tweet_text') -> DataFrame:
        """
        Method to convert the WordCloudAnalyzer results to a Pandas DataFrame.

        Args:
            tweet_column_name: the name of the column holding the tweet text.

        Returns:
            A Pandas DataFrame with the WordCloudAnalyzer results.
        """
        self.logger.debug('Converting WordCloudAnalyzer results into a Pandas DataFrame')

        word_cloud_tweets_df : DataFrame = self.analysis_df.copy()
        word_cloud_tweets_df.columns = [tweet_column_name]

        self.logger.debug('Converted WordCloudAnalyzer results into a Pandas DataFrame')

        return word_cloud_tweets_df


    def to_image(
            self,
            width : float = 15,
            height : float = 10,
            title : str = 'Tweet wordcloud',
        ) -> go.Figure:
        """
        Method to convert the WordCloudAnalyzer results into a figure.

        Args:
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            The figure containing the results of the WordCloudAnalyzer.
        """
        self.logger.debug('Converting word cloud analysis results to image')

        words_as_string = ' '.join([' '.join(tweet_tokens) for tweet_tokens in self.analysis_results])

        wordcloud = WordCloud(
            width = 3000,
            height = 2000,
            random_state = 42,
            background_color = '#1a1a2e',
            colormap = 'Set2',
            collocations = False,
            stopwords = STOPWORDS
        ).generate(words_as_string)

        fig = self.visualizer.create_word_cloud_plot(
            word_cloud = wordcloud,
            width = width,
            height = height,
            title = title,
        )

        self.logger.debug('Converted word cloud analysis results to image')

        return fig
