import json
import pickle

def add_complements():

    #get data from existing dictionary
    try:
        with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'rb') as data:
            dictionary = pickle.load(data)
            section = dictionary[0]
            list_keywords = dictionary[1]
            list_complements = dictionary[2]

    #if no dictionary, ask user to create one
    except FileNotFoundError:
        print("Le dictionnaire n'existe pas. Veuillez le créer en ajoutant une section.")
        exit()

    #if no sections, ask user to create one
    if not section:
        print("Pas de sections existantes. Veuillez d'abord créer une section.")
        exit()

    countsection=0
    #ask for the section where the user wants to add complement keywords
    for section_name in section:
        countsection += 1
        print(str(countsection) + " : " + section_name)
    session_selected = input("Veuillez entrer le numéro de section comportant le mot-clé où vous souhaitez ajouter le(s) complément(s):")
    #keep asking the user for an integer in the range of the list as long as he enters anything else
    while True:
        try:
            while (int(session_selected) > countsection or int(session_selected) < 0):
                session_selected = input("Veuillez entrer un numéro de section entre 1 et " + str(countsection) + " :")
            break
        except:
            session_selected = input("Veuillez entrer un entier:")


    #if no keywords in the section, ask user to add keywords first
    try:
        if len(list_keywords[int(session_selected)-1]) == 0:
            #print("La section ne comporte aucun mot-clé. Veuillez d'abord ajouter des mots-clés dans la section.")
            exit()
    except:
        print("La section ne comporte aucun mot-clé. Veuillez d'abord ajouter des mots-clés dans la section.")
        exit()

    countkeyword=0

    #try to display the keywords from the section selected by the user
    try:
        for keyword_name in list_keywords[int(session_selected)-1]:
            countkeyword += 1
            print(str(countkeyword) + " : " + keyword_name)

        # ask the keyword where the user wants to add a complement word
        keyword_selected = input("Veuillez entrer le numéro du mot clé où vous souhaitez ajouter des compléments:")
        #keep asking the user for an integer in the range of the list as long as he enters anything else
        while True:
            try:
                while (int(keyword_selected) > countkeyword or int(keyword_selected) < 0):
                    keyword_selected = input("Veuillez entrer un numéro de section entre 1 et " + str(countkeyword) + " :")
                break
            except:
                keyword_selected = input("Veuillez entrer un entier:")

        if not list_keywords:
            list_keywords = [[]]
        while len(list_keywords)<int(session_selected):
            keywords = []
            list_keywords.append(keywords)
        keywords = list_keywords[int(session_selected)-1]

    # if no keywords in the section, ask user to add keywords first
    except:
        print("La section ne comporte aucun mot-clé. Veuillez d'abord ajouter des mots-clés dans la section.")
        exit()

    #create empty lists to store the complement at the right place
    if not list_complements:
        lt_complements=[[]]
        list_complements = [lt_complements]
    while len(list_complements) < len(section):
        lt_complements=[]
        list_complements.append(lt_complements)
    lt_complements = list_complements[int(session_selected) - 1]
    print(len(lt_complements))
    print(keyword_selected)
    print(lt_complements)
    while len(lt_complements) < len(list_keywords[int(session_selected)-1]):
        complements = []
        lt_complements.append(complements)
    lt_complements = list_complements[int(session_selected) - 1]
    print(lt_complements)
    complements = lt_complements[int(keyword_selected) - 1]

    #display existing complements for the keyword selected by the user
    print("Liste des compléments existants pour le mot-clé " + keywords[int(keyword_selected)-1] + " :")
    for complement in lt_complements[int(keyword_selected) - 1]:
        print(complement)

    #ask for new complements to add
    new_complement = input("Nom du complément à ajouter (si plusieurs, les séparer par une virgule):")
    new_complement_list = new_complement.replace(', ',',').replace(' ,',',').split(',')
    for complement in new_complement_list:
        if complement not in complements:
            complements.append(complement)
        else:
            print("Le complément \"" + complement + "\" existe déjà pour ce mot clé.")
            exit()
    lt_complements[int(keyword_selected) - 1] = complements
    list_complements[int(session_selected) - 1] = lt_complements
    print("Les nouveaux compléments de la section " + section[int(session_selected) - 1] + " pour le mot-clé " + keywords[int(keyword_selected)-1] + " sont : ")
    for complement in lt_complements[int(keyword_selected) - 1]:
        print(complement)
    print("Les sections sont:")
    for section_name in section:
        print(section_name)
    dictionary = [section, list_keywords, list_complements]

    #write the information in the new dictionary
    with open('/home/ubuntu/PycharmProjects/TweetArchi/modifyDictionary/dictionary.txt', 'wb') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    add_complements()