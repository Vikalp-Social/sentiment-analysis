from flask import Flask, request, jsonify, Response, make_response
from flask_cors import CORS, cross_origin
import requests
import json
import bcrypt
from datetime import datetime, timedelta
import pytz
from vikalp_base_api import viaklp_bp
from sentiment_analysis import analyzeSentiment
import urllib.parse

app = Flask(__name__)
cors = CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3001"}})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['DOMAIN'] = "http://localhost:3001"

def is_within_last_hour(timestamp_str):
    try:
        input_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now(pytz.UTC)
        one_hour_ago = now - timedelta(hours=1)
        return one_hour_ago <= input_date <= now
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return False

def track_metrics(req, res):

    try:
        metrics_token = request.cookies.get('metrics_token')
        if not metrics_token:
            return


        # URL decode the metrics token before parsing as JSON
        decoded_metrics_token = urllib.parse.unquote(metrics_token)        
        metrics_data = json.loads(decoded_metrics_token)

        uid = metrics_data.get('uid')
        experience = metrics_data.get('experience')
        last_db_update = metrics_data.get('lastDBUpdate')
        algo = metrics_data.get('algo')

        if not all([uid, experience, last_db_update]):
            return

        print(last_db_update, is_within_last_hour(last_db_update))

        if not is_within_last_hour(last_db_update):
            # Hash the UID for security
            salt = bcrypt.gensalt()
            hashed_uid = bcrypt.hashpw(uid.encode(), salt).decode()

            # Send metrics to auth service
            try:
                requests.post(
                    'https://auth.srg.social/api/v1/metric/log/activeUser',
                    json={
                        'lastDBUpdate': last_db_update,
                        'uid': hashed_uid,
                        'exp': experience,
                        'algo': algo
                    }
                )
            except Exception as e:
                print(f"Error sending metrics: {e}")

            # Update the cookie with new timestamp
            metrics_data['lastDBUpdate'] = datetime.now(pytz.UTC).isoformat()
            
            # Set the updated cookie in the response
            res.set_cookie(
                'metrics_token',
                json.dumps(metrics_data),
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Strict',
                max_age=24*60*60  # 1 day
            )

    except json.JSONDecodeError as e:
        print('Error in metrics tracking: Invalid JSON format -', str(e))
    except Exception as e:
        print('Error in metrics tracking:', str(e))

#search
@app.get("/api/v1/search")
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def search():
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
            'q': request.args['q']
        }
        search_response = requests.get(f"https://{request.args['instance']}/api/v2/search", params=params, headers=headers)
        results = search_response.json()
        
        if search_response.status_code >= 400:
            return jsonify({
                'error': results.get('error'),
                'status': search_response.status_code,
                'statusText': search_response.reason
            }), search_response.status_code
            
        sent = analyzeSentiment(results['statuses'])
        data = {
            'accounts': results['accounts'],
            'statuses': sent,
            'hashtags': results['hashtags']
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

#fetch tag timeline
@app.get("/api/v1/timelines/tag/<name>")
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
            
        sent = analyzeSentiment(tag_timeline)
        data = {
            'data': sent,
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
@app.get("/api/v1/timelines/home")
@cross_origin(origin="http://localhost:3001", supports_credentials=True)
def get_timeline():
    try:
        # Create response object
        response = make_response()
        
        # Track metrics
        track_metrics(request, response)
        
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
        
        # Analyze sentiment of the timeline
        sent = analyzeSentiment(timeline)
        
        # Prepare response data
        data = {
            'data': sent,
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
        
app.register_blueprint(viaklp_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
