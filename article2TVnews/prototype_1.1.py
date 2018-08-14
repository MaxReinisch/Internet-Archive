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
    # for video_url in video_list:
    #     print(video_url)

def getSuggestedTVNewsClips(search_result):
    query = " ".join(search_result['POI'])

    url = 'https://api.gdeltproject.org/api/v2/tv/tv?query='+query+ '%20market:%22National%22&mode=clipgallery&format=json&datanorm=perc&timelinesmooth=0&datacomb=sep&last24=yes&timezoom=yes&TIMESPAN=14days#'

    res = requests.get(url)
    print("api status code:", res.status_code)
    df = pd.DataFrame(json.loads(res.text)['clips'])

    snippet_matrix = df.snippet.as_matrix()
    snippet_matrix.put(0, search_result['document'])
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2) )
    bow = vectorizer.fit_transform(snippet_matrix)
    bow_df = pd.DataFrame(bow.todense(), columns=vectorizer.get_feature_names())

    distances = pairwise_distances(bow, metric='cosine')
    distance_df = pd.DataFrame(distances, index=bow_df.index, columns=bow_df.index)
    distance_df.head()

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
    print(res.status_code)
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
    content = response.text

    c = json.loads(content)

    tags = getTags(c)

    df = pd.DataFrame(tags)

    # Select all people who were mentioned more than the mean number of mentions per person
    POI = list(df[(df["type"] == "Person") & (df['mentions'] > df[df['type'] =='Person']['mentions'].mean())]['commonname'])
    search_result = {"POI": POI, "document": body, "title": title, "subtitle": subtitle, "author": author}
    return search_result

def getTags(c):
    """
    returns list of possible search query entities given the contents from
    OpenCalais response
    """
    topics = list(c.keys())[1:]
    tags = []
    for topic in topics:
        if c[topic]['_typeGroup'] == "entities":
            new_entity = {}
            new_entity['name'] = c[topic]['name']
            new_entity['mentions'] = len(c[topic]['instances'])
            new_entity['type'] = c[topic]['_type']
            if(new_entity['type'] == "Person"):
    #             print(new_entity['name'])
                new_entity['commonname'] = c[topic]['commonname']
            else:
                new_entity['commonname'] = ""
            tags.append(new_entity)
    return tags


main()
