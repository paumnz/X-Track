import text2emotion as te
from nltk.sentiment import SentimentIntensityAnalyzer as SIA
import liwc
from collections import Counter
import re

class TweetAnalyzer:
    def __init__(self, tweet_text):
        """
        Inicializa el analizador de tweets con el texto del tweet.
        """
        self._text = tweet_text
        self._sia = SIA()

    def scan_sentiment(self):
        """
        Analiza el sentimiento del tweet utilizando el SentimentIntensityAnalyzer de NLTK.
        """
        tweet_sentiments = self._sia.polarity_scores(self._text)
        return tweet_sentiments

    def scan_emotion(self):
        """
        Analiza las emociones del tweet utilizando text2emotion.
        """
        tweet_emotions = te.get_emotion(self._text)
        return tweet_emotions

    def scan_political(self):
        """
        Cuenta el número de palabras políticas en el tweet basado en un archivo de palabras políticas.
        """
        pol_words = 0
        try:
            with open("political.txt", "r") as political_words_file:
                political_words = political_words_file.read().split("\n")
                for word in self._text.split():
                    if word.lower() in political_words:
                        pol_words += 1
        except FileNotFoundError:
            print("El archivo 'political.txt' no se encontró.")
        return pol_words

    def scan_liwc(self):
        """
        Analiza el tweet utilizando el diccionario LIWC para obtener categorías de palabras.
        """
        try:
            parse, category_names = liwc.load_token_parser('LIWC2015_English.dic')
            tokens = self._tokenize()
            counts = Counter(category for token in tokens for category in parse(token))
            liwc_scan = {
                "neg_emo": counts["negemo"],
                "pos_emo": counts["posemo"],
                "anger": counts["anger"],
                "death": counts["death"],
                "drives": counts["drives"],
                "family": counts["family"],
                "power": counts["power"],
                "money": counts["money"],
                "religion": counts["relig"],
                "time": counts["time"],
                "social": counts["social"],
                "affect": counts["affect"],
                "health": counts["health"],
                "bio": counts["bio"],
                "work": counts["work"],
                "feel": counts["feel"],
                "interrogative": counts["interrog"],
                "insight": counts["insight"],
                "focus_past": counts["focuspast"],
                "focus_future": counts["focusfuture"],
                "discrepancies": counts["discrep"],
                "achieve": counts["achieve"],
                "leisure": counts["leisure"],
                "motion": counts["motion"],
                "perception": counts["percept"],
                "affiliation": counts["affiliation"],
                "male": counts["male"],
                "female": counts["female"],
                "informal": counts["informal"],
                "swear": counts["swear"],
                "netspeak": counts["netspeak"]
            }
            return liwc_scan
        except FileNotFoundError:
            print("El archivo 'LIWC2015_English.dic' no se encontró.")
            return {}

    def _tokenize(self):
        """
        Tokeniza el texto del tweet.
        """
        for match in re.finditer(r'\w+', self._text, re.UNICODE):
            yield match.group(0)

