import re
import json
import requests
import tokenizer
import mysql.connector
from bs4 import BeautifulSoup
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


# save data (id, title, url, html, size) of a web page to database
def save_data(_title, _url, _html, _images, _size):
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = "INSERT INTO websites (title, url, html, images, size) VALUES(%s, %s, %s, %s, %s)"
        val = (_title, _url, _html, _images, _size)
        cursor.execute(query, val)
        cnx.commit()
        cnx.close()
        # print("\033[92mSAVED\033[0m")
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# initializer for database
# the url field should be 2048 bytes (chrome url limit) long but due to mysql 5.5 limitation
# while using utf8 encoding, it has been set to 200 bytes (might have been solved in newer mysql versions,)
def start_data():
    try:
        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root')
        cursor = cnx.cursor()
        query = "CREATE DATABASE IF NOT EXISTS uu_search;"
        cursor.execute(query)
        cnx.commit()
        cnx.close()

        cnx = mysql.connector.connect(user='root', host='127.0.0.1', password='root', database='uu_search')
        cursor = cnx.cursor()
        query = "CREATE TABLE IF NOT EXISTS websites (" \
                "title nvarchar(200) NOT NULL, " \
                "url NVARCHAR(200) PRIMARY KEY," \
                "html MEDIUMTEXT, " \
                "images MEDIUMTEXT, " \
                "size INT) default charset=utf8"
        cursor.execute(query)
        cnx.commit()
        cnx.close()
        print("Database was initialized successfully.\n")
    except mysql.connector.Error as err:
        print("Error acquired;", err)


# initialize database
# start_data()

# how many links to crawl
LINK_COUNT = 10

# outputs that will be saved to a file
output_tokens = {}
output_images = {}

# starting url
urls = ["https://www.urmia.ac.ir/"]

# for https/http removal thing
final_urls = []

# elastic search initializer
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
# es.delete(index='urmia.ac_pages', id=1)
# es.delete(index='urmia.ac_images', id=1)
doc_id = 0
image_doc_id = 0

# create request url by getting html
i = 0
while True:

    # end process at given link count
    if LINK_COUNT <= 0:
        break
    LINK_COUNT -= 1

    html = ""
    try:
        html = str(requests.get(urls[i]).text)
    except requests.exceptions.RequestException as err:
        continue

    soup = BeautifulSoup(html, "html.parser")

    # update urls with new links (links in the current web page)
    links = set(soup.findAll("a"))
    for link in links:
        link_string = link.get("href")
        if link_string is None:
            continue
        elif re.findall(r".*urmia\.ac.*", link_string):
            temp_url = re.sub(r"\$", "", str(link.get("href")))
            urls.append(temp_url)
            final_urls.append(temp_url)
            # print(link.get("href"))
    i += 1

urls = set(urls)


# remove "https" equivalent "http" links
kill_urls = set()
final_urls = set(final_urls)
for item in urls:
    if item in kill_urls:
        continue
    for other_item in urls.difference([item]):
        if re.sub(r"http:", "", item) == re.sub(r"https:", "", other_item):
            final_urls.remove(item)
            kill_urls.add(item)

# crawler
for url in final_urls:

    # create request url and get html
    html = ""
    try:
        if re.findall(r"^http|https", url):
            html = str(requests.get(url).text)
        else:
            continue
    except requests.exceptions.RequestException as err:
        print(BColors.FAIL + "Error has acquired while requesting web page.\n" + BColors.ENDC + str(err))
        print()
        continue

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as err:
        print(err)
        continue
    except BaseException as err:
        print(err)
        continue
    # print(soup)

    # get all images links in a web page
    images = set(soup.findAll("img"))
    new_images = set()
    for image in images:
        if re.findall(r"png|jpg", str(image.get("src"))):
            if re.findall(r"^http|https", image.get("src")):
                if re.findall(r"urmia.ac.ir", image.get("src")):
                    new_images.add(image.get("src"))
    output_images[url] = new_images

    # get title of the web page
    title = str(soup.findAll("title"))
    title = re.sub(r"\[<title>|</title>\]", "", title)
    # print(title)
    if title == "[]":
        continue

    # tokenize the web page ({word: count, word2: count2})
    out = tokenizer.start_tokenizer(html)
    # print(out)

    # create real output ({word: {doc1: count1, doc2: count2}, word2: {doc2: count2, doc3: count3}})
    # using req_url as id(doc1/doc2/...)
    for key in out.keys():
        if key in output_tokens.keys():
            output_tokens[key][url] = out[key]
        else:
            output_tokens[key] = {url: out[key]}

    # save data to database
    # save_data(title, url, html, str(new_images), len(html))
    # print(title, url)

    try:
        # elastic search [pages]
        doc = {
            'title': title,
            'body': html,
            'url': url
        }
        es.index(index='urmia.ac_pages', id=doc_id, document=doc)
        doc_id += 1

        # elastic search [images]
        for image_url in new_images:

            image_doc = {
                'title': title,
                'body': html,
                'url': image_url
            }
            es.index(index='urmia.ac_images', id=image_doc_id, document=image_doc)
            image_doc_id += 1
    except Exception as err:
        print(err)


# save tokens to one single file
tokens_file = open("tokens_file.txt", "w", encoding='utf8')
tokens_file.write(json.dumps(output_tokens))
tokens_file.close()

# save images to a single file
# images_file = open("images_file.txt", "w", encoding='utf8')
# images_file.write(str(output_images))
# images_file.close()

# create tokens for spell checking
spell_tokens = {}
for token in output_tokens:
    spell_tokens[token] = sum(output_tokens[token].values())

# save spell checking tokens
s_t = open("spell_tokens.txt", "w", encoding='utf8')
s_t.write(json.dumps(spell_tokens))
s_t.close()
