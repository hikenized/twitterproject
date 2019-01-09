import json
import pickle

def add_keywords():

    #recuperation du dictionnaire existant
    try:
        with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
            dictionary = pickle.load(data)
            section = dictionary[0]
            list_keywords = dictionary[1]
    except FileNotFoundError:
        print("Le dictionnaire n'existe pas. Veuillez le créer en ajoutant une section.")
        exit()
    if not section:
        print("Pas de sections existantes. Veuillez d'abord créer une section.")
        exit()
    count=0
    for section_name in section:
        count += 1
        print(str(count) + " : " + section_name)
    session_selected = input("Veuillez entrer le numéro de section où vous souhaitez supprimer les mots-clefs:")
    if not list_keywords:
        list_keywords = [[]]
        keywords = []
    else:
        keywords = list_keywords[int(session_selected)-1]

    #suppression des mots-clefs
    print("Voici la liste des mots clefs de la section " + section[int(session_selected) - 1] + " : ")
    for motclef in list_keywords[int(session_selected) - 1]:
        print(motclef)
    trash_keywords = input("Nom du mot-clef à supprimer (si plusieurs, les séparer par une virgule) (pour tout supprimer, tapez \"all\"):")


    if trash_keywords=="all":
        keywords.clear()

    trash_keywords_list = trash_keywords.replace(', ',',').replace(' ,',',').split(',')
    for keyword in trash_keywords_list:
        if keyword in keywords:
            keywords.remove(keyword)
        else:
            print("Le mot clé \"" + keyword + "\" n'existe pas dans la section.")


    list_keywords[int(session_selected) - 1] = keywords

    if not keywords:
        print("Aucun mots-clefs dans la section " + section[int(session_selected) - 1] + ".")
    else:
        print("Voici la nouvelle liste des mots clefs de la section " + section[int(session_selected) - 1] + " : ")
        for motclef in list_keywords[int(session_selected) - 1]:
            print(motclef)

    print("Les sections sont:")
    for section_name in section:
        print(section_name)
    dictionary = [section, list_keywords]

    with open('/home/ubuntu/PycharmProjects/Twitter/modifyDictionary/dictionary.txt', 'wb') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    add_keywords()