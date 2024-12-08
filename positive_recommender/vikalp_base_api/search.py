from flask import Blueprint, request
from flask_cors import CORS, cross_origin
import requests
import json


search_bp = Blueprint('search', __name__)

#search
@search_bp.route("/api/v1/search", methods=['GET'])
@cross_origin()

def search():
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'q': request.args['q']
        }
        response = requests.get(f"https://{request.args['instance']}/api/v2/search", params=params, headers=headers)
        results = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': results['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            data = {
                'accounts': results['accounts'],
                'statuses': results['statuses'],
                'hashtags': results['hashtags']
            }
            return data
