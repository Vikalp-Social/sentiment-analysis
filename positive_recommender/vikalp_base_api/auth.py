from flask import Blueprint, current_app, request, jsonify, Response
from flask_cors import CORS, cross_origin
import requests
import json

auth_bp = Blueprint('auth', __name__)

#register app
@auth_bp.route("/api/v1/register", methods=['POST'])
@cross_origin()

def register_app():
    try:
        body = {
            'client_name': "Vikalp",
            'redirect_uris': f"{current_app.config['DOMAIN']}/auth/",
            'scopes': "read write push",
            'website': f"{current_app.config['DOMAIN']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/apps", json=body)
        register_app = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': register_app['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return register_app

#authenticate user
@auth_bp.route("/api/v1/auth", methods=['POST'])
@cross_origin()

def get_auth_token():
    #print(request.json)
    try:
        body = {
            'client_id': request.json['id'],
            'client_secret': request.json['secret'],
            'redirect_uri': f"{current_app.config['DOMAIN']}/auth/",
            'grant_type': "authorization_code",
            'code': request.json['code'],
            'scope': "read write push",
        }
        res1 = requests.post(f"https://{request.json['instance']}/oauth/token", json=body)
        auth = json.loads(res1.text)
        headers = {
            "Authorization": f"Bearer {auth['access_token']}"
        }
        res2 = requests.get(f"https://{request.json['instance']}/api/v1/accounts/verify_credentials", headers=headers)
        verify = json.loads(res2.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if res1.status_code >= 400:
            return ({
            'error': auth['error'],
            'status': res1.status_code,
            'statusText': res1.reason,
        }, res1.status_code)
        elif res2.status_code >= 400:
            return ({
            'error': verify['error'],
            'status': res2.status_code,
            'statusText': res2.reason,
        }, res2.status_code)
        else:
            return jsonify({
                'account': verify,
                'token': auth['access_token']
            })