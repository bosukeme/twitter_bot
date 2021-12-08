from flask_restful import Resource
from twitter_bot import start_twitter_bot



class TwitterBot(Resource):
    def post(self):
        try:

            result = start_twitter_bot()
            return {
                'status': 'success',
                'data': None, 
                'message': 'Twitter Bot successful.'
            }, 200

        except Exception as e:
            return {
                'status': 'failed',
                'data': None,
                'message': str(e)
            }, 500



