from flask import Blueprint, current_app, request, jsonify, Response, make_response
from flask_cors import CORS, cross_origin
import requests
import json

auth_bp = Blueprint('auth', __name__)

#register app
@auth_bp.route("/api/v1/register", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def register_app():
    try:
        body = {
            'client_name': "Vikalp",
            'redirect_uris': f"{current_app.config['DOMAIN']}/auth/",
            'scopes': "read write push",
            'website': f"{current_app.config['DOMAIN']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/apps", json=body)
        register_app = response.json()
        
        if response.status_code >= 400:
            return jsonify({
                'error': register_app.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code
            
        return jsonify(register_app)
        
    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#authenticate user
@auth_bp.route("/api/v1/auth", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_auth_token():
    try:
        # Create response object
        response = make_response()
        
        body = {
            'client_id': request.json['id'],
            'client_secret': request.json['secret'],
            'redirect_uri': f"{current_app.config['DOMAIN']}/auth/",
            'grant_type': "authorization_code",
            'code': request.json['code'],
            'scope': "read write push",
        }
        
        # Get access token
        token_response = requests.post(f"https://{request.json['instance']}/oauth/token", json=body)
        auth_data = token_response.json()
        
        if token_response.status_code >= 400:
            return jsonify({
                'error': auth_data.get('error'),
                'status': token_response.status_code,
                'statusText': token_response.reason
            }), token_response.status_code
            
        # Verify credentials
        headers = {
            "Authorization": f"Bearer {auth_data['access_token']}"
        }
        verify_response = requests.get(
            f"https://{request.json['instance']}/api/v1/accounts/verify_credentials",
            headers=headers
        )
        verify_data = verify_response.json()
        
        if verify_response.status_code >= 400:
            return jsonify({
                'error': verify_data.get('error'),
                'status': verify_response.status_code,
                'statusText': verify_response.reason
            }), verify_response.status_code
            
        # Set the access token in a cookie
        response.set_cookie(
            'access_token',
            auth_data['access_token'],
            httponly=True,
            secure=False,  # Set to True in production
            samesite='Strict',
            max_age=24*60*60  # 1 day
        )
        
        # Set the response data
        response.data = json.dumps({
            'account': verify_data
        })
        response.content_type = 'application/json'
        
        return response
        
    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500