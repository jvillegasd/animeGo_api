import cfscrape
import json
from flask import request
from flask_restplus import Resource, Namespace, fields, abort
from Servers.AnimeFLV.scraper import scrapeEpisodeList, scrapeEpisode, scrapeGenre, scrapeGenreList, scrapeFeed

cfscraper = cfscrape.create_scraper(delay=10)

animeflv_api = Namespace('AnimeFLV', description='AnimeFLV API')

search_model = animeflv_api.model('Search', {
    'value': fields.String
})
episodes_list_model = animeflv_api.model('Episodes List', {
    'last_id': fields.Integer,
    'slug': fields.String
})
watch_episode_model = animeflv_api.model('Watch Episode', {
    'id_episode': fields.Integer,
    'slug': fields.String,
    'no_episode': fields.Integer
})
genre_model = animeflv_api.model('Genre search', {
    'type': fields.String
})


def getList():
  response = cfscraper.get('https://animeflv.net/api/animes/list')
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


@animeflv_api.route('/')
class Home(Resource):
    @animeflv_api.doc(description='Index endpoint',
                      responses={200: 'Server is OK'})
    def get(self):
        return {'server': 'AnimeFLV'}


@animeflv_api.route('/list')
class List(Resource):
    @animeflv_api.doc(description='Get AnimeFLV anime library',
                      responses={
                          200: 'Request was successful',
                          500: 'Internal server error'
                      })
    def get(self):
        try:
            anime_list = getList()
            return anime_list
        except:
            abort(500, 'Something ocurred while retrieving all anime list')


@animeflv_api.route('/search')
class Search(Resource):
    @animeflv_api.expect(search_model)
    @animeflv_api.doc(description='Search for an anime in AnimeFLV',
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      },
                      params={'value': 'String to search in AnimeFLV'})
    def post(self):
        params = request.get_json()
        anime_name = params['value']
        if not anime_name:
            abort(400, 'Bad request')
        try:
            anime_list = getList()
            filtered_anime = [anime for anime in anime_list if anime_name in anime['title']]
            return filtered_anime
        except:
            abort(500, 'Something ocurred while searching the anime')


@animeflv_api.route('/episodes')
class Episodes(Resource):
    @animeflv_api.expect(episodes_list_model)
    @animeflv_api.doc(description='Search an anime episodes list',
                      responses={
                        200: 'Request was successful',
                        400: 'Bad request',
                        500: 'Internal server error'
                      },
                      params={
                        'last_id': 'Anime last Id',
                        'slug': 'Anime name used in AnimeFLV endpoint'
                      })
    def post(self):
        params = request.get_json()
        last_id = params['last_id']
        slug = params['slug']
        if not slug or not last_id:
            abort(400, 'Bad request')
        try:
            return scrapeEpisodeList(last_id, slug)
        except:
            abort(500, 'Something ocurred while retrieving the episodes list')


@animeflv_api.route('/watch')
class Watch(Resource):
    @animeflv_api.expect(watch_episode_model)
    @animeflv_api.doc(description='Get episode streaming options', 
                      responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      }, params={
                          'id_episode': 'Episode id',
                          'slug': 'Anime name used in AnimeFLV endpoint',
                          'no_episode': 'Eposide number'
                      })
    def post(self):
        params = request.get_json()
        id_episode = params['id_episode']
        slug = params['slug']
        no_episode = params['no_episode']
        if not id_episode or not slug or not no_episode:
            abort(400, 'Bad request')
        try:
            return scrapeEpisode(id_episode, slug, no_episode)
        except:
            abort(500, 'Something ocurred while retrieving streaming options')


@animeflv_api.route('/genre')
class Genre(Resource):
    @animeflv_api.expect(genre_model)
    @animeflv_api.doc(description='Get animes related with specific genre', 
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


@animeflv_api.route('/genre/list')
class GenreList(Resource):
    @animeflv_api.doc(description='Get genre list', 
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


@animeflv_api.route('/feed')
class Feed(Resource):
    @animeflv_api.doc(description='Get today feed', responses={
                          200: 'Request was successful',
                          400: 'Bad request',
                          500: 'Internal server error'
                      })
    def get(self):
        try:
            return scrapeFeed()
        except:
            abort(500, 'Something ocurred while retrieving today feed')