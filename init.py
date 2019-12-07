from flask import Flask
from flask_restplus import Api, Resource, Namespace
from Servers.AnimeFLV.main import animeflv_api
from Servers.api import main_api

app = Flask(__name__)
api = Api(app=app)
api.add_namespace(main_api)
api.add_namespace(animeflv_api, path='/api/AnimeFLV')

if __name__ == '__main__':
    app.run(debug=True)