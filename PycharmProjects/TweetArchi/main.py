import pickle
from AuthorImport import importauthors
from TweetImport import importtweets
from connections import connectionMongoDB

# open the dictionary to import the list of keywords to search
with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
    dictionary = pickle.load(data)
    section = dictionary[0]
    list_keywords = dictionary[1]

if __name__ == '__main__':
    # for each keyword, search and save every data (authors, tweets, words) in MongoDB
    importauthors(connectionMongoDB())
    importtweets()

