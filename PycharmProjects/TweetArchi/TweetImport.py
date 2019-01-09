import os
import pickle
import datetime
from datetime import date
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
from time import sleep
import spacy

#cloud language imports
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types



os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/ubuntu/Downloads/ArchImage-4545358e6adc.json"


client = language.LanguageServiceClient()


words_architect = ['teamarchi', 'architect', 'urbanist', 'dplg', 'd.p.l.g', 'design']
words_enterprise = ['manufactur', 'facility', 'firm', 'filiale', 'enterprise']
words_association = 'associat'
words_construction = 'construc'
words_agence = 'agenc'
words_journalist = ['journalist', 'media', 'presse', 'editor', 'redact', 'magazine']
words_ecole = ['etudiant', 'student', 'ecole', 'education', 'enseignant', 'professor', 'professeur','formateur', 'ecole nationale superieure']
words_director = ['directeur', 'director', 'directrice', 'ceo']
words_photo = ['photo', 'photograph']
words_communication = ['presse', 'media', 'communicat']

#download stopwords (only 1 execution needed). Stopwords are unimportant words, like determiners.
nltk.download('stopwords')

#load spacy natural processing languages
nlp_fr = spacy.load('/home/ubuntu/python-docs-samples/vision/cloud-client/detect/venv/lib/python3.5/site-packages/fr_core_news_sm/fr_core_news_sm-2.0.0')
nlp_en = spacy.load('/home/ubuntu/python-docs-samples/vision/cloud-client/detect/venv/lib/python3.5/site-packages/en_core_web_sm/en_core_web_sm-2.0.0')


#affectation of the stopwords per language, and personalization by adding other words we wish not to see
stop_words_eng = set(stopwords.words('english'))
stop_words_fr = set(stopwords.words('french'))
otherwords_fr = ['les', 'leur', 'leurs', 'celle', 'celles', 'ceux', 'celui', 'le', 'la', 'des', 'nos', 'est', 'cette', 'quand', '&gt;&gt', '&lt;&lt', 'ça','va', 'de', '&amp', '&gt', 'si', "qu'il", 'plus', 'tous', "j'ai", 'ils', 'cela', 'ici', 'où', "d'une", "d'un", "c'est", "l'"]
stop_words_fr |= set(otherwords_fr)
otherwords_eng = ['this', "they're", 'their', 'you', "my", 'one']
stop_words_eng |= set(otherwords_eng)

import_all = 100
import_week = 50

d0 = date(2018,1,1)
now = datetime.datetime.now()
d1 = date(now.year,now.month,now.day)
delta = d1 - d0
nb_days_2018 = delta.days

# connection to MongoDB
client = MongoClient("localhost", 27017)
dbMongo = client.TwitterSearchData


#open the dictionary to import the list of keywords to search
with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
    dictionary = pickle.load(data)
    section = dictionary[0]
    list_keywords = dictionary[1]
    list_complements = dictionary[2]

def saveAuthor(s, dbMongo, origin):
    # store the important data of the author in the dictionary Authors, and save it to the collection Authors
    # _id is the primary key, if already detected in the collection, it overwrites the data => no duplications
    Author = {'_id': s.author.id_str,
              'authorid': s.author.id_str,
              'author_name': s.author.screen_name,
              'location': s.author.location.replace("\n", " ").replace(",", "~"),
              'user_url': s.author.url,
              'description': s.author.description.replace("\n", " ").replace(",", "~"),
              # 'derived_geo': s.author.derived,
              'protected_acc': s.author.protected,
              'verified_acc': s.author.verified,
              'nb_followers': s.author.followers_count,
              'nb_friends': s.author.friends_count,
              'nb_lists': s.author.listed_count,
              'nb_liked': s.author.favourites_count,
              'nb_tweets': s.author.statuses_count,  # from the user (including RT)
              'created_at': s.author.created_at,  # time of the creation of the acc
              'utc_offset': s.author.utc_offset,
              'time_zone': s.author.time_zone,
              'geo_enabled': s.author.geo_enabled,
              'country': s.author.lang,
              # 'contributors_enabled': s.author.contributors_enabled,
              'profile_background_color': s.author.profile_background_color,
              'background_img': s.author.profile_background_image_url,
              # 'profile_background_img_https': s.author.profile_background_image_url_https,
              'nb_faces_profile': 0, 'tile': 0, 'nb_colors_profile': 0,
              'nb_chars_profile': 0,
              'profile_background_tile': s.author.profile_background_tile,
              # 'profile_banner_url': s.author.profile_banner_url,
              'profile_img': s.author.profile_image_url.replace('_normal', ''),
              # 'profile_img_https': s.author.profile_image_url_https,
              # 'profile_link_color': s.author.profile_link_color,
              # 'profile_sidebar_border_color': s.author.profile_sidebar_border_color,
              # 'profile_sidebar_fill_color': s.author.profile_sidebar_fill_color,
              # 'profile_text_color': s.author.profile_text_color,
              # 'profile_use_background_image': s.author.profile_use_background_image,
              # 'default_profile': s.author.default_profile,
              # 'default_profile_img': s.author.default_profile.image,
              # 'withheld_in_countries': s.author.withheld_in_countries,
              # 'withheld_scope': s.author.withheld_scope,
              'class': "1",
              'origin': origin,
              'import_date_author': datetime.date.today().strftime('%Y-%m-%d %H:%M')
              }

    if dbMongo.Authors.count({'author_name':s.author.screen_name, 'data_imported':True}) == 0:
        Author['data_imported'] = False

    # store quoted authors
    if origin == "quoted_author":
        # we don't want to store their tweets
        del Author['data_imported']
        # change the _id to separated them from important authors
        Author['_id'] = "q" + Author.get('authorid')
        # if not already stored, set quoted_times to 1
        if dbMongo.Authors.count({'_id': "q" + Author.get('authorid')}) == 0:
            Author['quoted_times'] = 1
        # if stored, increment quoted_times and save
        else:
            find_quoted = dbMongo.Authors.find({'_id': Author.get('_id')})
            for quoted in find_quoted:
                Author['quoted_times'] = quoted.get('quoted_times') + 1

    # store replied authors
    elif origin == "replied_author":
        # we don't want to store their tweets
        del Author['data_imported']
        # change the _id to separate them from important authors
        Author['_id'] = "rp" + Author.get('authorid')
        # if not already stored, set replied_times to 1
        if dbMongo.Authors.count({'_id': "rp" + Author.get('authorid')}) == 0:
            Author['replied_times'] = 1
        # if stored, increment replied_times and save
        else:
            find_replied = dbMongo.Authors.find({'_id': Author.get('_id')})
            for replied in find_replied:
                Author['replied_times'] = replied.get('replied_times') + 1

    # store retweeted authors
    elif origin == "retweeted_author":
        del Author['data_imported']
        Author['_id'] = "rt" + Author.get('authorid')
        if dbMongo.Authors.count({'_id': "rt" + Author.get('authorid')}) == 0:
            Author['retweeted_times'] = 1
        else:
            find_retweeted = dbMongo.Authors.find({'_id': Author.get('_id')})
            for retweeted in find_retweeted:
                Author['retweeted_times'] = retweeted.get('retweeted_times') + 1


    # get data of interesting users every months, (or every week by uncommenting the line below)
    elif origin == "keyword_search":
        Author['_id'] += datetime.date.today().strftime(
            '%Y-%m')  # + '-w' + str(int(int(datetime.date.today().strftime('%d'))/8)%4)
        if dbMongo.Authors.count({'_id': Author.get('_id')}) == 0:
            Author['keyword_times'] = 1
        else:

            find_keywords = dbMongo.Authors.find({'_id': Author.get('_id')})
            for keyword in find_keywords:
                print(keyword.get('keyword_times'))
                if not keyword.get('keyword_times'):
                    Author['keyword_times'] = 1
                else:
                    Author['keyword_times'] = int(keyword.get('keyword_times')) + 1

    for word in words_architect:
        if word in s.author.description.lower():
            Author['class'] = "2"
            break
    for word in words_enterprise:
        if word in s.author.description.lower():
            Author['class'] += "3"
            break
    for word in words_journalist:
        if word in s.author.description.lower():
            Author['class'] += "4"
            break
    for word in words_ecole:
        if word in s.author.description.lower():
            Author['class'] += "5"
            break
    if words_agence in s.author.description.lower():
        Author['class'] += "6"
    for word in words_director:
        if word in s.author.description.lower():
            Author['class'] += "7"
            break
    for word in words_photo:
        if word in s.author.description.lower():
            Author['class'] += "8"
            break
    if words_association in s.author.description.lower():
        Author['class'] += "9"
    dbMongo.Authors.save(Author)
    print("new author : " + Author.get('author_name'))


def split_list_authors(isNewAuthor, nbsplit):

    # store in a list all the distinct words in the collection WordData
    list_authorname = dbMongo.Authors.find({'data_imported': not isNewAuthor}).distinct('author_name')
    print(list_authorname)
    try:
        chunks = [list_authorname[x:x+(int(len(list_authorname)/nbsplit))] for x in range(0, len(list_authorname), int(len(list_authorname)/nbsplit))]
    except:
        chunks = []
    return chunks


def get_media(tweet_data, keyword):
    if 'media' in tweet_data.entities:
        count_media = 0
        for media in tweet_data.extended_entities['media']:
            if 'video' in media.get('expanded_url'):
                print('media type : video')
                print(media['expanded_url'])
                Entity = {'_id': "v" + tweet_data.id_str + str(count_media), 'e_tweetid': tweet_data.id_str, 'entity_type': "video", 'entity_content': media['expanded_url'], 'tweet_keyword': keyword, 'entity_author': tweet_data.author.screen_name, 'number':count_media, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
                dbMongo.Entities.save(Entity)
                count_media += 1
            else:
                print('media type : image')
                print(media['media_url'])
                Entity = {'_id': "i" + tweet_data.id_str + str(count_media), 'e_tweetid': tweet_data.id_str, 'entity_type': "image", 'entity_content': media['media_url'], 'tweet_keyword': keyword, 'entity_author': tweet_data.author.screen_name, 'number': count_media, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
                dbMongo.Entities.save(Entity)

    else:
        print('no media')

def get_hashtag(tweet_data):
    if tweet_data.entities.get('hashtags'):
        count_hashtag = 0
        for hashtag in tweet_data.entities['hashtags']:
            #print('media type : hashtag')
            #print(hashtag.get('text'))
            Entity = {'_id': "h" + tweet_data.id_str + str(count_hashtag), 'e_tweetid': tweet_data.id_str, 'entity_type': "hashtag", 'entity_content': hashtag.get('text'), 'entity_author': tweet_data.author.screen_name, 'number': count_hashtag, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
            count_hashtag += 1
            dbMongo.Entities.save(Entity)
def get_hashtag_kw(tweet_data, keyword):
    if tweet_data.entities.get('hashtags'):
        count_hashtag = 0
        for hashtag in tweet_data.entities['hashtags']:
            #print('media type : hashtag')
            #print(hashtag.get('text'))
            Entity = {'_id': "h" + tweet_data.id_str + str(count_hashtag), 'e_tweetid': tweet_data.id_str, 'entity_type': "hashtag", 'entity_content': hashtag.get('text'), 'tweet_keyword': keyword, 'entity_author': tweet_data.author.screen_name, 'number': count_hashtag, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
            count_hashtag += 1
            dbMongo.Entities.save(Entity)


def get_mentions(tweet_data):
    if tweet_data.entities.get('user_mentions'):
        count_mention = 0
        for user in tweet_data.entities['user_mentions']:
            #print('media type : mention')
            #print(user.get('screen_name'))
            Entity = {'_id': "m" + tweet_data.id_str + str(count_mention), 'e_tweetid': tweet_data.id_str, 'entity_type': "mention",
                 'entity_content': user.get('screen_name'), 'entity_author': tweet_data.author.screen_name, 'number': count_mention, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
            count_mention += 1
            dbMongo.Entities.save(Entity)

def get_mentions_kw(tweet_data, keyword):
    if tweet_data.entities.get('user_mentions'):
        count_mention = 0
        for user in tweet_data.entities['user_mentions']:
            # print('media type : mention')
            # print(user.get('screen_name'))
            Entity = {'_id': "m" + tweet_data.id_str + str(count_mention), 'e_tweetid': tweet_data.id_str,
                              'entity_type': "mention",
                              'entity_content': user.get('screen_name'), 'tweet_keyword': keyword, 'entity_author': tweet_data.author.screen_name, 'number': count_mention, 'created_at': tweet_data.created_at.strftime('%Y-%m-%d %H:%M')}
            count_mention += 1
            dbMongo.Entities.save(Entity)


#get a list of the last tweets, length of list determined by nbloop = the number of loops
def get_list_TweetData(connection, list, length_tweet):

    # connection to MongoDB
    client = MongoClient("localhost", 27017)
    dbMongo = client.TwitterSearchData

    loop = 0
    for authorname in list:
        alltweets = []
        print(authorname)

        try :
            statuses = connection.user_timeline(screen_name=authorname, count=length_tweet, tweet_mode='extended')
            alltweets.extend(statuses)
            oldest = alltweets[-1].id - 1
            print("author number :" + str(loop))
            loop += 1

            # keep grabbing tweets until nbloop is reached / there are no tweets left to grab
            i = 0

            if length_tweet == 100:
                limit_import = 30

            if length_tweet == 50:
                limit_import = 7

            # while i < nbloop:
            while alltweets[-1].created_at >= (datetime.datetime.today() - datetime.timedelta(days=limit_import)):
                print("getting tweets before %s" % (oldest,))

                # all subsiquent requests use the max_id param to prevent duplicates
                statuses = connection.user_timeline(screen_name=authorname, count=length_tweet, max_id=oldest,
                                                    tweet_mode='extended')

                # save most recent, "screenname" : "degioanni", "numberofretweets" : 2, "author_id" : 17514448 t tweets
                alltweets.extend(statuses)

                # update the id of the oldest tweet less one
                if oldest == alltweets[-1].id - 1:
                    break
                oldest = alltweets[-1].id - 1
                i = i + 1
                print("...%s tweets downloaded so far" % (len(alltweets),))

            # get from tweet : author name, keyword used, number of times the tweet has been liked, retweeted, quoted, replied

            for s in alltweets:

                print('---------------------TWEET------------------------')
                keysection = ''
                query = ''

                # modify the text of the tweet to respect the csv output (delimiter is ~ so we need to clean it from the text)
                try:
                    if s.full_text is not None:
                        text_clear = s.full_text.replace('\n', ' ').replace('~', ' ')
                except:
                    text_clear = s.text.replace('\n', ' ').replace('~', ' ')

                Tweet = {'_id': s.id_str,
                         'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
                         'tweetid': s.id_str,
                         'text': text_clear,
                         'source': s.source,
                         'truncated': s.truncated,
                         'in_reply_to_status_str': s.in_reply_to_status_id_str,
                         'in_reply_to_user_id': s.in_reply_to_user_id_str,
                         'author_name': s.author.screen_name,
                         'authorid': s.author.id_str,
                         'coordinates': s.coordinates,
                         'place': s.place,
                         'is_quote': s.is_quote_status,
                         'nb_retweeted': s.retweet_count,
                         'nb_likes': s.favorite_count,
                         'section': None,
                         'keyword': None,
                         # 'favorited': s.favorited,
                         # 'retweeted': s.retweeted,
                         # 'possibly_sensitive': s.possibly_sensitive,
                         # 'filter_level': s.filter_level,
                         'lang': s.lang,
                         # 'matching_rules': s.matching_rules,
                         'complement': '',
                         'word_imported': False,
                         'import_date': datetime.date.today().strftime('%Y-%m-%d %H:%M')
                         }

                if s.entities.get('urls'):
                    # print(s.extended_entities)
                    for url in s.entities['urls']:
                        try:
                            if '/status/' in url['expanded_url']:
                                print(s.author.screen_name)
                                print(url['expanded_url'].split('/status/')[1])
                                tweet = connectionTwitterAPI().get_status(int(url['expanded_url'].split('/status/')[1]),
                                                                          tweet_mode='extended')
                                print(tweet.full_text)
                                get_media(tweet)
                                get_hashtag(tweet)
                                get_mentions(tweet)
                            else:
                                print('media type : url')
                                print(url['expanded_url'])
                                get_hashtag(s)
                                get_mentions(s)
                        except:
                            ConnectionError

                get_hashtag(s)
                get_mentions(s)

                countrt = 0

                try:
                    if s.retweeted_status is not None:
                        countrt += 1
                        Tweet['rt_originaltweetid'] = s.retweeted_status.id_str
                        Tweet['rt_originalauthorname'] = s.retweeted_status.author.screen_name
                        Tweet['text'] = s.retweeted_status.full_text.replace("\n", " ").replace("~", " ")
                        if dbMongo.Tweet.count({'_id': s.id_str}) == 0:
                            saveAuthor(s.retweeted_status, dbMongo, "retweeted_author")
                except:
                    Tweet['rt_originaltweetid'] = None
                    Tweet['text'] = text_clear

                    ###### if the tweet has a location, save it

                print(s)

                try:
                    if s.place is not None:
                        Tweet['country'] = s.place.country

                except:
                    Tweet['country'] = None
                    # Tweet['coordinates'] = None

                try:
                    if s.place.place_type == 'city':
                        Tweet['city'] = s.place.name
                    else:
                        Tweet['city'] = None
                        # Tweet['coordinates'] = s.place.bounding_box.coordinates
                except:
                    Tweet['city'] = None

                try:
                    Tweet['coordinates'] = s.place.bounding_box.coordinates

                    geo_x = []
                    geo_y = []

                    for doc in s.place.bounding_box.coordinates:
                        for docs in doc:
                            for point in docs:
                                geo_x.append(point[0])
                                geo_y.append(point[1])

                    mean_x = geo_x.mean()
                    mean_y = geo_y.mean()
                    Tweet['geopoint'] = [mean_x, mean_y]

                except:
                    Tweet['coordinates'] = None

                try:
                    Tweet['reply_to_screen_name'] = s.reply_to_screen_name
                except:
                    Tweet['reply_to_screen_name'] = None

                try:
                    Tweet['quoted_status_id_str'] = s.quoted_status_id_str
                except:
                    Tweet['quoted_status_id_str'] = None

                try:
                    Tweet['quoted_status_id_str'] = s.quoted_status.id_str
                    Tweet['quoted_status_authorid'] = s.quoted_status.author.id_str
                    Tweet['quoted_status_author_name'] = s.quoted_status.author.screen_name
                    if dbMongo.Tweet.count({'_id': s.id_str}) == 0:
                        saveAuthor(s.quoted_status, dbMongo, "quoted_author")
                    print(
                        "quote id:" + s.quoted_status.author.id_str + " ; " + s.quoted_status.author.screen_name + " vs " + s.author.screen_name)
                except:
                    Tweet['quoted_status_id_str'] = None
                    Tweet['quoted_status_authorid'] = None
                    Tweet['quoted_status_author_name'] = None

                try:
                    Tweet['quote_count'] = s.quote_count
                except:
                    Tweet['quote_count'] = None

                try:
                    Tweet['reply_count'] = s.reply_count
                except:
                    Tweet['reply_count'] = None
                try:
                    if Tweet['in_reply_to_status_str']:
                        tweet = connectionTwitterAPI().get_status(int(Tweet.get('in_reply_to_status_str')),
                                                                  tweet_mode='extended')
                        if dbMongo.Tweet.count({'_id': s.id_str}) == 0:
                            saveAuthor(tweet, dbMongo, "replied_author")
                except:
                    print("replied tweet not found")

                ########################### get the primal sentiment of the tweet###############################


                Tweet['primal_sentiment'] = get_tweet_sentiment(Tweet.get('text'))

                #########################################################################################

                for complements in list_complements:
                    for complement in complements:
                        for comp in complement:
                            if comp in s.full_text.lower():
                                Tweet['complement'] += comp

                countitem = 0
                countkeywords = 0
                for keywords in list_keywords:
                    for key in keywords:
                        if key in s.full_text.lower():
                            keysection = section[countitem]
                            query = key

                            ########################### get the advanced sentiment of the tweet###############################

                            # doc = types.Document(content=s.full_text.lower(), type=enums.Document.Type.PLAIN_TEXT)
                            # sentiment = client.analyze_sentiment(document = doc).document_sentiment
                            # entities = client.analyze_entities(doc).entities

                            #########################################################################################

                            if countkeywords == 0:
                                Tweet['section'] = keysection
                                Tweet['keyword'] = query
                            else:
                                if keysection not in Tweet.get('section'):
                                    Tweet['section'] = Tweet.get('section') + " - " + keysection
                                Tweet['keyword'] = Tweet.get('keyword') + " - " + query
                            saveAuthor(s, dbMongo, "keyword_search")
                            countkeywords += 1
                    countitem += 1

                get_media(s, Tweet.get('keyword'))
                get_mentions_kw(s, Tweet.get('keyword'))
                get_hashtag_kw(s, Tweet.get('keyword'))
                # print(s.entities)

                try:
                    dbMongo.Tweet.save(Tweet)
                    print(Tweet)
                except:
                    print("erreur tweet non importé:")
                    print(Tweet)
                    #######

                    # detect the language of the tweet
            '''
                try:
                    if s.lang is not None:
                        if s.lang == "en":
                            doc = nlp_en(Tweet.get('text'))
                        if s.lang == "fr":
                            doc = nlp_fr(Tweet.get('text'))

                        for index in range(0,len(doc)):
                            WordData = {'_id': Tweet.get('_id') + str(index), 'tweetid': s.id_str,
                                        'word': doc[index].text, 'word_root': doc[index].lemma_,
                                        'created_at': s.created_at, 'position': index,
                                        'word_type': doc[index].pos_,
                                        'import_date': datetime.date.today().strftime('%Y-%m-%d %H:%M')}

                            try:
                                if index == 0:
                                    WordData['prev_word'] = None
                                    WordData['next_word'] = doc[index+1].text
                                elif index == len(doc)-1:
                                    WordData['prev_word'] = doc[index-1].text
                                    WordData['next_word'] = None
                                else:
                                    WordData['prev_word'] = doc[index - 1].text
                                    WordData['next_word'] = doc[index + 1].text

                                print(WordData)
                                dbMongo.Word.save(WordData)
                            except:
                                print('index not working')
                except:
                    AttributeError

            '''

            dbMongo.Authors.update({'author_name': authorname}, {'$set': {'data_imported': True}})

            # print("Nombre de retweets:" + str(dbMongo.Tweet.count({'is_retweet': 0})))
            print("Nombre de tweets importés:" + str(dbMongo.Tweet.count({})))
            print("Nombre de tweets total:" + str(len(alltweets)))

        except :
            dbMongo.Authors.remove({'author_name' : authorname, 'origin':"keyword_search"})

    return alltweets

#à mettre dans le nouveau main

#list_of_old_authors = split_list_old_authors()
#list_of_new_authors = split_list_new_authors()
#print(list_of_old_authors)
#connectionsapi = [connectionAPI1(),connectionAPI2(),connectionAPI3()]


def clean_tweet(tweet):
    '''
    Utility function to clean tweet text by removing links, special characters
    using simple regex statements.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())


def get_tweet_sentiment(tweet):
    '''
    Utility function to classify sentiment of passed tweet
    using textblob's sentiment method
    '''
    # create TextBlob object of passed tweet text
    analysis = TextBlob(clean_tweet(tweet))
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

    #pool = ThreadPool(8)
    #lst_oldauthdat = split_list_authors(False, 4)
    #lst_newauthdat = split_list_authors(True, 4)
    #results1 = pool.starmap(get_list_TweetData, zip(itertools.repeat(connectionTwitterAPI()), lst_oldauthdat, itertools.repeat(import_week)))
    #results2 = pool.starmap(get_list_TweetData, zip(itertools.repeat(connectionTwitterAPI()), lst_newauthdat, itertools.repeat(import_all)))

    #lst_tweets = split_list_tweets()
    #results = pool.starmap(get_list_WordData, zip(lst_tweets, itertools.repeat("#teamarchi")))

def importtweets():

    lst_authors_new = dbMongo.Authors.find({'origin':"keyword_search", 'data_imported': True}).distinct('author_name')
    get_list_TweetData(connectionTwitterAPI(), lst_authors_new, import_week)
    lst_authors = dbMongo.Authors.find({'origin':"keyword_search", 'data_imported': False}).distinct('author_name')
    get_list_TweetData(connectionTwitterAPI(),lst_authors, import_all)

if __name__ == "__main__":
    importtweets()
