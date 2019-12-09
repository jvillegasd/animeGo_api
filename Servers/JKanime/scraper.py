import cfscrape
from bs4 import BeautifulSoup

cfscraper = cfscrape.create_scraper(delay=10)


def scrapeFeed():
    response = cfscraper.get('https://jkanime.net')
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
    response = cfscraper.get('https://jkanime.net')
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
    page = 1
    results = []
    while True:
        response = cfscraper.get('https://jkanime.net/buscar/{}/{}/'.format(value, page))
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
            page_results.append(anime)
        results.append(page_results)
        page+=1
    return results


def getEpisodeInfo(a_tag):
    title = a_tag['title']
    href = a_tag['href']
    splitted_href = href.split('/')
    slug = splitted_href[3]
    no_episode = splitted_href[4]
    return title, slug, no_episode