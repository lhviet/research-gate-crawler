import csv
import requests
import datetime
import re
import time

"""
Modify the below params to crawl the data we want
"""
# ex url = 'https://www.researchgate.net/search.SearchBox.loadMore.html?type=publication&query=hyperspectral%20drone%20uav&offset=10&limit=20&subfilter%5BpublicationType%5D=article'
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

"""
Custom Filters that this Crawler is using to limit the result that is not supported by the ResearchGate Filter
"""
from_year = 2000
abstract_required = True

"""
Build the Payload to pass to the query URL
"""
getPayload = lambda offset: {
  'query': terms,
  'type': search_type,
  'subfilter[publicationType]': publication_type,
  'offset': offset,
  'limit': limit,
}

pub_year_regex = '^[a-zA-Z]{3}\s20\d{2}$'

def crawl_data(offset, totalItems = 0):
  percentage = '0%' if totalItems == 0 else '{:.0%}'.format(offset/totalItems)
  print(f'Fetching {offset}/{totalItems} ({percentage})\n{base_url}')
  req = requests.get(base_url, getPayload(offset))
  res = req.json()
  return res['result']['searchSearch']['publication']

count_result = 0
author_separator = ','

# Set is_new_crawling to be False if we are crawling (continously) and written data into existing CSVs
is_new_crawling = True
nextOffset = 0
totalItems = 0

# Create the CSVs for years 2000 - 2020
if (is_new_crawling):
  for y in range(2000, 2021):
    with open(f'ResearchGate-{y}-{datetime.date.today()}.csv', 'w', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(['#', 'Title', 'Authors', 'Abstract', 'Announced', 'URL', 'DOI'])

# Continue crawling until finished (nextOffset is 0 from return data)
while True:
  publication = crawl_data(nextOffset, totalItems)
  nextOffset = publication['nextOffset']
  # totalItems for this search terms is 178787, on Jan 07th, 2020
  totalItems = publication['totalItems']
  # print(publication)

  items = publication['items']
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
    if re.search(pub_year_regex, announced) is None:
      continue
    year = int(announced.split(' ')[1])

    url = item['urls']['bareRootUrl']

    count_result += 1
    print(f'Retrieved paper = {count_result}')

    with open(f'ResearchGate-{year}-{datetime.date.today()}.csv', 'a', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow([count_result, title, author_str, abstract, announced, url])

  if nextOffset == 0:
    break

  # Take a break of 60 seconds before sending the next HTTP request
  time.sleep(60)

  # We may enable below code for Testing purpose
  # if (count_result > 10):
  #   break

