import json
import pickle

def add_keywords():

    #get the dictionary data
    try:
        with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
            dictionary = pickle.load(data)
            section = dictionary[0]
            list_keywords = dictionary[1]
            list_complements = dictionary[2]
    #if no existing dictionary, create it first by running addSection
    except FileNotFoundError:
        print("Le dictionnaire n'existe pas. Veuillez le créer en ajoutant une section.")
        exit()
    #if no sections in the dictionary, create one by running addsection
    if not section:
        print("Pas de sections existantes. Veuillez d'abord créer une section.")
        exit()

    #print the list of all the sections in the dictionary
    count=0
    for section_name in section:
        count += 1
        print(str(count) + " : " + section_name)

    #ask the user in which section he want to add keywords
    session_selected = input("Veuillez entrer le numéro de section où vous souhaitez ajouter les mots-clefs:")
    #keep asking the user for an integer in the range of the list as long as he enters anything else
    while True:
        try:
            while (int(session_selected) > count or int(session_selected) < 0):
                session_selected = input("Veuillez entrer un numéro de section entre 0 et " + str(count) + " :")
            break
        except:
            session_selected = input("Veuillez entrer un entier:")

    #if there are no keywords, create the list
    if not list_keywords:
        list_keywords = [[]]
    #create an empty list of keywords for each section
    while len(list_keywords)<int(session_selected):
        keywords = []
        list_keywords.append(keywords)
    keywords = list_keywords[int(session_selected)-1]


    #add the keywords to the selected section
    print("Liste des mots-clefs existants dans la section " + section[int(session_selected)-1] + " :")
    for motclef in list_keywords[int(session_selected) - 1]:
        print(motclef)
    new_keywords = input("Nom du mot-clef à ajouter (si plusieurs, les séparer par une virgule):")
    new_keywords_list = new_keywords.replace(', ',',').replace(' ,',',').split(',')
    for keyword in new_keywords_list:
        if keyword not in keywords:
            keywords.append(keyword)
        else:
            print("Le mot clé existe déjà dans la section.")
            exit()
    list_keywords[int(session_selected) - 1] = keywords
    print("Les nouveaux mots clefs de la section " + section[int(session_selected) - 1] + " sont : ")
    for motclef in list_keywords[int(session_selected) - 1]:
        print(motclef)
    print("Les sections sont:")
    for section_name in section:
        print(section_name)
    dictionary = [section, list_keywords, list_complements]

    with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'wb') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    add_keywords()