from flask import jsonify
from flask_restful import Resource

# TestAPI Resource
class TestAPI(Resource):
    def get(self):
        response = {
            "error": False,
            "error_msg": "",
            "message": "API working"
        }
        return jsonify(response)
