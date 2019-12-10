from flask_restplus import Resource, Namespace

main_api = Namespace('api', description='Index of main API')

@main_api.route('/')
class Home(Resource):
    def get(self):
        return {
            'servers': {
                'Español': [
                    'AnimeFLV',
                    'JKanime'
                ],
                'English': [
                    '9anime'
                ]
            }
        }