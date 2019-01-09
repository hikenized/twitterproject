
import pickle
import datetime
from connections import connectionTwitterAPI, connectionMongoDB
import os
import csv

words_architect = ['teamarchi', 'architect', 'urbanist', 'dplg', 'd.p.l.g', 'design']
words_enterprise = ['manufactur', 'facility', 'firm', 'filiale', 'enterprise']
words_association = 'associat'
words_construction = 'construc'
words_agence = 'agenc'
words_journalist = ['journalist', 'media', 'presse', 'editor', 'redact', 'magazine']
words_ecole = ['etudiant', 'student', 'ecole', 'education', 'enseignant', 'professor', 'professeur', 'formateur',
               'ecole nationale superieure']
words_director = ['directeur', 'director', 'directrice', 'ceo']
words_photo = ['photo', 'photograph']
words_communication = ['presse', 'media', 'communicat']

# open the dictionary to import the list of keywords to search
with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
    dictionary = pickle.load(data)
    section = dictionary[0]
    list_keywords = dictionary[1]


# get a list of the last tweets, length of list determined by nbloop = the number of loops
def get_list_tweetdata(query, connection):
    alltweets = []
    statuses = connection.search(q=query, count=100)
    alltweets.extend(statuses)
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until last week
    i = 0

    # while i < nbloop:


    while alltweets[-1].created_at >= (datetime.datetime.today() - datetime.timedelta(days=7)):
        print("getting tweets before %s" % (oldest,))

        # all subsiquent requests use the max_id param to prevent duplicates
        statuses = connection.search(q=query, count=100, max_id=oldest)

        # save most recent, "screenname" : "degioanni", "numberofretweets" : 2, "author_id" : 17514448 t tweets
        alltweets.extend(statuses)

        if (alltweets[-1].id - 1 == oldest):
            break

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        i = i + 1
        print("...%s tweets downloaded so far" % (len(alltweets),))

    return alltweets


def saveAuthor(s, dbMongo, origin):
    if dbMongo.Authors.count({'authorid': s.author.id_str}) == 0 or origin == "keyword_search" and dbMongo.Authors.count({'_id': s.author.id_str + datetime.date.today().strftime('%Y-%m')}) == 0 :
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
                  'contributors_enabled': s.author.contributors_enabled,
                  'profile_background_color': s.author.profile_background_color,
                  # 'background_img_http': s.author.profile_background_image_url,
                  'background_img': s.author.profile_background_image_url_https,
                  'nb_faces_profile': 0, 'tile': 0, 'nb_colors_profile': 0,
                  'nb_chars_profile': 0,
                  'profile_background_tile': s.author.profile_background_tile,
                  # 'profile_img_http': s.author.profile_image_url.replace('_normal', ''),
                  'profile_img': s.author.profile_image_url_https.replace('_normal', ''),
                  # 'profile_link_color': s.author.profile_link_color,
                  # 'profile_sidebar_border_color': s.author.profile_sidebar_border_color,
                  # 'profile_sidebar_fill_color': s.author.profile_sidebar_fill_color,
                  'profile_text_color': s.author.profile_text_color,
                  'profile_use_background_image': s.author.profile_use_background_image,
                  'default_profile': s.author.default_profile,
                  'default_profile_img': s.author.default_profile_image,
                  'data_imported': False,
                  'class': "1",
                  'origin': origin,
                  'import_date_author': datetime.date.today().strftime('%Y-%m-%d %H:%M')
                  }
        try:
            Author['withheld_in_countries'] = s.author.withheld_in_countries
        except:
            Author['withheld_in_countries'] = None

        try:
            Author['profile_banner_url'] = s.author.profile_banner_url
        except:
            Author['profile_banner_url'] = None

        try:
            Author['withheld_scope'] = s.author.withheld_scope
        except:
            Author['withheld_scope'] = None

        '''
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
                find_quoted = dbMongo.Authors.find({'_id': "q" + Author.get('authorid')})
                for quoted in find_quoted:
                    if quoted.get('quoted_times'):
                        print(quoted)
                        quoted['quoted_times'] = quoted.get('quoted_times') + 1
                        dbMongo.Authors.save(quoted)
                        return None

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
                find_replied = dbMongo.Authors.find({'_id': "rp" + Author.get('authorid')})
                for replied in find_replied:
                    if replied.get('replied_times'):
                        print(replied)
                        replied['replied_times'] = replied.get('replied_times') + 1
                        dbMongo.Authors.save(replied)
                        return None

        # store retweeted authors
        elif origin == "retweeted_author":
            del Author['data_imported']
            Author['_id'] = "rt" + Author.get('authorid')
            if dbMongo.Authors.count({'_id': "rt" + Author.get('authorid')}) == 0:
                Author['retweeted_times'] = 1
            else:

                find_retweeted = dbMongo.Authors.find({'_id': "rt" + Author.get('authorid')})
                print(type(find_retweeted))
                print(len(find_retweeted))
                for retweeted in find_retweeted:
                    if retweeted.get('retweeted_times'):
                        print(retweeted)
                        retweeted['retweeted_times'] = retweeted.get('retweeted_times') + 1
                        dbMongo.Authors.save(retweeted)
                        return None

        '''

        # get data of interesting users every months, (or every week by uncommenting the line below)
        if origin == "keyword_search":
            Author['_id'] += datetime.date.today().strftime(
                '%Y-%m')  # + '-w' + str(int(int(datetime.date.today().strftime('%d'))/8)%4)
            if dbMongo.Authors.count({'_id': Author.get('_id')}) == 0:
                Author['keyword_times'] = 0

            '''
            else:
                find_keywords = dbMongo.Authors.find({'_id': Author.get('_id') })
                for keyword in find_keywords:
                    Author['keyword_times'] = keyword.get('keyword_times') + 1
            '''

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


def get_collections_data(list_tweet, query, dbMongo):
    # get from tweet : author name, keyword used, number of times the tweet has been liked, retweeted, quoted, replied
    for s in list_tweet:

        saveAuthor(s, dbMongo, "keyword_search")

        if dbMongo.AuthorKeys.count({'authorid': s.author.id_str, 'authorkw': query}) == 0:

            keysection = ''
            # get the section of the current keyword
            countitem = 0
            for keywords in list_keywords:
                for key in keywords:
                    if key == query:
                        keysection = section[countitem]
                countitem += 1

            AuthorKeywords = {'_id': keysection + query + s.author.id_str, 'authorid': s.author.id_str,
                              'author_name': s.author.screen_name, 'authorsectionkw': keysection, 'authorkw': query}

            dbMongo.AuthorKeys.save(AuthorKeywords)

    print("Nombre d'auteurs importés: " + str(dbMongo.Authors.count({})))

    print("Nombre d'auteurs / motsclés: " + str(dbMongo.AuthorKeys.count({'authorkw': query})))


# à mettre dans le nouveau main

def importauthors(dbMongo):
    for keyword in list_keywords:
        if dbMongo.Authors.count(
                {'import_date_author':
                     {"$regex": datetime.date.today().strftime('%Y-%m-%d')}}) < 10:
            for word in keyword:
                print(word)
                list_tweet = get_list_tweetdata(word, connectionTwitterAPI())
                get_collections_data(list_tweet, word, connectionMongoDB())


if __name__ == '__main__':
    print('WHAT')
    importauthors(connectionMongoDB())

# modify description and location attributes to respect csv output rules

'''
liste_aut = connectionMongoDB().Authors.find({'description': {"$regex": ","}})

for auteur in liste_aut :
    auteur['description'] = auteur.get('description').replace(",", " ").replace("\n", " ")
    connectionMongoDB().Authors.save(auteur)

liste_aut2 = connectionMongoDB().Authors.find({'description': {"$regex": "\n"}})

print("---------------------------------")

for auteur2 in liste_aut2:
    auteur2['description'] = auteur2.get('description').replace("\n", " ")
    print(auteur2)
    connectionMongoDB().Authors.save(auteur2)


liste_aut3 = connectionMongoDB().Authors.find({'location': {"$regex": ","}})

for auteur3 in liste_aut3:
    auteur3['location'] = auteur3.get('location').replace(",", " ")
    print(auteur3)
    connectionMongoDB().Authors.save(auteur3)



list_media = connectionMongoDB().Media.find({'tweetid':None})

for media in list_media:
    if media.get('_id')[0] == "m" or media.get('_id')[0] == "h":
        media['mediaid'] = media.get('_id')[:-1][1:]
    else:
        media['tweetid'] = media.get('_id')[:-1]
    connectionMongoDB().Media.save(media)

'''

# os.system('''mongoexport --db TwitterSearchData --collection Tweet --type csv --fields _id,created_at,tweetid,text,source,truncated,in_reply_to_status_str,in_reply_to_user_id,author_name,authorid,coordinates,place,is_quote,nb_retweeted,nb_likes,section,keyword,lang,complement,import_date,country,city,coordinates,rt_originaltweetid,rt_originalauthorname,sentiment,reply_to_screen_name,quoted_status_id_str,quoted_status_authorid,quoted_status_author_name,quote_count,reply_count --out tweets.csv''')
# os.system('''mongoexport --db TwitterSearchData --collection Authors--type csv --fields _id,authorid,author_name,location,user_url,description,nb_followers,nb_friends,nb_lists,nb_liked,nb_tweets,created_at,country,profile_img,class,origin,import_date_author --out authors.csv''')
# os.system('''mongoexport --db TwitterSearchData --collection AuthorKeys --type csv --fields _id,authorid,author_name,authorsectionkw,authorkw --out authorkeys.csv''')
# os.system('''mongoexport --db TwitterSearchData --collection Media --noHeaderLine --fields _id,media_type,media_url --out media.csv''')
# os.system('''mongoexport --db TwitterSearchData --collection WordData --type csv --fields _id,tweetid,word,wordroot,wordclear,prev_word,next_word,created_at,position,is_mention,is_hashtag,word_type,is_retweet,selectedword,import_date --out worddata.csv''')



# change the delimitor for tweetdata, because the text contains commas
# os.system('''mongoexport --db TwitterSearchData --collection TweetData --type csv --fields nb_likes,is_quote --out tweetsdata.csv''')

'''
reader = csv.reader(open("tweetsdata.csv", "rU"), delimiter=',')
writer = csv.writer(open("tweetsdata_v2.csv", 'w'), delimiter='~')
writer.writerows(reader)

'''