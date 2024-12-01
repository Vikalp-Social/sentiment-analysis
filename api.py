from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
import requests
import json
import os

# Sentiment Analyzer Dependencies
import time
import torch
from bs4 import BeautifulSoup
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
domain = "https://vikalp.social"

# Check if Sentiment Analyzer model is already downloaded
folder = 'sentimentAnalyzerFolder'
def check_folder_exists(folder_path):
    return os.path.isdir(folder_path)

if not check_folder_exists(folder):
    # DistilBERT Model Parameters
    modelName = "distilbert-base-uncased-finetuned-sst-2-english"
    model = DistilBertForSequenceClassification.from_pretrained(modelName)
    tokenizer = DistilBertTokenizer.from_pretrained(modelName)

    # Set model to evaluation mode
    model.eval()

    # Save Pre-trained models so that it is not downloaded repeatedly
    localDir = "./sentimentAnalyzerFolder"
    model.save_pretrained(localDir)
    tokenizer.save_pretrained(localDir)
    print(f"Model and tokenizer saved to {localDir}")

# Model Parameters
localDir = "./sentimentAnalyzerFolder"
model = DistilBertForSequenceClassification.from_pretrained(localDir)
tokenizer = DistilBertTokenizer.from_pretrained(localDir)
model.eval()
torch.backends.quantized.engine = 'qnnpack'
print("Model and tokenizer loaded from the local directory")

# Encode Sentiment Label to value
label_to_value = {
    'NEGATIVE': -1,
    'POSITIVE': 1
}

# Analyze Sentiment of Posts
def analyzeSentiment(toots):
    results = []
    for t in toots:
        if t.get('language', None) == 'en' or (t.get('reblog', {}) and t.get('reblog', {}).get('language', None) == 'en'):
            results.append(t)

    def getProbability(model, text):
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        return probabilities

    def getSentiment(text):
        # Process HTML Text to obtain Plain Text
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text()

        # Analyze Sentiment
        probabilities = getProbability(model, plain_text)
        prediction = torch.argmax(probabilities, dim=-1).item()
        label = model.config.id2label[prediction]
        return label_to_value[label]

    # Get list of positive and negative posts
    positivePosts = []
    negativePosts = []
    for row in results:
        if row['content'] and getSentiment(row['content']) == 1:
            positivePosts.append(row)
        elif row['content'] and getSentiment(row['content']) == -1:
            negativePosts.append(row)
        elif 'reblog' in row and row['reblog'] and getSentiment(row['reblog']['content']) == 1:
            positivePosts.append(row)
        elif 'reblog' in row and row['reblog'] and getSentiment(row['reblog']['content']) == -1:
            negativePosts.append(row)

    # Return positive posts
    return positivePosts

@app.get("/api/v1/health")
@cross_origin()
def health():
    return {
        'status': 'ok'
    }

#register app
@app.post("/api/v1/register")
@cross_origin()
def register_app():
    try:
        body = {
            'client_name': "Vikalp",
            'redirect_uris': f"{domain}/auth/",
            'scopes': "read write push",
            'website': f"{domain}"
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
@app.post("/api/v1/auth")
@cross_origin()
def get_auth_token():
    #print(request.json)
    try:
        body = {
            'client_id': request.json['id'],
            'client_secret': request.json['secret'],
            'redirect_uri': f"{domain}/auth/",
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

#fetch user account data
@app.get("/api/v1/accounts/<id>")
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
@app.patch("/api/v1/accounts")
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
@app.get("/api/v1/accounts/<id>/followers")
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
@app.get("/api/v1/accounts/<id>/following")
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

#follow a user
@app.post("/api/v1/accounts/<id>/follow")
@cross_origin()
def follow_user(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/follow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow

#follow a tag
@app.post("/api/v1/tags/<name>/follow")
@cross_origin()
def follow_tag(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/follow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow
        
#get following tags
@app.get("/api/v1/tags/following")
@cross_origin()
def get_following_tags():
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        response = requests.get(f"https://{request.args['instance']}/api/v1/followed_tags", headers=headers)
        tags = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': tags['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return tags

#unfollow a user
@app.post("/api/v1/accounts/<id>/unfollow")
@cross_origin()
def unfollow_user(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/unfollow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow

#unfollow a tag
@app.post("/api/v1/tags/<name>/unfollow")
@cross_origin()
def unfollow_tag(name):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/unfollow", headers=headers)
        follow = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': follow['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return follow

#post a status
@app.post("/api/v1/statuses")
@cross_origin()
def post_status():
    try:
        body = {
            'status': request.json['message'],
            'media_ids': request.json['media_ids'],
            'in_reply_to_id': request.json['reply_id'],
        }
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses", headers=headers, json=body)
        post_status = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': post_status['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return post_status

#edit a status
@app.put("/api/v1/statuses/<id>")
@cross_origin()
def edit_status(id):
    try:
        body = {
            'status': request.json['text']
        }
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.put(f"https://{request.json['instance']}/api/v1/statuses/{id}", json=body, headers=headers)
        edit_status = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': edit_status['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return edit_status

#favorite or unfavourite a status
@app.post("/api/v1/statuses/<id>/favourite")
@cross_origin()
def favourite(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}favourite", headers=headers)
        favourite = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': favourite['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return favourite

#boost or unboost a status
@app.post("/api/v1/statuses/<id>/boost")
@cross_origin()
def boost(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.json['token']}"
        }
        response = requests.post(f"https://{request.json['instance']}/api/v1/statuses/{id}/{request.json['prefix']}reblog", headers=headers)
        boost = json.loads(response.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if response.status_code >= 400:
            return ({
            'error': boost['error'],
            'status': response.status_code,
            'statusText': response.reason,
        }, response.status_code)
        else:
            return boost

#fetch a status
@app.get("/api/v1/statuses/<id>")
@cross_origin()
def get_status(id):
    try:
        headers = {
            "Authorization": f"Bearer {request.args['token']}"
        }
        res1 = requests.get(f"https://{request.args['instance']}/api/v1/statuses/{id}", headers=headers)
        status = json.loads(res1.text)
        res2 = requests.get(f"https://{request.args['instance']}/api/v1/statuses/{id}/context", headers=headers)
        replies = json.loads(res2.text)
    except requests.exceptions.ConnectionError as e:
        return {
                'error': "Can't Establish a connection to the server",
                'status': 502,
                'statusText': "Bad Gateway",
            }
    else:
        if res1.status_code >= 400:
            return ({
            'error': status['error'],
            'status': res1.status_code,
            'statusText': res1.reason,
        }, res1.status_code)
        else:
            data = {
                'status': status,
                'replies': replies['descendants']
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
