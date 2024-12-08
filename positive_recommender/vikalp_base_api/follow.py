from flask import Blueprint, Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import requests
import json


follow_bp = Blueprint('follow', __name__)

#follow a user
@follow_bp.route("/api/v1/accounts/<id>/follow", methods=['POST'])
@cross_origin()

def follow_user(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/follow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow

#follow a tag
# POST
@follow_bp.route("/api/v1/tags/<name>/follow", methods=['POST'])
@cross_origin()

def follow_tag(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/follow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow
        
#get following tags
# GET
@follow_bp.route("/api/v1/tags/following", methods=['GET'])
@cross_origin()

def get_following_tags():
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/followed_tags", headers=headers)
        tags = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': tags['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return tags

#unfollow a user
# POST
@follow_bp.route("/api/v1/accounts/<id>/unfollow", methods=['POST'])
@cross_origin()

def unfollow_user(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/unfollow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow

#unfollow a tag
# POST
@follow_bp.route("/api/v1/tags/<name>/unfollow", methods=['POST'])
@cross_origin()

def unfollow_tag(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/unfollow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow
