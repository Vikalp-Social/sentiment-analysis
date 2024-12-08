from flask import Blueprint, Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import requests
import json

timeline_bp = Blueprint('timeline', __name__)

@timeline_bp.route('/')
def home():
    return "Welcome to the Main App"

#fetch tag timeline
# GET
@timeline_bp.route("/api/v1/timelines/tag/<name>", methods=['GET'])
@cross_origin()

def get_tag_timeline(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'max_id': request.args['max_id']
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/tag/{name}?limit=50", params=params, headers=headers)
        tag_timeline = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': tag_timeline['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            data = {
                'data': tag_timeline,
                'max_id': tag_timeline[-1]['id']
            }
            return data

#fetch home timeline
# GET
@timeline_bp.route("/api/v1/timelines/home", methods=['GET'])
@cross_origin()

def get_timeline():
    #print(request.args)
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'max_id': request.args['max_id'] #posts[len(posts) - 1].id
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/home?limit=20", headers=headers, params=params)
        timeline = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': timeline['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            data = {
                'data': timeline,
                'max_id': timeline[-1]['id']
            }
            return data