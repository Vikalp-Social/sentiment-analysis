from flask import Blueprint, request
from flask_cors import CORS, cross_origin
import requests
import json

profile_bp = Blueprint('profile', __name__)

#fetch user account data
@profile_bp.route("/api/v1/accounts/<id>", methods=['GET'])
@cross_origin()

def get_profile(id):
    try:
        res1 = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}")
        account = json.loads(res1.text)
        res2 = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}/statuses")
        statuses = json.loads(res2.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if res1.status_code >= 400:
            return ({
            'error': account['error'],
            'status': res1.status_code,
            'statusText': res1.reason,
        }, res1.status_code)
        elif res2.status_code >= 400:
            return ({
            'error': statuses['error'],
            'status': res2.status_code,
            'statusText': res2.reason,
        }, res2.status_code)
        else:
            data = {
                'account': account,
                'statuses': {
                    'count': len(statuses),
                    'list': statuses
                }
            }
            return data

#edit user profile
@profile_bp.route("/api/v1/accounts", methods=['PATCH'])
@cross_origin()

def edit_profile():
    try:
        body = {
            'display_name': request.json['display_name'],
            'note': request.json['note'],
        }
        headers = {
            'Authorization': f"Bearer {request.json['token']}"
        }
        response = requests.patch(f"https://{request.json['instance']}/api/v1/accounts/update_credentials", headers=headers, json=body)
        edit_profile = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': edit_profile['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return edit_profile
    
#fetch user followers
@profile_bp.route("/api/v1/accounts/<id>/followers", methods=['GET'])
@cross_origin()

def get_followers(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}/followers", headers=headers)
        followers = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': followers['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            data = {
                'accounts': followers,
                'max_id': followers[-1]['id'],
            }
            return data
        
#fetch user following
@profile_bp.route("/api/v1/accounts/<id>/following", methods=['GET'])
@cross_origin()

def get_following(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}/following", headers=headers)
        following = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': following['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            data = {
                'accounts': following,
                'max_id': following[-1]['id'],
            }
            return data
