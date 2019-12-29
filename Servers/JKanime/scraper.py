import cfscrape
import re
from random import choice
from bs4 import BeautifulSoup
from string import ascii_uppercase
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

def scrapeFeed():
    response = cfscraper.get('https://jkanime.net', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    div_tag = soup.find('div', class_='overview')
    feed_a_array = div_tag.findAll('a')
    feed = []
    for a_tag in feed_a_array:
        title, slug, no_episode, image = getEpisodeInfo(a_tag)
        episode = {
            'title': title,
            'slug': slug,
            'no_episode': no_episode,
            'image': image
        }
        feed.append(episode)
    return feed


def scrapeGenreList():
    response = cfscraper.get('https://jkanime.net', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    div_tag = soup.find('div', class_='genre-list')
    ul_tag = div_tag.find('ul')
    li_array = ul_tag.findAll('li')
    genre_list = []
    for li_tag in li_array:
        a_tag = li_tag.find('a')
        href = a_tag['href']
        splitted_href = href.split('/')
        genre_list.append(splitted_href[2])
    return genre_list


def scrapeSearch(value, page):
    return getSearchResults(value, 'buscar', page)


def scrapeGenre(value, page):
    return getSearchResults(value, 'genero', page)


def scrapeEpisodeList(slug, page):
    response = cfscraper.get('https://jkanime.net/{}/'.format(slug), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    title, synopsis = getAnimeInfo(soup)
    endpoint = getEpisodeEndpoint(soup)
    episodes = getEpisodes(endpoint, page)
    return {
        'title': title,
        'synopsis': synopsis,
        'slug': slug,
        'episodes': episodes
    }
    

def scrapeEpisode(slug, no_episode):
    response = cfscraper.get('https://jkanime.net/{}/{}/'.format(slug, no_episode), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    var_pattern = re.compile(r'var video = .')
    script_tag = soup.find('script', text=var_pattern).text
    parsed_script = parse(script_tag)
    parsed_array = parsed_script['body']
    iframe_array = []
    streaming_options = []
    for element in parsed_array:
        if videoExists(element):
            iframe_array.append(element['expression']['right']['value'])
    links = getStreamingOptions(iframe_array)
    server_names = getServerNames(soup)
    for i in range(0, len(links)):
        server_info = {
            'server_name': server_names[i],
            'link': links[i]
        }
        streaming_options.append(server_info)
    return streaming_options


def scrapeLastAnimeAdded():
    response = cfscraper.get('https://jkanime.net', headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    div_content_box = soup.find('div', class_='content-box')
    div_array = div_content_box.findAll('div', class_='portada-box')
    last_anime_added = []
    for div_tag in div_array:
        a_tag = div_tag.find('a', {'rel': 'nofollow'})
        title, slug, image, description = getLastAnimeInfo(a_tag)
        anime = {
          'title': title,
          'slug': slug,
          'description': description,
          'image': image
        }


def getLastAnimeInfo(a_tag):
    title = a_tag['title']
    splitted_href = a_tag['href'].split('/')
    slug = splitted_href[3]
    image = (a_tag.find('img'))['src']
    description = 'Sipnosis disponible en su pagina respectiva.'
    return [title, slug, image, description]


def getStreamingOptions(iframe_array):
    streaming_options = []
    for html_element in iframe_array:
        soup = BeautifulSoup(html_element, 'html.parser')
        iframe_tag = soup.find('iframe')
        streaming_options.append(iframe_tag['src'])
    return streaming_options


def getServerNames(soup):
    server_names = []
    ul_tag = soup.find('ul', class_='server-tab')
    li_array = ul_tag.findAll('li', role='presentation')
    for li_tag in li_array:
        a_tag = li_tag.find('a')
        server_names.append(a_tag.text)
    return server_names


def getEpisodeEndpoint(soup):
    var_pattern = re.compile(r'var invertir = .')
    container_div_tag = soup.find('div', id='container')
    script_tag = container_div_tag.find('script', text=var_pattern).text
    parsed_script = parse(script_tag)
    endpoint = parsed_script['body'][1]['expression']['arguments'][0]['body']['body'][0]['expression']['arguments'][0]['left']['left']['value']
    endpoint = 'https://jkanime.net' + endpoint + '{}/'
    return endpoint


def getEpisodes(endpoint, page):
    response = cfscraper.get(endpoint.format(page), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    json_response = response.json()
    pag_episodes = json_response
    episodes_info = [{'no_episode': episode['number']} for episode in pag_episodes]
    return episodes_info


def getEpisodeInfo(a_tag):
    title = a_tag['title']
    href = a_tag['href']
    splitted_href = href.split('/')
    slug = splitted_href[3]
    no_episode = splitted_href[4]
    image = (a_tag.find('img'))['src']
    return title, slug, no_episode, image


def getAnimeInfo(soup):
    div_tag = soup.find('div', class_='sinopsis-box')
    title = div_tag.find('h2').text
    synopsis = div_tag.find('p', class_='pc').text
    synopsis.replace('Sinopsis: ', '')
    return title, synopsis


def getSearchResults(value, option, page):
    response = cfscraper.get('https://jkanime.net/{}/{}/{}/'.format(option, value, page), headers=randomUserAgent())
    if response.status_code != 200:
        return []
    html_file = response.text
    soup = BeautifulSoup(html_file, 'html.parser')
    div_array = soup.findAll('div', class_='portada-box')
    if not div_array:
        return []
    page_results = []
    for div_tag in div_array:
        a_tag = div_tag.find('a')
        title, slug, no_episode = getEpisodeInfo(a_tag)
        anime = {
            'title': title,
            'slug': slug
        }
        if not slug:
            continue
        page_results.append(anime)
    return page_results


def videoExists(element):
    return 'expression' in element and 'right' in element['expression'] and 'value' in element['expression']['right']