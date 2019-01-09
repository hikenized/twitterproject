import json
import pickle

with open('/home/ubuntu/PycharmProjects/Twitter/modifyDictionary/dictionary.txt', 'rb') as data:
    dictionary = pickle.load(data)
    section = dictionary[0]
    list_keywords = dictionary[1]

def remove_section():
    count=0
    count2 = 0
    for section_name in section:
        count += 1
        print(str(count) + " : " + section_name)
    trash_session_str = input("Numéro de la section à supprimer (si plusieurs, les séparer par une virgule):")
    trash_list = sorted(trash_session_str.replace(' ','').split(','), key=int, reverse=True)
    for item in trash_list:
        list_keywords[int(trash_session_str)-1].clear()
        section.remove(section[int(item)-1])
    print("Voici la nouvelle liste des sections:")
    for section_name in section:
        count2 += 1
        print(str(count2) + " : " + section_name)

    dictionary = [section, list_keywords]

    with open('/home/ubuntu/PycharmProjects/Twitter/modifyDictionary/dictionary.txt', 'wb') as output:
        pickle.dump(dictionary, output)

if __name__ == '__main__':
    print("Attention, supprimer une section supprimera tous les mots-clefs associés à celle-ci.")
    answer = input("Continuer? (o/n)")
    if (answer == "o" or answer == "oui"):
        remove_section()