import os
import pickle
import datetime
import io
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
import string
import tweepy
import re
from textblob import TextBlob
from pymongo import MongoClient
from connections import connectionTwitterAPI
from multiprocessing.dummy import Pool as ThreadPool
import itertools
#from stemmingWordDataTest import stemmingWords
#from getExpressions_v3 import getExpressions, groupExpressions
from time import sleep
import spacy

#download stopwords (only 1 execution needed). Stopwords are unimportant words, like determiners.
nltk.download('stopwords')

#load language
nlp = spacy.load('xx')

#affectation of the stopwords per language, and personalization by adding other words we wish not to see
stop_words_eng = set(stopwords.words('english'))
stop_words_fr = set(stopwords.words('french'))
otherwords_fr = ['les', 'leur', 'leurs', 'celle', 'celles', 'ceux', 'celui', 'le', 'la', 'des', 'nos', 'est', 'cette', 'quand', '&gt;&gt', '&lt;&lt', 'ça','va', 'de', '&amp', '&gt', 'si', "qu'il", 'plus', 'tous', "j'ai", 'ils', 'cela', 'ici', 'où', "d'une", "d'un", "c'est", "l'"]
stop_words_fr |= set(otherwords_fr)
otherwords_eng = ['this', "they're", 'their', 'you', "my", 'one']
stop_words_eng |= set(otherwords_eng)

# connection to MongoDB
client = MongoClient("localhost", 27017)
dbMongo = client.TwitterSearchData

#open the dictionary to import the list of keywords to search
with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
    dictionary = pickle.load(data)
    section = dictionary[0]
    list_keywords = dictionary[1]
    list_complements = dictionary[2]

def get_list_WordData(list_tweetdata, query):
    for s in list_tweetdata:
        try:

            ###### Scattering the tweet in words and saving word data into WordData
            print("before get text")
            print(s)
            # split the text of the tweet in words and affecting them in a list
            list_words = s.get('text').lower().split(' ')
            # defining the punctuation
            punc = "!,.:;?^-~…\\➡️•+/"
            accolades = "(){}[]|«»\""
            # filter empty items in the list
            print("before while")
            while '' in list_words:
                list_words.remove('')
            increment = len(list_words)

            ##### separate punctuations and accolades from words
            # example : All men must die. Dracarys!!!!
            #  ['All', 'men', 'must', 'die.', 'Dracarys!!!!'] => ['All', 'men', 'must', 'die', '.', 'Dracarys', '!!!!']

            # reverse to prevent range errors because of the insertion
            for word in reversed(list_words):
                print("FIRST LOOP ENTERED")

                if '#' in word[1:] and 'http' not in word:
                    list_words[increment - 1] = word[0] + word[1:].split('#')[0]
                    list_words.insert(increment, '#' + word.split('#')[1])

                # if the last letter of the word is a punctuation or a bracket :
                if word[-1:] in punc or word[-1:] in accolades:
                    i = 1
                    if len(word) != 1:
                        # while the last letters are a succession of punctuations or brackets, separate them from the word
                        while ((word[-i:-i + 1] in punc or word[-i:-i + 1] in accolades) and i <= len(word)):
                            i += 1
                        if increment >= 0:
                            list_words[increment - 1] = word[:-i + 1]
                            list_words.insert(increment, word[-i + 1:])
                            word = word[-i + 1:]
                        # if the word is empty, do nothing
                        else:
                            pass

                # if the first letter of the word is a punctuation or a bracket :
                if word[:1] in punc or word[:1] in accolades:
                    j = 1
                    if len(word) != 1:
                        # while the first letters are a succession of punctuations or brackets, separate them from the word
                        while ((word[j:j + 1] in punc or word[j:j + 1] in accolades) and j <= len(word)):
                            j += 1
                        try:
                            list_words[increment - 1] = word[j:]
                            list_words.insert(increment - 1, word[:j])
                        except:
                            IndexError

                increment -= 1
                print("PUNCTUATION IS WORKING")

            # filter empty items in the list
            while '' in list_words:
                list_words.remove('')

            index = 1

            # detect the language of the tweet
            try:

                if s.lang is not None:
                    if s.lang == "de":
                        stemmer = SnowballStemmer("german")
                    if s.lang == "es":
                        stemmer = SnowballStemmer("spanish")
                    if s.lang == "pt":
                        stemmer = SnowballStemmer("portuguese")
                    if s.lang == "en":
                        stemmer = SnowballStemmer("english")
                    if s.lang == "fr":
                        stemmer = SnowballStemmer("french")
                print("THE LANGUAGE WORKS")
            except:
                AttributeError

            ######importation of the word data into the collection WordData

            # for every word in the current tweet
            for word in list_words:
                print("BEWARE FOR LOOP ENTERED")
                # initialization of the data
                is_mention = 0
                is_hashtag = 0
                wordclear = word
                word_type = ''
                # if it's the first word of the tweet, there is no word before it : set prev_word to None
                if index == 1:
                    prev_word = None
                # else grab the previous word
                else:
                    prev_word = list_words[index - 2]
                # try grabbing the next word of the current word
                try:
                    next_word = list_words[index]
                # if its the last word, set next_word to None
                except:
                    next_word = None

                ### clear special determiners in the french language : m' , l' , d' , t' , n', etc.

                try:  # exceptions happen if the word's length is only 1

                    # if an apostrophe is detected on the second position of the word
                    if (word[1] == '\'' or word[1] == '’') and s.lang == "fr":
                        # grab what's after the apostrophe
                        wordclear = word[2:]
                        # if you grabbed nothing => case of a space between the apostrophe and the word
                        if wordclear == '':
                            # correct it by adding the next word to the word
                            word = word + next_word
                            # then set the next_word data to the next next word
                            next_word = list_words[index + 1]

                            # grab the word without its special determinant if there is one after the apostrophe
                            try:
                                if word[1] == '\'' or word[1] == '’':
                                    wordclear = next_word
                            except:
                                IndexError
                            # delete the next word from the list because we concatenated it to the current word
                            del list_words[index]
                except:
                    IndexError

                print("IT WORKS UNTIL PREV WORD AND NEXT WORD")

                # if the first letter of the word is a hashtag or an at symbol, detect it
                try:
                    if "#" == wordclear[0]:
                        is_hashtag = 1
                        wordclear = wordclear[1:]
                    if "@" == wordclear[0]:
                        is_mention = 1
                        wordclear = wordclear[1:]

                # if the author intelligently hashtaged or mentionned blank space, throw an IndexError, and in this situation wordclear = ''
                except:
                    IndexError

                ### detect the type of the word : keyword, stopword, punctuation, or link
                if query and word == query:
                    word_type = "keyword"
                if word in stop_words_fr or word in stop_words_eng:
                    word_type = "stopword"
                if word[0] in punc or word[0] in accolades:
                    word_type = "punctuation"
                if 'http' in word:
                    word_type = "lien"

                # stem the word and assign it to wordroot, which represent the family of the word
                try:
                    wordroot = stemmer.stem(wordclear)
                # if no language is detected, don't stem
                except:
                    wordroot = wordclear

                try:
                    if s.retweeted_status is not None:
                        is_retweet = 1
                except:
                    is_retweet = 0

                # store the important data of the word in the dictionary WordData, and save it to the collection WordData
                # _id is the primary key, if already detected in the collection, it overwrites the data => no duplications
                print("IT WORKS BEFORE WORKDATATEST")
                WordData = {'_id': s.get('_id') + str(index), 'tweetid': s.get('tweetid'),
                                'word': word, 'wordroot': wordroot, 'wordclear': wordclear,
                                'prev_word': prev_word, 'next_word': next_word,
                                'created_at': s.get('created_at'), 'selectedword':word,
                                'position': index, 'is_mention': is_mention, 'is_hashtag': is_hashtag,
                                'word_type': word_type, 'is_retweet': is_retweet,
                                'import_date': datetime.date.today().strftime('%Y-%m-%d %H:%M')}
                dbMongo.Word.save(WordData)
                dbMongo.Word2.save(WordData)
                print(WordData)
                index += 1

            dbMongo.Tweet.update({'_id': s.get('_id')}, { '$set': {'word_imported':True} })
        except:
            IndexError


def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())


if __name__ == '__main__':


    #pool = ThreadPool(8)

    dbMongo.Tweet.update({}, {'$set': {'word_imported': False}})

    list_tweet = dbMongo.TweetData.find({'word_imported': False})

    try:
        get_list_WordData(list_tweet, '#teamarchi')
    except:
        IndexError
    # getExpressions()
    # groupExpressions()
    dbMongo.Word2.remove({})


    #lst_oldauthdat = split_list_authors(False, 4)
    #lst_newauthdat = split_list_authors(True, 4))
    #results = pool.starmap(get_multithread,zip(lst_newauthdat))

    '''
    list_authordat = dbMongo.AuthorData.find({'data_imported':True}).distinct('author_name')


    for key in list_keywords:
        print(key)
        get_multithread(list_authordat,key)
    '''
    #get sentimment of tweets without sentiment


    '''
    list_tweet_nosentiment = dbMongo.TweetData.find({'sentiment': {"$exists":False}})

    for tweet in list_tweet_nosentiment:
        print(tweet)
        if tweet.get('text'):
            tweet['sentiment'] = get_tweet_sentiment(tweet.get('text'))
        else:
            dbMongo.TweetData.remove({'_id': tweet.get('_id')})
        dbMongo.TweetData.save(tweet)
    '''