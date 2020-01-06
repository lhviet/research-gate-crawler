import csv
import requests
import datetime
import re

"""
Modify the below params to crawl the data we want
"""
# ex url = 'https://www.researchgate.net/search.SearchBox.loadMore.html?type=publication&query=hyperspectral%20drone%20uav&offset=10&limit=20&subfilter%5BpublicationType%5D=article'
base_url = 'https://www.researchgate.net/search.SearchBox.loadMore.html'

# Keywords used to search papers
# Looks like the query operator is OR,
# eg., searching 'drone' returns totalItems=7467, wheras, searching 'drone uav' returns totalItems=28388
terms = 'drone uav remote-sensing "remote sensing"'

# Searching Publications, not Authors or Reviews...
search_type = 'publication'
# Type of publication we need to search is Article, not Conference Paper, Posters, or Others...
publication_type = 'article'

limit = 10

"""
Custom Filters that this Crawler is using to limit the result that is not supported by the ResearchGate Filter
"""
from_year = 2000
abstract_required = True

"""
Build the Payload to pass to ther query URL
"""
getPayload = lambda offset: {
  'query': terms,
  'type': search_type,
  'subfilter[publicationType]': publication_type,
  'offset': offset,
  'limit': limit,
}

pub_year_regex = '^[a-zA-Z]{3}\s20\d{2}$'

def crawl_data(offset):
  req = requests.get(base_url, getPayload(offset))
  res = req.json()
  return res['result']['searchSearch']['publication']

count_result = 0
author_separator = ','

with open(f'ResearchGate-{datetime.date.today()}.csv', 'w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['#', 'Title', 'Authors', 'Abstract', 'Announced', 'URL', 'DOI'])

  # The first attempt to crawl data
  publication = crawl_data(0)
  nextOffset = publication['nextOffset']

  # Continue crawling until finished (nextOffset is 0 from return data)
  while (nextOffset > 0):
    items = publication['items']
    print(items)
    for item in items:
      title = item['title']
      
      authors = [a['name'] for a in item['authors']]
      author_str = author_separator.join(authors)

      abstract = ''
      if abstract_required:
        if 'abstract' not in item:
          continue
        abstract = item['abstract']

      # Extract the publication date
      if 'metaItems' not in item or len(item['metaItems']) < 1:
        continue
      announced = item['metaItems'][0]['label']
      # Testing if the announced date match with the format, e.g., 'Mar 2007' matched, 'Apr 1999' unmatched
      if re.search('^[a-zA-Z]{3}\s20\d{2}$', announced) is None:
        continue

      url = item['urls']['bareRootUrl']

      count_result += 1
      # print(f'{count_result} = {abstract}')
      writer.writerow([count_result, title, author_str, abstract, announced, url])

    if (count_result > 5):
      break
    publication = crawl_data(nextOffset)


# print(publication['totalItems'])
# print(publication['nextOffset'])
# print(publication['items'])
