from flask import Flask
from flask_restful import Api
from resources.test import TestAPI 

app = Flask(__name__)

api = Api(app, prefix="/api")

api.add_resource(TestAPI, '/')

if __name__ == '__main__':
    app.run(debug=True)
