from flask import Flask
from flask_restplus import Api, Namespace
from Servers.AnimeFLV.main import animeflv_api
from Servers.api import main_api
from Servers.JKanime.main import jkanime_api

app = Flask(__name__)
api = Api(app=app)
api.add_namespace(main_api)
api.add_namespace(animeflv_api, path='/api/AnimeFLV')
api.add_namespace(jkanime_api, path='/api/JKanime')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)