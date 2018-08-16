# News Recommender version 2
# written by Max Reinisch

#
# This should be refactored code from the prototype.
# Possible to avoid using pandas?
# This should be easy to turn into an API endpoint
#

####################
##### IMPORTS ######
####################

import sys
import requests
import json
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine

####################
#### VARIABLES #####
####################

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
CALAIS_ENDPOINT = 'https://api.thomsonreuters.com/permid/calais'
CALAIS_TOKEN = "cvTFhY53VXBYm5HO85weHPx346W05015"
CALAIS_HEADER = {'X-AG-Access-Token' : CALAIS_TOKEN, 'Content-Type' : 'text/raw', 'outputformat' : 'application/json'}

def main():
    url = getArticleURL()
    article_response = requestArticle(url)
    article = parseArticle(article_response) # retrieve article contents as dict
    calais_json = getOpenCalaisResponse(article)
    entities = getSearchQuery(calais_json)
    GDELT_response = getDGELTv2Response(entities) #GDELT_response in JSON format
    clip_list = list(sortClipsBySimilarity(GDELT_response.get("clips"), article))
    for clip in sorted(clip_list, key = lambda x: x[1]):
        print(clip[0]['preview_url'])
        print("D =",clip[1])

def getArticleURL():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        print("Please enter the web address for a news article.")
        exit(-1)

def requestArticle(URL):
    print("Requesting article...")
    header = {"Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(URL, headers = header)
    print("Status Code:", res.status_code)
    if (res.status_code == 404):
        print("Requested page not found... Aborting.")
        exit(-1)
    else:
        return res

def parseArticle(res):
    # This parse currently works for Huffington Post articles.
    # This function will require further testing and will be subject to edits
    # Idea: make an article class
        # __init__() parses and sets class attributes
        # functions to print, run nlp, etc.
    soup = BeautifulSoup(res.content, 'lxml')
    title = soup.find("h1", attrs={"class":"headline__title"}).text
    try:
        subtitle = soup.find("div", attrs={"class":"headline__subtitle"}).text
    except:
        subtitle = ""
    author = soup.find("a", attrs={"class": "author-card__link yr-author-name"}).text
    body = "\n\n".join(list(map(lambda x: x.text,
        soup.find("div", attrs={"class":"entry__text"}).find_all("div",
        attrs={"class":"content-list-component"}))))

    article = {"title":title, "subtitle": subtitle, "author":author, "body":body}
    article = {key:value.replace('\u2015', '--').replace('\xa0', " ")
        for key, value in article.items()}

    return article

def getOpenCalaisResponse(article):
    response = requests.post(CALAIS_ENDPOINT, data=article['body'].encode('utf-8'), headers=CALAIS_HEADER, timeout=80)
    print("OpenCalais status code:", response.status_code)
    content = response.text

    c = json.loads(content)
    return c

def getSearchQuery(c):
    # This function is an unsolved problem.  How to find the best search query
    # Currently returns a list of all entities' names in order of number of mentions
    entities = [values for values in c.values() if values.get("_typeGroup") == "entities"]
    return [e['name'] for e in sorted(entities, key=lambda x: len(x['instances']), reverse=True)]

def getDGELTv2Response(entities):
    good_result = False
    entities = entities[:3]
    while(not good_result):
        if len(entities) ==0:
            print("Failed to find relevant TV News Clips... Aborting.")
            exit(-1)
        query = " ".join(entities)
        url = 'https://api.gdeltproject.org/api/v2/tv/tv?query='+query+ '%20market:%22National%22&mode=clipgallery&format=json&datanorm=perc&timelinesmooth=0&datacomb=sep&last24=yes&timezoom=yes&TIMESPAN=14days#'
        res = requests.get(url)

        gdelt_json = json.loads(res.text)
        if len(gdelt_json.keys()) ==0:
            entities = entities[0:-1]
        elif len(gdelt_json.get('clips')) < 5:
            entities = entities[0:-1]
        else:
            good_result = True
            print("search query:",query)
            print("GDELT status code:", res.status_code)
    return gdelt_json


def sortClipsBySimilarity(clips, article):
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2) )
    bow = vectorizer.fit_transform([clip.get('snippet') for clip in clips])
    article_bow = vectorizer.transform([article.get('body')])
    cosine_distances = [cosine(vec.todense(), article_bow.todense()) for vec in bow]

    # clips= [clip.update({'distance': distance}) for clip, distance in zip(clips, cosine_distances)]
    # return [clip.get('preview_url') for clip in sorted(clips, key=lambda x: x.get('distance'))]
    return zip(clips, cosine_distances)
main()
