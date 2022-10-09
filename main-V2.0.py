import spell_correction
import mysql.connector
from elasticsearch import Elasticsearch


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# get data from database b title and URL
def load_data(_title, _url):
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = "SELECT * FROM websites where title = %s and url = %s"
        val = (_title, _url)
        cursor.execute(query, val)
        cnx.commit()
        cnx.close()
        return cursor
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# update data in data base (find by title and url - data by html)
def update_data(_title, _url, _html):
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = "UPDATE websites SET html = %s where title = %s and url = %s"
        val = (_html, _title, _url)
        cursor.execute(query, val)
        cnx.commit()
        cnx.close()
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# delete data by title and url
def delete_data(_title, _url):
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = "DELETE FROM websites WHERE title = %s and url = %s"
        val = (_title, _url)
        cursor.execute(query, val)
        cnx.commit()
        cnx.close()
        print("DATA HAS BEEN DELETED")
        return 1
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# send your direct query to database (string)
def direct_query_db(_query):
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = _query
        cursor.execute(query)
        cnx.commit()
        cnx.close()
        return cursor
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# search for web pages
def search_websites(_input):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    res = es.search(index='urmia.ac_pages', query={
        "bool": {
            "must": [
                {"multi_match": {
                    "query": _input,
                    "fields": ["title", "body"]
                }}
            ]
        }
    }
                    )
    return res


# search for images
def search_images(_input):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    res = es.search(index='urmia.ac_images', query={
        "bool": {
            "must": [
                {"multi_match": {
                    "query": _input,
                    "fields": ["title", "body"]
                }}
            ]
        }
    }
                    )
    return res


# loading stop words into script
# print(BColors.OKCYAN + "\nPlease wait while loading stop words..." + BColors.ENDC)
sw = open("stop_words.txt", "r", encoding='utf-8')
stop_words = sw.read()
sw.close()
# print(BColors.OKGREEN + "Stop Words loaded successfully.\n" + BColors.ENDC)

# get user input as a string
input_word = input("INPUT: ")

# split input words
input_word = input_word.split(" ")

# check for miss spell in words (and remove stop words)
for j, word in enumerate(input_word):

    # check word for miss spell
    spelled_word = spell_correction.spell_check(word)

    # ask user the probable right form
    if spelled_word != 1 and len(spelled_word) > 0:
        print(BColors.FAIL + "There might be a misspell in your query word: " + BColors.ENDC + word)
        i = 0
        for i, item in enumerate(spelled_word):
            print(str(i + 1) + ". " + item)

        # get user input to fix and replace the correct word
        choose_spell = int(input(BColors.WARNING + "Which one did you mean: (To skip enter 0)\n" + BColors.ENDC))
        if choose_spell != 0:
            input_word[j] = spelled_word[choose_spell - 1]

# coming soon...
query_word = ""
for word in input_word:

    # remove stop words
    if word in stop_words:
        continue
    query_word += word
    query_word += " "

# search_res = search_websites(query_word)
# print(type(search_res))
# for doc in search_res['hits']['hits']:
#     print("%s) %s %s %s" % (doc['_id'], doc['_source']['url'], doc['_source']['body'], doc['_source']['title']))
