import tweepy
from pymongo import MongoClient

def connectionTwitterAPI():
    # Keys
    consumer_key = "cBM6g8ZN0ku1w7uTyiRo6mlxO"
    consumer_secret = "UGBAd3asTNgEGipWYDPKuTuelpDRkeQnniWh5QVL8imEufAyAz"
    access_key = "4490574262-FKSUsuUXvhTR2GUMcAWn7ci0wV1k3fstsu7K8yY"
    access_secret = "Sz3kfLr1dbjTuRfs5XgtvKrFvRxTJsLYXhZnTO3i2dl60"

    # Twitter initialization
    #api = TwitterAPI(consumer_key,consumer_secret,access_key,access_secret)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    return api



def connectionMongoDB():
    # Mongo initialization
    client = MongoClient("localhost", 27017)
    db = client.TwitterSearchData
    return db
    ## serverStatusResult = db.command("serverStatus")
    ## pprint(serverStatusResult)

