from flask_restplus import Api, Resource, Namespace

main_api = Namespace('api', description='Index of main API')

@main_api.route('/')
class Home(Resource):
    def get(self):
        return {
            'status': 200,
            'servers': [
                'AnimeFLV'
            ]
        }