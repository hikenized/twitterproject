import json
import pickle
import os.path

def add_section():

    #if the dictionary exists, load it. Else, create an empty dictionary to add sections in it
    if os.path.isfile('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt'):
        with open('dictionary.txt', 'rb') as data:
            dictionary = pickle.load(data)
            section = dictionary[0]
            list_keywords = dictionary[1]
            list_complements = dictionary[2]
    else:
        section = []
        list_keywords=[]
        list_complements=[]


    #add the sections' name to the dictionary
    new_section = input("Nom de la section à ajouter (si plusieurs, les séparer par une virgule):")
    new_section_list = new_section.replace(', ',',').replace(' ,',',').split(',')
    for item in new_section_list:
        section.append(item)
    print("Voici la liste des sections:")
    for section_name in section:
        print(section_name)
    dictionary = [section, list_keywords, list_complements]

    with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'wb') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    add_section()