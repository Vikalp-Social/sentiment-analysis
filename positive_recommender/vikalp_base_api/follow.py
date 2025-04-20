from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
import requests

follow_bp = Blueprint('follow', __name__)

@follow_bp.route("/api/v1/accounts/<id>/follow", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def follow(id):
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
        response = requests.post(
            f"https://{request.json['instance']}/api/v1/accounts/{id}/follow",
            headers=headers
        )
        follow = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': follow.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(follow)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/accounts/<id>/unfollow", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def unfollow(id):
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
        response = requests.post(
            f"https://{request.json['instance']}/api/v1/accounts/{id}/unfollow",
            headers=headers
        )
        unfollow = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': unfollow.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(unfollow)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/accounts/<id>/followers", methods=['GET'])
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

        return jsonify(followers)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/accounts/<id>/following", methods=['GET'])
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

        return jsonify(following)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/tags/<name>/follow", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def follow_tag(name):
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
        response = requests.post(
            f"https://{request.json['instance']}/api/v1/tags/{name}/follow",
            headers=headers
        )
        follow_tag = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': follow_tag.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(follow_tag)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/tags/<name>/unfollow", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def unfollow_tag(name):
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
        response = requests.post(
            f"https://{request.json['instance']}/api/v1/tags/{name}/unfollow",
            headers=headers
        )
        unfollow_tag = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': unfollow_tag.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(unfollow_tag)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@follow_bp.route("/api/v1/tags/following", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_followed_tags():

    print('fetching followed tags')

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
            f"https://{request.args['instance']}/api/v1/followed_tags",
            headers=headers
        )
        followed_tags = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': followed_tags.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        print(followed_tags)
        
        return jsonify(followed_tags)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        