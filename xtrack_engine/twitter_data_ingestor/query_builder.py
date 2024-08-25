"""
Module to prepare data retrieval from the Twitter API.
"""

import argparse
import datetime
import pymongo

class TrendingTopicsManager:
    def __init__(self, start_date, trending_topics, mongo_uri, db_name='trending_topics', collection_name='usa2017', city='trump17'):
        self.start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        self.trending_topics = trending_topics
        self.city = city
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]


    def insert_trending_topics(self, days=5):
        current_date = self.start_date
        for _ in range(days):
            for hour in range(24):
                for topic in self.trending_topics:
                    topic_object = {
                        "trending_topic": topic,
                        "trending_topic_info": "",
                        "date": current_date.strftime("%Y-%m-%d"),
                        "hour": str(hour),
                        "city": self.city
                    }
                    self.collection.insert_one(topic_object)
            current_date += datetime.timedelta(days=1)
