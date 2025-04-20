from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests

profile_bp = Blueprint('profile', __name__)

@profile_bp.route("/api/v1/accounts/<id>", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_profile(id):
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        account_response = requests.get(
            f"https://{request.args['instance']}/api/v1/accounts/{id}",
            headers=headers
        )
        account = account_response.json()

        if account_response.status_code >= 400:
            return jsonify({
                'error': account.get('error'),
                'status': account_response.status_code,
                'statusText': account_response.reason
            }), account_response.status_code

        statuses_response = requests.get(
            f"https://{request.args['instance']}/api/v1/accounts/{id}/statuses",
            headers=headers
        )
        statuses = statuses_response.json()

        if statuses_response.status_code >= 400:
            return jsonify({
                'error': statuses.get('error'),
                'status': statuses_response.status_code,
                'statusText': statuses_response.reason
            }), statuses_response.status_code

        return jsonify({
            'account': account,
            'statuses': {
                'count': len(statuses),
                'list': statuses
            }
        })

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route("/api/v1/accounts", methods=['PATCH'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def edit_profile():
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        body = {
            'display_name': request.json['display_name'],
            'note': request.json['note'],
        }
        headers = {
            'Authorization': f"Bearer {access_token}"
        }
        response = requests.patch(
            f"https://{request.json['instance']}/api/v1/accounts/update_credentials",
            headers=headers,
            json=body
        )
        edit_profile = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': edit_profile.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(edit_profile)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route("/api/v1/accounts/<id>/followers", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_followers(id):
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(
            f"https://{request.args['instance']}/api/v1/accounts/{id}/followers",
            headers=headers
        )
        followers = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': followers.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify({
            'accounts': followers,
            'max_id': followers[-1]['id'] if followers else None
        })

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@profile_bp.route("/api/v1/accounts/<id>/following", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_following(id):
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(
            f"https://{request.args['instance']}/api/v1/accounts/{id}/following",
            headers=headers
        )
        following = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': following.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify({
            'accounts': following,
            'max_id': following[-1]['id'] if following else None
        })

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
