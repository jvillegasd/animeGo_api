import cfscrape
import re
import json
from random import choice
from bs4 import BeautifulSoup
from pyjsparser import parse

cfscraper = cfscrape.create_scraper(delay=12)
user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36']


def randomUserAgent():
    return {
      'user-agent': choice(user_agents)
    }

def scrapeLastAnimeAdded():
    response = cfscraper.get('https://animeflv.net/', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    ul_tag = soup.find('ul', class_='ListAnimes')
    li_array = ul_tag.findAll('li')
    last_anime_list = []
    for li_tag in li_array:
        title, slug, last_id, description, image = getLastAnimeInfo(li_tag)
        anime = {
          'title': title,
          'slug': slug,
          'last_id': last_id,
          'description': description,
          'image': image
        }
        last_anime_list.append(anime)
    return last_anime_list


def scrapeEpisodeList(last_id, slug):
    response = cfscraper.get('https://animeflv.net/anime/{}/{}'.format(last_id, slug), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    episodes = getEpisodes(soup)
    title, sysnopsis = getAnimeInfo(soup)
    return {
        'title': title,
        'synopsis': sysnopsis,
        'slug': slug,
        'episodes': episodes
    }


def scrapeEpisode(id_episode, slug, no_episode):
    response = cfscraper.get('https://animeflv.net/ver/{}/{}-{}'.format(id_episode, slug, no_episode), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    return getStreamOptions(soup)


def scrapeGenre(genre, page):
    animes = getResults(genre, page)
    return animes


def scrapeGenreList():
    response = cfscraper.get('https://animeflv.net/browse', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    genre_select_tag = soup.find('select', id='genre_select')
    genre_option_array = genre_select_tag.findAll('option')
    genre_list = [option_tag['value'] for option_tag in genre_option_array]
    return genre_list


def scrapeFeed():
    response = cfscraper.get('https://animeflv.net', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    wrapper_div_tag = soup.find('div', class_='Wrapper')
    ep_ul_tag = wrapper_div_tag.find('ul', class_='ListEpisodios')
    li_array = ep_ul_tag.findAll('li')
    feed = []
    for li_tag in li_array:
        title, id_episode, slug, no_episode, image = getEpisodeInfo(li_tag)
        episode = {
            'title': title,
            'slug': slug,
            'id_episode': id_episode,
            'no_episode': no_episode,
            'image': image
        }
        feed.append(episode)
    return feed


def getEpisodeInfo(li_tag):
    a_tag = li_tag.find('a')
    span_image = a_tag.find('span', class_='Image')
    image = 'https://animeflv.net' + (span_image.find('img'))['src']
    href = a_tag['href']
    title = a_tag.find('strong').text
    splitted_href = href.split('/')
    id_episode = int(splitted_href[2])
    slug_ep_href = splitted_href[3].split('-')
    array_size = len(slug_ep_href)
    ep_len = len(slug_ep_href[array_size - 1])
    no_episode = int(slug_ep_href[array_size - 1])
    slug = splitted_href[3][:-(ep_len + 1)]
    return [title, id_episode, slug, no_episode, image]


def getResults(genre, page):
    response = cfscraper.get('https://animeflv.net/browse?genre[]={}&order=default&page={}'.format(genre, page), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    animes_div_array = soup.findAll('div', class_='Description')
    results = []
    for div_tag in animes_div_array:
        anime_title = div_tag.find('strong').text
        anime_href = div_tag.find('a', class_='Button Vrnmlk')['href']
        splitted_href = anime_href.split('/')
        last_id = splitted_href[2]
        slug = splitted_href[3]
        anime = {
            'title': anime_title,
            'slug': slug,
            'last_id': last_id
        }
        results.append(anime)
    return results


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


def getAnimeInfo(soup):
    main_tag = soup.find('main', class_='Main')
    sysnopsis_section_tag = main_tag.find('section', class_='WdgtCn')
    div_tag = sysnopsis_section_tag.find('div', class_='Description')
    p_tag = div_tag.find('p')
    sysnopsis = p_tag.text
    h2_tag = soup.find('h2', class_='Title')
    title = h2_tag.text
    return [title, sysnopsis]


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


def getLastAnimeInfo(li_tag):
    figure_tag = li_tag.find('figure')
    image = 'https://animeflv.net' + (figure_tag.find('img'))['src']
    a_tag = li_tag.find('a')
    a_href = a_tag['href']
    splitted_href = a_href.split('/')
    last_id = int(splitted_href[2])
    slug = splitted_href[3]
    div_description = li_tag.find('div', class_='Description')
    div_title = div_description.find('div', class_='Title')
    title = (div_title.find('strong')).text
    description = ""
    p_array = div_description.findAll('p')
    for p_tag in p_array:
        if not p_tag.find('span'):
            description = p_tag.text
            break
    return [title, slug, last_id, description, image]

def getList():
  response = cfscraper.get('https://animeflv.net/api/animes/list', headers=randomUserAgent())
  json_file = json.loads(response.text)
  json_response = []
  for anime in json_file:
      json_response.append({
          'id': anime[0],
          'title': anime[1],
          'type': anime[4],
          'last_id': anime[3],
          'slug': anime[2]
      })
  return json_response