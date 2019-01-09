import nltk
from nltk.corpus import stopwords
import string
import string
import re
import pickle
import os
import csv
from pymongo import MongoClient
import datetime
import time
import math
from datetime import date
from connections import connectionTwitterAPI, connectionMongoDB

# connection to MongoDB
client = MongoClient("localhost", 27017)
dbMongo = client.TwitterSearchData


words_architect = ['teamarchi', 'archi', 'urbanist', 'dplg', 'd.p.l.g', 'design']
words_enterprise = ['manufactur', 'facility', 'firm', 'filiale', 'enterprise','peintre','construc','building','bim','ouvrier','artisan','agenc']
words_association = 'associat'
words_construction = 'construc'
words_agence = 'agenc'
words_journalist = ['journal', 'media', 'press', 'editor', 'redact', 'magazine', 'communicat']
words_ecole = ['etudiant', 'student', 'ecole', 'educ', 'enseign', 'prof', 'formateur',
               'ecole nationale superieure']
words_director = ['directeur', 'director', 'directrice', 'ceo']
words_photo = ['photo', 'photograph']
words_communication = ['press', 'media', 'communicat','journal']
'''

list1 = dbMongo.Authors.count({})
print(list1)
list2 = dbMongo.Authors.find({})
list3 = dbMongo.Authors.count({'description':''})
print(list3)
list4 = dbMongo.Authors.find({'origin': "keyword_search"})
list5 =  dbMongo.Authors.count({'origin': "keyword_search"})
print(list5)

list6 =  dbMongo.Authors.find({'origin': "retweete d"})
for text in list6 :
    print(text.get('author_name'))

count_prescri = 0
count_faiseur = 0
count_ecole = 0
count_media = 0

for element in list4:
    for word in words_architect:
        if word in element.get('description'):
            count_prescri +=1
            break
    for word in words_enterprise:
        if word in element.get('description'):
            count_faiseur +=1
            break
    for word in words_ecole:
        if word in element.get('description'):
            count_ecole +=1
            break
    for word in words_journalist:
        if word in element.get('description'):
            count_media +=1
            break

print(count_prescri)
print(count_faiseur)
print(count_ecole)
print(count_media)

'''

length_tweet = 100

# connection to MongoDB
client = MongoClient("localhost", 27017)
dbMongo = client.TwitterSearchData

list = dbMongo.Authors.find({'origin':"keyword_search", 'data_imported': True}).distinct('author_name')

loop = 0
for authorname in list:
    alltweets = []
    print(authorname)
    nb_tweets = 0
    statuses = connection.search(screen_name=authorname, count=100, max_id=oldest)

    # save most recent, "screenname" : "degioanni", "numberofretweets" : 2, "author_id" : 17514448 t tweets
    alltweets.extend(statuses)

    if (alltweets[-1].id - 1 == oldest):
        break

    # update the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    i = i + 1
    print("...%s tweets downloaded so far" % (len(alltweets),))


