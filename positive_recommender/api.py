from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import requests
import json
from vikalp_base_api import viaklp_bp
from sentiment_analysis import analyzeSentiment

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['DOMAIN'] = "http://localhost:3000"

#search
@app.get("/api/v1/search")
@cross_origin()
def search():
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'q': request.args['q']
        }
        response = requests.get(f"https://{request.args['instance']}/api/v2/search", params=params, headers=headers)
        results = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': results['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            sent = analyzeSentiment(results['statuses'])
            data = {
                'accounts': results['accounts'],
                'statuses': sent,
                'hashtags': results['hashtags']
            }
            return data

#fetch tag timeline
@app.get("/api/v1/timelines/tag/<name>")
@cross_origin()
def get_tag_timeline(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'max_id': request.args['max_id']
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/tag/{name}?limit=50", params=params, headers=headers)
        tag_timeline = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': tag_timeline['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            sent = analyzeSentiment(tag_timeline)
            data = {
                'data': sent,
                'max_id': tag_timeline[-1]['id']
            }
            return data
        
#fetch home timeline
@app.get("/api/v1/timelines/home")
@cross_origin()
def get_timeline():
    #print(request.args)
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        params = {
            'max_id': request.args['max_id'] #posts[len(posts) - 1].id
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/home?limit=20", headers=headers, params=params)
        timeline = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': timeline['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            sent = analyzeSentiment(timeline)
            data = {
                'data': sent,
                'max_id': timeline[-1]['id']
            }
            return data
        
app.register_blueprint(viaklp_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
