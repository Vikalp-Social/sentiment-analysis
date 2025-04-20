from flask import Blueprint, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests

search_bp = Blueprint('search', __name__)

@search_bp.route("/api/v1/search", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def search():
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
        params = {
            'q': request.args['q'],
            'type': request.args['type']
        }
        response = requests.get(
            f"https://{request.args['instance']}/api/v2/search",
            headers=headers,
            params=params
        )
        search_results = response.json()

        if response.status_code >= 400:
            return jsonify({
                'error': search_results.get('error'),
                'status': response.status_code,
                'statusText': response.reason
            }), response.status_code

        return jsonify(search_results)

    except requests.exceptions.ConnectionError as e:
        return jsonify({
            'error': "Can't Establish a connection to the server",
            'status': 502,
            'statusText': "Bad Gateway"
        }), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500
