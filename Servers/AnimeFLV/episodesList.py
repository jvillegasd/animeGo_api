import cfscrape
import json
from bs4 import BeautifulSoup

cfscraper = cfscrape.create_scraper(delay=10)

def scrapeEpisodeList(last_id, slug):
    response = cfscraper.get('https://animeflv.net/anime/{}/{}'.format(last_id, slug))
    html_file = response.text
    soup = BeautifulSoup(html_file, 'html.parser')
    json_response = []
    script_tags = soup('script')
    json_response = []
    for script in script_tags:
      json_response.append({script})
    print(json_response)
    return json_response