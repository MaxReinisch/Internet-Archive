# Article to TV News clips

- [files](#files)
- [how it works](#hiw)
- [instructions](#instructions)
- [todo](#todo)

<a id='files'></a>
### Files:

- The jupyter notebook files (.ipynb) are used for testing.  
- `prototype_1.1.py` is a proof of concept.  Mostly spaghetti code
- All relevant code has been refactored into `NewsRecommenderV2.py`.

<a id='hiw'></a>
### How It Works:

- Requests news article URL
  - extracts `title`, `author`, `fulltext`, etc
- Requests `OpenCalais` for NLP entity extraction
  - generates search query using entities
- Requests `GDELT` using search query
  - results include TV news clips
  - sort news clips using cosine distance between article text and TV closed captions


<a id='instructions'></a>
### Instructions:

To run the program, simply call:


`python NewsRecommenderV2.py <article_url>`



Currently, the program only works with huffingtonpost articles.  This will be
extended later on.  
<a id='todo'></a>
### TODO:
- We currently need a way to parse news articles
  - Stackoverflow had some [ideas](https://stackoverflow.com/questions/30356069/extract-news-article-content-from-stored-html-pages)
- We are looking for a more optimal way to query for news clips.  Entity extraction is a good start, but it has issues
