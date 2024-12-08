from flask import Blueprint, request
from flask_cors import CORS, cross_origin
import json
import requests


status_bp = Blueprint('status', __name__)


#post a status
# POST
@status_bp.route("/api/v1/statuses", methods=['POST'])
@cross_origin()

def post_status():
    try:
        body = {
            'status': request.json['message'],
            'media_ids': request.json['media_ids'],
            'in_reply_to_id': request.json['reply_id'],
        }
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses", headers=headers, json=body)
        post_status = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': post_status['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return post_status

#edit a status
# PUT
@status_bp.route("/api/v1/statuses/<id>", methods=['PUT'])
@cross_origin()

def edit_status(id):
    try:
        body = {
            'status': request.json['text']
        }
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.put(f"https://{request.json['instance']}/api/v1/statuses/{id}", json=body, headers=headers)
        edit_status = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': edit_status['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return edit_status

#favorite or unfavourite a status
# POST
@status_bp.route("/api/v1/statuses/<id>/favourite", methods=['POST'])
@cross_origin()

def favourite(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}favourite", headers=headers)
        favourite = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': favourite['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return favourite

#boost or unboost a status
# POST
@status_bp.route("/api/v1/statuses/<id>/boost", methods=['POST'])
@cross_origin()

def boost(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}reblog", headers=headers)
        boost = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': boost['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return boost

#fetch a status
# GET
@status_bp.route("/api/v1/statuses/<id>", methods=['GET'])
@cross_origin()

def get_status(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        res1 = requests.get(f"https://{request.args['instance']}/api/v1/statuses/{id}", headers=headers)
        status = json.loads(res1.text)
        res2 = requests.get(f"https://{request.args['instance']}/api/v1/statuses/{id}/context", headers=headers)
        replies = json.loads(res2.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if res1.status_code >= 400:
            return ({
            'error': status['error'],
            'status': res1.status_code,
            'statusText': res1.reason,
        }, res1.status_code)
        else:
            data = {
                'status': status,
                'replies': replies['descendants']
            }
            return data
