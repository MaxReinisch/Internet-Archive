# This python file is to test the use of newspaper3k for news article parsing
# Max Reinisch


from newspaper import Article, fulltext
import requests


# url = 'https://www.huffingtonpost.com/entry/alex-jones-infowars-app-apple-google_us_5b694ec3e4b0de86f4a4bc1d'
url = 'https://www.nytimes.com/2018/08/09/us/politics/kansas-kobach-colyer-votes.html'

def attempt1():
    huffpo = Article(url)

    huffpo.download()
    huffpo.parse()

    print(huffpo.authors)

    print()
    print(huffpo.text)

    print()
    huffpo.nlp()
    print(huffpo.keywords)

def attempt2():
    header = {"Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    html = requests.get(url, headers=header).text
    text = fulltext(html)
    print(text)
# attempt1() # Did not deliver full text

attempt1()
