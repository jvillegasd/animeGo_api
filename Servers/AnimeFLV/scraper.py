import cfscrape
import re
from bs4 import BeautifulSoup
from pyjsparser import parse

cfscraper = cfscrape.create_scraper(delay=10)

def scrapeEpisodeList(last_id, slug):
  response = cfscraper.get('https://animeflv.net/anime/{}/{}'.format(last_id, slug))
  html_file = response.content
  soup = BeautifulSoup(html_file, 'html.parser')
  episodes = getEpisodes(soup)
  return {
    'slug': slug,
    'episodes': episodes
  }


def scrapeEpisode(id_episode, slug, no_episode):
  response = cfscraper.get('https://animeflv.net/ver/{}/{}-{}'.format(id_episode, slug, no_episode))
  html_file = response.content
  soup = BeautifulSoup(html_file, 'html.parser')
  return getStreamOptions(soup)


def getStreamOptions(soup):
  options_pattern = re.compile(r'var videos = .')
  options_script_tag = soup.find('script', text=options_pattern).text
  parsed_script = parse(options_script_tag)
  options_js = parsed_script['body'][5]['declarations'][0]['init']['properties'][0]['value']['elements']
  options = []
  for option in options_js:
    option_info = {
      'server_name': option['properties'][1]['value']['value'],
      'link': option['properties'][3]['value']['value']
    }
    if option_info['server_name'] == 'MEGA':
      option_info['link'] = option['properties'][2]['value']['value']
    options.append(option_info)
  return options

def getEpisodes(soup):
  episodes_pattern = re.compile(r"var episodes = .")
  episodes_script_tag = soup.find('script', text=episodes_pattern).text
  parsed_script = parse(episodes_script_tag)
  episodes_js = parsed_script['body'][1]['declarations'][0]['init']['elements']
  episodes = []
  for episode in episodes_js:
    episode_info = {
      'no_episode': episode['elements'][0]['value'],
      'id_episode': episode['elements'][1]['value']
    }
    episodes.append(episode_info)
  episodes.reverse()
  return episodes