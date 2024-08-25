"""
Module to implement the word usage analysis functionality of XTRACK's engine.
"""


import logging
import re
from typing import Any, Dict, Tuple

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


    @property
    def pre_computed_results_query(self) -> str:
        """ Property to retrieve the pre-computed results of the UserReplyActivityAnalyzer. """
        return """
            SELECT tweet_text
            FROM tweet_wordcloud_analysis_results
            WHERE
                campaign_analysis_id = %(campaign_analysis_id)s
        """


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


    def build_new_results(
            self,
            campaign_analysis_id : int,
            hashtags : Tuple[str, ...] | None = None
        ) -> str:
        """
        Method to carry out the analysis of most used words in the given campaign/s of the XTRACK's engine.

        Args:
            campaign_analysis_id: the identifier with which to store results into the database.
            hashtags: the hashtags with which to filter the activity (if any).

        Returns:
            The most employed words of the given campaigns and hashtags (if provided).
        """
        self.logger.debug(f'Calculating relevant words employed in the tweets of the given campaigns and hashtags')

        # Step 1: Retrieving tweets from the given campaigns and hashtags
        tweets_df = self.__retrieve_tweets(hashtags)

        # Step 2: Calculating word usage from retrieved tweets
        self.analysis_results : Tuple[Tuple[str, ...], ...] = tuple(tweets_df['tweet_text'].apply(self.__preprocess_tweet).to_list())

        # Step 3: Storing the results into the database
        processed_df = self.to_pandas_dataframe()
        processed_df['campaign_analysis_id'] = campaign_analysis_id
        processed_df = processed_df[['campaign_analysis_id', 'tweet_text']]
        self.db_connector.store_table_to_sql(processed_df, 'tweet_wordcloud_analysis_results', 'append')

        self.logger.debug(f'Calculated relevant words employed in the tweets of the given campaigns and hashtags')

        return self.analysis_results


    def __format_analysis_results(self, wordcloud_df : DataFrame) -> Tuple[Tuple[str, ...], ...]:
        """
        Method to format the pre-computed DataFrame into the expected format by the front-end.

        Args:
            wordcloud_df (DataFrame): The Pandas DataFrame containing the pre-computed results.

        Returns:
            A tuple containing the tuple of tokens of each tweet (processed).
        """
        self.logger.debug('Formatting the pre-computed results of the WordCloudAnalyzer')

        wordcloud_results = tuple(tuple(row['tweet_text'].split(' ')) for _, row in wordcloud_df.iterrows())

        self.logger.debug('Formatted the pre-computed results of the WordCloudAnalyzer')

        return wordcloud_results


    def analyze(
            self,
            campaign_analysis_id : int,
            pre_computation_query_params : Dict[str, Any] = {},
            new_computation_kwargs : Dict[str, Any] = {}
        ) -> Any:
        """
        Method to analyze the most employed words in the tweets of the given campaign (wordcloud).

        Args:
            campaign_analysis_id: the identifier to be used for storing the analysis results in the database.
            pre_computation_query_params: the parameters to be used for the query that checks for existing WordCloudAnalyzer pre-computed results.
            new_computation_kwargs: the arguments to be used for computing the analysis results from scratch.

        Returns:
            A tuple containing the tokens per tweet with which to build the wordcloud.
        """
        return super().analyze(campaign_analysis_id, pre_computation_query_params, self.__format_analysis_results, new_computation_kwargs)


    def to_pandas_dataframe(self, tweet_column_name : str = 'tweet_text') -> DataFrame:
        """
        Method to convert the WordCloudAnalyzer results to a Pandas DataFrame.

        Args:
            tweet_column_name: the name of the column holding the tweet text.

        Returns:
            A Pandas DataFrame with the WordCloudAnalyzer results.
        """
        self.logger.debug('Converting WordCloudAnalyzer results into a Pandas DataFrame')

        tweet_df = DataFrame([' '.join(tweet) for tweet in self.analysis_results], columns = [tweet_column_name])

        self.logger.debug('Converted WordCloudAnalyzer results into a Pandas DataFrame')

        return tweet_df


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
            width = 500,
            height = 300,
            random_state = 42,
            background_color = '#1a1a2e',
            colormap = 'Set2',
            collocations = False,
            stopwords = STOPWORDS,
            max_words = 30
        ).generate(words_as_string)

        fig = self.visualizer.create_word_cloud_plot(
            word_cloud = wordcloud,
            width = width,
            height = height,
            title = title,
        )

        self.logger.debug('Converted word cloud analysis results to image')

        return fig
