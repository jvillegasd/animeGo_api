import cfscrape
from flask import request
from flask_restplus import Namespace, Resource, abort, fields
from Servers.JKanime.scraper import scrapeFeed, scrapeGenreList, scrapeSearch

cfscraper = cfscrape.create_scraper(delay=10)

jkanime_api = Namespace('JKanime', description='JKanime API')

search_model = jkanime_api.model('Search', {
    'value': fields.String
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