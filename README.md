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

limit = 300
```
#### Notice: 
- From my test, request around 300 items in each request is reasonable. Increase the number to 400 may return errors.
- Besides, there is Request time-rate limitation. Keep sending crawling requests in short time may trigger API server to block your IP.
To avoid that case, a break time of 60-second between two requests is added `time.sleep(60)`.

### Launch the crawler

```sh
$ python crawler.py
Fetching 0...
https://www.researchgate.net/search.SearchBox.loadMore.html?type=publication&subfilter%5BpublicationType%5D=article&query=drone%20uav%20remote-sensing%20%22remote%20sensing%22&offset=0&limit=10
Retrieved paper = 1
Retrieved paper = 2
Retrieved paper = 3
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

### Technology
The Crawler uses [requests](https://pypi.org/project/requests/) library to send a `GET` query to get the needed information returned in JSON format.

## Future work
Figure out to extract Keywords from Title & Abstract

**I am welcome any effort to enhance this open-source project.**

**Thank you.**