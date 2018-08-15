# Article -> TV News clips Recommendation System
# Max Reinisch

#
# This program will return a list of TV news clips hosted on Archive.org that
# are related to a given news article (with a provided URL)
#

#imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import pairwise_distances, cosine_distances
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import json

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = 'https://www.huffingtonpost.com/entry/kansas-democrat-brent-welder-ad_us_5b625d65e4b0b15aba9f9774'
    search_result = getQueryFromArticle(url)
    video_list = getSuggestedTVNewsClips(search_result)


def getSuggestedTVNewsClips(search_result):
    """
    requests the GDELT API to get tv news clips, and then sorts them by relevance
    """

    #Requests GDELT
    successfulSearch = False
    people = search_result['POI']
    while(not successfulSearch):

        ### Tries the most specific search query that gets some result.
        query = " ".join(people)

        url = 'https://api.gdeltproject.org/api/v2/tv/tv?query='+query+ '%20market:%22National%22&mode=clipgallery&format=json&datanorm=perc&timelinesmooth=0&datacomb=sep&last24=yes&timezoom=yes&TIMESPAN=14days#'

        res = requests.get(url)


        gdelt_json = json.loads(res.text)
        if len(gdelt_json.keys()) ==0:
            people = people[0:-1]
        elif len(gdelt_json['clips']) < 5:
            people = people[0:-1]
        else:
            successfulSearch = True
            print("GDELT status code:", res.status_code)
            print("search query:",query)

    # Save GDELT result in dataframe
    df = pd.DataFrame(gdelt_json.get('clips'))

    # Vectorize snippets to bag of words
    snippet_matrix = df.snippet.as_matrix()
    snippet_matrix.put(0, search_result['document'])  # put article text in snippet matrix.  This is kinda hackey but gets the job done
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2) )
    bow = vectorizer.fit_transform(snippet_matrix)
    bow_df = pd.DataFrame(bow.todense(), columns=vectorizer.get_feature_names())

    # compute pairwize cosine distances
    distances = pairwise_distances(bow, metric='cosine')
    distance_df = pd.DataFrame(distances, index=bow_df.index, columns=bow_df.index)
    distance_df.head()

    # prints in order of most similar to article
    order = distance_df.loc[0, :].sort_values(ascending=True).index
    for i in order:
        print(df.loc[i, ["show", "preview_url"]]['preview_url'])



def getQueryFromArticle(article_url):
    """
    Takes in an article URL and returns its parsed contents, as well as a recommended search query
    """
    # openCalais
    access_token = "cvTFhY53VXBYm5HO85weHPx346W05015"
    calais_url = 'https://api.thomsonreuters.com/permid/calais'
    headers = {'X-AG-Access-Token' : access_token, 'Content-Type' : 'text/raw', 'outputformat' : 'application/json'}

    # article request
    url = article_url

    header = {"Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.get(url, headers=header )
    print("article status code:", res.status_code)
    if res.status_code == 403:
        print("Try changing User-Agent")
        exit(-1)
    elif res.status_code == 404:
        print("404, page not found")
        exit(-1)


    # Parsing article
    soup = BeautifulSoup(res.content, 'lxml')

    title = soup.find("h1", attrs={"class":"headline__title"}).text
    subtitle = soup.find("div", attrs={"class":"headline__subtitle"}).text
    author = soup.find("a", attrs={"class": "author-card__link yr-author-name"}).text
    body = "\n\n".join(list(map(lambda x: x.text, soup.find("div", attrs={"class":"entry__text"}).find_all("div", attrs={"class":"content-list-component"}))))


    # Using openCalais for entity extraction
    response = requests.post(calais_url, data=body.encode('utf-8'), headers=headers, timeout=80)
    print("OpenCalais status code:", response.status_code)
    content = response.text

    c = json.loads(content)
    topics = list(c.keys())[1:]

    tags = getEntities(c)

    df = pd.DataFrame(tags)

    # Select all people who were mentioned more than the mean number of mentions per person
    POI = list(df[(df["type"] == "Person") & (df['mentions'] > df[df['type'] =='Person']['mentions'].mean())]['commonname'])
    search_result = {"POI": POI, "document": body, "title": title, "subtitle": subtitle, "author": author}
    return search_result

def getEntities(c):
    """
    returns list of possible search query entities given the contents from
    OpenCalais response
    """

    tags = []

    for key, value in c.items():
        if value.get('_typeGroup') == "entities":
            new_entity = {}
            new_entity['name'] = value['name']
            new_entity['mentions'] = len(value['instances'])
            new_entity['type'] = value['_type']
            if(new_entity['type'] == "Person"):
    #             print(new_entity['name'])
                new_entity['commonname'] = value['commonname']
            else:
                new_entity['commonname'] = ""
            tags.append(new_entity)
    return tags


main()
