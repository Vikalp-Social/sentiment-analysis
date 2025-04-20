from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import json
import requests


status_bp = Blueprint('status', __name__)


#post a status
# POST
@status_bp.route("/api/v1/statuses", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)

def post_status():
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        body = {
            'status': request.json['message'],
            'media_ids': request.json['media_ids'],
            'in_reply_to_id': request.json['reply_id'],
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.post(
            f"https://{request.json['instance']}/api/v1/statuses",
            headers=headers,
            json=body
        )
        post_status = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': post_status.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(post_status)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#edit a status
# PUT
@status_bp.route("/api/v1/statuses/<id>", methods=['PUT'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)

def edit_status(id):
    try:
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': 'Unauthorized',
                'status': 401,
                'statusText': 'No access token found'
            }), 401

        body = {
            'status': request.json['text']
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.put(
            f"https://{request.json['instance']}/api/v1/statuses/{id}",
            json=body,
            headers=headers
        )
        edit_status = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': edit_status.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(edit_status)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#favorite or unfavourite a status
# POST
@status_bp.route("/api/v1/statuses/<id>/favourite", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)

def favourite(id):
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
            f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}favourite",
            headers=headers
        )
        favourite = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': favourite.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(favourite)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#boost or unboost a status
# POST
@status_bp.route("/api/v1/statuses/<id>/boost", methods=['POST'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)

def boost(id):
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
            f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}reblog",
            headers=headers
        )
        boost = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': boost.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(boost)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#fetch a status
# GET
@status_bp.route("/api/v1/statuses/<id>", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)

def get_status(id):
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
        status_response = requests.get(
            f"https://{request.args['instance']}/api/v1/statuses/{id}",
            headers=headers
        )
        status = status_response.json()

        if status_response.status_code >= 400:
            return jsonify({
                'error': status.get('error'),
                'status': status_response.status_code,
                'statusText': status_response.reason
            }), status_response.status_code

        context_response = requests.get(
            f"https://{request.args['instance']}/api/v1/statuses/{id}/context",
            headers=headers
        )
        replies = context_response.json()

        if context_response.status_code >= 400:
            return jsonify({
                'error': replies.get('error'),
                'status': context_response.status_code,
                'statusText': context_response.reason
            }), context_response.status_code

        return jsonify({
            'status': status,
            'replies': replies['descendants']
        })

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
