import cfscrape
import re
from bs4 import BeautifulSoup
from pyjsparser import parse

cfscraper = cfscrape.create_scraper(delay=10)

def scrapeEpisodeList(last_id, slug):
    response = cfscraper.get('https://animeflv.net/anime/{}/{}'.format(last_id, slug))
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
    response = cfscraper.get('https://animeflv.net/ver/{}/{}-{}'.format(id_episode, slug, no_episode))
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    return getStreamOptions(soup)


def scrapeGenre(genre):
    pagination = getPagination(genre)
    animes = []
    for i in range(1, pagination + 1):
        animes.append(getResults(genre, i))
    return animes


def scrapeGenreList():
    response = cfscraper.get('https://animeflv.net/browse')
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    genre_select_tag = soup.find('select', id='genre_select')
    genre_option_array = genre_select_tag.findAll('option')
    genre_list = [option_tag['value'] for option_tag in genre_option_array]
    return genre_list


def scrapeFeed():
    response = cfscraper.get('https://animeflv.net')
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    wrapper_div_tag = soup.find('div', class_='Wrapper')
    ep_ul_tag = wrapper_div_tag.find('ul', class_='ListEpisodios')
    li_array = ep_ul_tag.findAll('li')
    feed = []
    for li_tag in li_array:
        title, id_episode, slug, no_episode = getEpisodeInfo(li_tag)
        episode = {
            'title': title,
            'slug': slug,
            'id_episode': id_episode,
            'no_episode': no_episode
        }
        feed.append(episode)
    return feed


def getEpisodeInfo(li_tag):
    a_tag = li_tag.find('a')
    href = a_tag['href']
    title = a_tag.find('strong').text
    splitted_href = href.split('/')
    id_episode = int(splitted_href[2])
    slug_ep_href = splitted_href[3].split('-')
    array_size = len(slug_ep_href)
    ep_len = len(slug_ep_href[array_size - 1])
    no_episode = int(slug_ep_href[array_size - 1])
    slug = splitted_href[3][:-(ep_len + 1)]
    return [title, id_episode, slug, no_episode]


def getPagination(genre):
    response = cfscraper.get('https://animeflv.net/browse?genre[]={}&order=default&page=1'.format(genre))
    if response.status_code != 200:
        return []
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    pagination_ul_tag = soup.find('ul', class_='pagination')
    li_array = pagination_ul_tag.findAll('li')
    pagination_size = int(li_array[len(li_array) - 2].text)
    return pagination_size


def getResults(genre, page):
    response = cfscraper.get('https://animeflv.net/browse?genre[]={}&order=default&page={}'.format(genre, page))
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