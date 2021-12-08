from flask import Flask
from flask_restful import Api
from twitter_bot_resources import TwitterBot

app=Flask(__name__)

api=Api(app)


@app.route("/")
def home():
    return "<h1 style='color:blue'>This is the Twiiter BOT  pipeline!</h1>"


api.add_resource(TwitterBot, '/twitter_bot')

if __name__=='__main__':
    app.run(port= 5000, debug=True)