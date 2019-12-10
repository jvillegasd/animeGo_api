import cfscrape
import re
from bs4 import BeautifulSoup
from string import ascii_uppercase
from pyjsparser import parse

cfscraper = cfscrape.create_scraper(delay=10)
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

def scrapeFeed():
    response = cfscraper.get('https://jkanime.net', headers=headers)
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    div_tag = soup.find('div', class_='overview')
    feed_a_array = div_tag.findAll('a')
    feed = []
    for a_tag in feed_a_array:
        title, slug, no_episode = getEpisodeInfo(a_tag)
        episode = {
            'title': title,
            'slug': slug,
            'no_episode': no_episode
        }
        feed.append(episode)
    return feed


def scrapeGenreList():
    response = cfscraper.get('https://jkanime.net', headers=headers)
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


def scrapeSearch(value):
    return getSearchResults(value, 'buscar')


def scrapeList():
    results = []
    for letter in ascii_uppercase:
        results.extend(getSearchResults(letter, 'letra'))
    results.extend(getSearchResults('0-9', 'letra'))
    return results


def scrapeGenre(value):
    return getSearchResults(value, 'genero')


def scrapeEpisodeList(slug):
    response = cfscraper.get('https://jkanime.net/{}/'.format(slug), headers=headers)
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    title, synopsis = getAnimeInfo(soup)
    pagination = getPagination(soup)
    endpoint = getEpisodeEndpoint(soup)
    episodes = getEpisodes(endpoint, pagination)
    return {
        'title': title,
        'synopsis': synopsis,
        'slug': slug,
        'episodes': episodes
    }
    

def scrapeEpisode(slug, no_episode):
    response = cfscraper.get('https://jkanime.net/{}/{}/'.format(slug, no_episode), headers=headers)
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


def getPagination(soup):
    nav_div_tag = soup.find('div', class_='navigation')
    a_array = nav_div_tag.findAll('a')
    return len(a_array)


def getEpisodeEndpoint(soup):
    var_pattern = re.compile(r'var invertir = .')
    container_div_tag = soup.find('div', id='container')
    script_tag = container_div_tag.find('script', text=var_pattern).text
    parsed_script = parse(script_tag)
    endpoint = parsed_script['body'][1]['expression']['arguments'][0]['body']['body'][0]['expression']['arguments'][0]['left']['left']['value']
    endpoint = 'https://jkanime.net' + endpoint + '{}/'
    return endpoint


def getEpisodes(endpoint, pagination):
    episodes = []
    for i in range(1, pagination + 1):
        response = cfscraper.get(endpoint.format(i), headers=headers)
        if response.status_code != 200:
            continue
        json_response = response.json()
        pag_episodes = json_response
        episodes_info = [{'no_episode': episode['number']} for episode in pag_episodes]
        episodes.extend(episodes_info)
    return episodes


def getEpisodeInfo(a_tag):
    title = a_tag['title']
    href = a_tag['href']
    splitted_href = href.split('/')
    slug = splitted_href[3]
    no_episode = splitted_href[4]
    return title, slug, no_episode


def getAnimeInfo(soup):
    div_tag = soup.find('div', class_='sinopsis-box')
    title = div_tag.find('h2').text
    synopsis = div_tag.find('p', class_='pc').text
    synopsis.replace('Sinopsis: ', '')
    return title, synopsis


def getSearchResults(value, option):
    page = 1
    results = []
    while True:
        response = cfscraper.get('https://jkanime.net/{}/{}/{}/'.format(option, value, page), headers=headers)
        if response.status_code != 200:
            return []
        html_file = response.text
        soup = BeautifulSoup(html_file, 'html.parser')
        div_array = soup.findAll('div', class_='portada-box')
        if not div_array:
            break
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
        results.extend(page_results)
        page+=1
    return results


def videoExists(element):
    return 'expression' in element and 'right' in element['expression'] and 'value' in element['expression']['right']