import cfscrape
from bs4 import BeautifulSoup

cfscraper = cfscrape.create_scraper(delay=10)


def scrapeFeed():
    response = cfscraper.get('https://jkanime.net')
    html_file = response.content
    soup = BeautifulSoup(html_file, 'html.parser')
    div_tag = soup.find('div', class_='overview')
    feed_a_tag = div_tag.findAll('a')
    feed = []
    for a in feed_a_tag:
        title, slug, no_episode = getEpisodeInfo(a)
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
    li_tag = ul_tag.findAll('li')
    genre_list = []
    for li in li_tag:
        a_tag = li.find('a')
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
        div_tag = soup.findAll('div', class_='portada-box')
        if not div_tag:
            break
        page_results = []
        for div in div_tag:
            a_tag = div.find('a')
            title, slug, no_episode = getEpisodeInfo(a_tag)
            anime = {
                'title': title,
                'slug': slug
            }
            page_results.append(anime)
        results.append(page_results)
        page+=1
    return results


def getEpisodeInfo(a):
    title = a['title']
    href = a['href']
    splitted_href = href.split('/')
    slug = splitted_href[3]
    no_episode = splitted_href[4]
    return title, slug, no_episode