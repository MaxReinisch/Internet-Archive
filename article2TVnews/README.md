# Article to TV News clips

- [files](#files)
- [instructions](#instructions)
- [todo](#todo)

<a id='files'></a>
### Files:

The jupyter notebook files (.ipynb) are used for testing.  All relevant code
has been refactored into `prototype_1.1.py`.
<a id='instructions'></a>
### Instructions:

To run the program, simply call:


`python prototype_1.1.py <article_url>`



Currently, the program only works with huffingtonpost articles.  This will be
extended later on.  
<a id='todo'></a>
### TODO:
- We currently need a way to parse news articles
  - Stackoverflow had some [ideas](https://stackoverflow.com/questions/30356069/extract-news-article-content-from-stored-html-pages)
- We are looking for a more optimal way to query for news clips.  Entity extraction is a good start, but it has issues
