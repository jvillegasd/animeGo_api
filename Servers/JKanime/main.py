import cfscrape
from flask import request
from flask_restplus import Namespace, Resource, abort, fields
from Servers.JKanime.scraper import scrapeFeed, scrapeGenreList, scrapeSearch, scrapeList, scrapeGenre, scrapeEpisodeList, scrapeEpisode

cfscraper = cfscrape.create_scraper(delay=10)

jkanime_api = Namespace('JKanime', description='JKanime API')

search_model = jkanime_api.model('Search JKanime', {
    'value': fields.String
})
episodes_list_model = jkanime_api.model('Episodes List JKanime', {
    'slug': fields.String
})
watch_episode_model = jkanime_api.model('Watch Episode JKanime', {
    'slug': fields.String,
    'no_episode': fields.Integer
})
genre_model = jkanime_api.model('Genre search JKanime', {
    'type': fields.String
})

@jkanime_api.route('/')
class Home(Resource):
    @jkanime_api.doc(description='Index endpoint',
                      responses={200: 'Server is OK'})
    def get(self):
        return {'server': 'JKanime'}


@jkanime_api.route('/feed')
class Feed(Resource):
    @jkanime_api.doc(description='Get feed', responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      })
    def get(self):
        try:
            return scrapeFeed()
        except:
            abort(500, 'Something ocurred while retrieving feed')


@jkanime_api.route('/genre/list')
class GenreList(Resource):
    @jkanime_api.doc(description='Get genre list', 
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      })
    def get(self):
        try:
            return scrapeGenreList()
        except:
            abort(500, 'Something ocurred while retrieving genre list')


@jkanime_api.route('/search')
class Search(Resource):
    @jkanime_api.expect(search_model)
    @jkanime_api.doc(description='Search for an anime in JKanime',
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      },
                      params={'value': 'String to search in JKanime'})
    def post(self):
        params = request.get_json()
        anime_name = params['value']
        if not anime_name:
            abort(400, 'Bad request')
        try:
            return scrapeSearch(anime_name)
        except:
            abort(500, 'Something ocurred while searching the anime')


@jkanime_api.route('/list')
class List(Resource):
    @jkanime_api.doc(description='Get JKanime anime library',
                      responses={
                          200: 'Request was successful',
                          500: 'Internal server error'
                      })
    def get(self):
        try:
            return scrapeList()
        except:
            abort(500, 'Something ocurred while retrieving all anime list')


@jkanime_api.route('/genre')
class Genre(Resource):
    @jkanime_api.expect(genre_model)
    @jkanime_api.doc(description='Get animes related with specific genre', 
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      }, params={
                          'type': 'Genre type'
                      })
    def post(self):
        params = request.get_json()
        genre_type = params['type']
        if not genre_type:
            abort(400, 'Bad request')
        try:
            return scrapeGenre(genre_type)
        except:
            abort(500, 'Something ocurred while retrieving animes')


@jkanime_api.route('/episodes')
class Episodes(Resource):
    @jkanime_api.expect(episodes_list_model)
    @jkanime_api.doc(description='Search an anime episodes list',
                      responses={
                        200: 'Request was successful',
                        400: 'Bad request',
                        500: 'Internal server error'
                      },
                      params={
                        'slug': 'Anime name used in JKanime endpoint'
                      })
    def post(self):
        params = request.get_json()
        slug = params['slug']
        if not slug:
            abort(400, 'Bad request')
        try:
            return scrapeEpisodeList(slug)
        except:
            abort(500, 'Something ocurred while retrieving the episodes list')


@jkanime_api.route('/watch')
class Watch(Resource):
    @jkanime_api.expect(watch_episode_model)
    @jkanime_api.doc(description='Get episode streaming options', 
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      }, params={
                          'slug': 'Anime name used in JKanime endpoint',
                          'no_episode': 'Eposide number'
                      })
    def post(self):
        params = request.get_json()
        slug = params['slug']
        no_episode = params['no_episode']
        if not slug or not no_episode:
            abort(400, 'Bad request')
        try:
            return scrapeEpisode(slug, no_episode)
        except:
            abort(500, 'Something ocurred while retrieving streaming options')