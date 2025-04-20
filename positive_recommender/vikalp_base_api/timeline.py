from flask import Blueprint, Flask, request, jsonify, Response, make_response
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
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_tag_timeline(name):
    try:
        # Create response object
        response = make_response()
        
        # Get auth token from cookies
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': "Authentication token not found",
                'status': 401,
                'statusText': "Unauthorized"
            }), 401
            
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            'max_id': request.args.get('max_id')
        }
        timeline_response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/tag/{name}?limit=50", params=params, headers=headers)
        tag_timeline = timeline_response.json()
        
        if timeline_response.status_code >= 400:
            return jsonify({
                'error': tag_timeline.get('error'),
                'status': timeline_response.status_code,
                'statusText': timeline_response.reason
            }), timeline_response.status_code
            
        data = {
            'data': tag_timeline,
            'max_id': tag_timeline[-1]['id'] if tag_timeline else None
        }
        
        # Set the response data
        response.data = json.dumps(data)
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

#fetch home timeline
# GET
@timeline_bp.route("/api/v1/timelines/home", methods=['GET'])
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_timeline():
    try:
        # Create response object
        response = make_response()
        
        # Get auth token from cookies
        access_token = request.cookies.get('access_token')
        if not access_token:
            return jsonify({
                'error': "Authentication token not found",
                'status': 401,
                'statusText': "Unauthorized"
            }), 401
            
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            'max_id': request.args.get('max_id')
        }
        
        timeline_response = requests.get(
            f"https://{request.args['instance']}/api/v1/timelines/home?limit=20",
            headers=headers,
            params=params
        )
        
        if timeline_response.status_code >= 400:
            error_data = timeline_response.json()
            return jsonify({
                'error': error_data.get('error'),
                'status': timeline_response.status_code,
                'statusText': timeline_response.reason
            }), timeline_response.status_code
            
        timeline = timeline_response.json()
        
        # Prepare response data
        data = {
            'data': timeline,
            'max_id': timeline[-1]['id'] if timeline else None
        }
        
        # Set the response data
        response.data = json.dumps(data)
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