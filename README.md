# research-gate-crawler
Crawling [ResearchGate](https://www.researchgate.net/) papers' Title & Abstract info and written into a CSV file.

### Introduction
In default, the crawler will retrieve all articles with below strategy:
- Only Article, not Conference Paper, Project, or any else
- The Article must contain one of the term in the string: `drone uav remote-sensing "remote sensing"`
- The Article must have Abstract
- The Article must have Announced date from year 2000

### Modifying crawling parameters
You may visit https://www.researchgate.net/search.Search.html?type=publication&query=drone%20uav%20remote-sensing to figure out all possible params
```python
# crawler.py
base_url = 'https://www.researchgate.net/search.SearchBox.loadMore.html'

# Keywords used to search papers
# Looks like the query operator is OR,
# eg., searching 'drone' returns totalItems=7467, whereas, searching 'drone uav' returns totalItems=28388
terms = 'drone uav remote-sensing "remote sensing"'

# Searching Publications, not Authors or Reviews...
search_type = 'publication'
# Type of publication we need to search is Article, not Conference Paper, Posters, or Others...
publication_type = 'article'

# From experiments, the max items we can crawl for each request is 300
limit = 300
```

#### Notice: 
- From our tests, limitation for crawling is 300 items in each request.
- Besides, there is Request time-rate limitation. By adding `cookies`, we can bypass this kind of error.

### Launch the crawler

```sh
$ python crawler.py
Fetching 300/178863 (0%)
https://www.researchgate.net/search.SearchBox.loadMore.html?query=drone+uav+remote-sensing+%22remote+sensing%22&type=publication&subfilter%5BpublicationType%5D=article&offset=300&limit=300
retrieved (192) & ignored (108)
...
```

### Results
csv files, that support UTF-8 encoding, named `ResearchGate-YYYY-YYYY-MM-DD.csv` will be created in the same location of the crawlers/caller

In which, 
- The first `YYYY` is the announced year of publications.
- `YYYY-MM-DD` is the crawling date.

Ex., 
- `ResearchGate-2007-2020-01-06.csv`
- `ResearchGate-2008-2020-01-06.csv`
- ...

## Data Collection (How-to)
- The crawled data was taken on Jan 10, 2020 (2020-Jan-10.zip)
- The results are 21 CSV files for keywords `drone uav remote-sensing "remote sensing"`. Each CSV is for one year, from 2000 to 2020.
- There are `178968` articles in total
- There are `131180 (73.3%)` articles collected and placed into their appropriate CSV
- And, `47788 (26.7%)` articles were ignored because of un-matched criteria (from year 2000 and must have the abstract)

### Technology
The Crawler uses [requests](https://pypi.org/project/requests/) library to send a `GET` query to get the needed information returned in JSON format.

## Future work
Figure out to extract Keywords from Title & Abstract

**I am welcome any effort to enhance this open-source project.**

**Thank you.**