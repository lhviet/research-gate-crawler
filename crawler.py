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

# From experiments, the max items we can crawl for each request is 300
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
headers = {
  'Accept': 'application/json'
}

# From experiments, we need below cookies to make sure that the crawler will obtain JSON data successfully.
# Without the cookies, after a few requests, the Server will return an ERROR HTML of time-rate limitation.
cookies = {
  'pl': 'deleted; path=/; domain=.www.researchgate.net; Secure; HttpOnly;'
}

pub_year_regex = '^[a-zA-Z]{3}\s20\d{2}$'

def crawl_data(offset, totalItems = 0):
  """
  Sending a GET request to collect the data. Retry 3 times if failed.
  :param offset:
  :param totalItems:
  :return: a JSON object (Dictionary)
  """
  retry = 0
  try:
    percentage = '0%' if totalItems == 0 else '{:.0%}'.format(offset / totalItems)

    req = requests.get(base_url, params=getPayload(offset), headers=headers, cookies=cookies)
    print(f'\nFetching {offset}/{totalItems} ({percentage})')
    # print(req.headers)
    print(req.url)

    res = req.json()
    retry = 0
    return res['result']['searchSearch']['publication']
  except:
    retry += 1
    print(f'An exception occurred, sleep 20 seconds and try again...{retry}')
    time.sleep(20)
    crawl_data(offset, totalItems)

    # Stop the program after re-tried 3 times
    if retry == 4:
      exit()


# Set is_new_crawling to be False if we are crawling (continuously) and written data into existing CSVs
def crawling(offset=0, is_new_crawling=True):
  count_result = 0
  nextOffset = offset
  totalItems = 0

  # Create the CSVs for years 2000 - 2020
  if (is_new_crawling):
    for y in range(2000, 2021):
      with open(f'ResearchGate-{y}-{datetime.date.today()}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['#', 'Title', 'Authors', 'Abstract', 'Announced', 'URL', 'DOI'])

  # Continue crawling until finished (nextOffset is 0 from return data)
  retrieved_total = []
  ignored_total = []
  while True:
    retrieved = []
    ignored = []

    publication = crawl_data(nextOffset, totalItems)
    # totalItems for this search terms is 178787, on Jan 07th, 2020
    totalItems = publication['totalItems']
    # print(publication)

    items = publication['items']
    for idx, item in enumerate(items):
      index = nextOffset + idx
      title = item['title']

      author_str = ''
      for a in item['authors']:
        # There is special cases, in which the paper has no-name author, in-existence
        if 'name' in a:
          author_str += f', {a["name"]}'

      abstract = ''
      if abstract_required:
        if 'abstract' not in item:
          ignored.append(index)
          continue
        abstract = item['abstract']

      # Extract the publication date
      if 'metaItems' not in item or len(item['metaItems']) < 1:
        ignored.append(index)
        continue
      announced = item['metaItems'][0]['label']
      # Testing if the announced date match with the format, e.g., 'Mar 2007' matched, 'Apr 1999' unmatched
      if re.search(pub_year_regex, announced) is None:
        ignored.append(index)
        continue
      year = int(announced.split(' ')[1])

      url = item['urls']['bareRootUrl']

      count_result += 1

      with open(f'ResearchGate-{year}-{datetime.date.today()}.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([count_result, title, author_str, abstract, announced, url])

      retrieved.append(index)

    retrieved_total.extend(retrieved)
    ignored_total.extend(ignored)

    print(f'retrieved ({len(retrieved)}) & ignored ({len(ignored)})')
    print(f'retrieved = {retrieved}')
    print(f'ignored = {ignored}')

    nextOffset = publication['nextOffset']
    if nextOffset == 0:
      break

    # Take a break of 60 seconds before sending the next HTTP request
    # time.sleep(20)

    # We may enable below code for Testing purpose
    # if (count_result > 10):
    #   break

  print('----------------------------')
  print(f'retrieved_total ({len(retrieved_total)}) & ignored_total ({len(ignored_total)})')
  print(f'retrieved_total = {retrieved_total}')
  print(f'ignored_total = {ignored_total}')

crawling()
