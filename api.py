from flask import Flask, request, jsonify
import requests
from flask_cors import CORS, cross_origin
import json
# import pandas as pd
# from transformers import pipeline
# from tqdm import tqdm

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# # # Create the sentiment analysis pipeline
# sentiment_task = pipeline("sentiment-analysis", model=model_name, tokenizer=model_name, max_length=512, truncation=True)

# label_to_value = {
#     'negative': -1,
#     'neutral': 0,
#     'positive': 1
# }

# def sentiment_anal(toots):
#     results = []
#     for t in toots:
#         if t.get('language', None) == 'en' or (t.get('reblog', {}) and t.get('reblog', {}).get('language', None) == 'en'):
#             results.append(t)


#     # print(results)
#     # Convert results list into a Pandas DataFrame
#     mastodon_df = pd.DataFrame(results)

#     """## Predicting using RoBERTa model"""

#     def get_sentiment(text):
#         result = sentiment_task(text)
#         label = result[0]['label']
#         return label_to_value[label]

#     def apply_sentiment(row):
#         if pd.notna(row['content']):
#             return get_sentiment(row['content'])
#         elif 'reblog' in row and pd.notna(row['reblog']['content']):
#             return get_sentiment(row['reblog']['content'])
#         else:
#             return 0

#     tqdm.pandas()
#     mastodon_df['pred_sentiment'] = mastodon_df.progress_apply(apply_sentiment, axis=1)
#     positive_sentiment_df = mastodon_df[mastodon_df['pred_sentiment'] == 1]
#     sent_list = positive_sentiment_df.to_dict('records')
#     return sent_list

#register app
@app.post("/api/v1/register")
@cross_origin()
def register_app():
    #print(request.json)
    body = {
        'client_name': "Vikalp",
        'redirect_uris': "http://localhost:3001/auth",
        'scopes': "read write push",
        'website': "http://localhost:3001"
    }
    response = requests.post(f"https://{request.json['instance']}/api/v1/apps", json=body)
    register_app = json.loads(response.text)
    #print(register_app)
    return jsonify(register_app)
    #return "helo"

#authenticate user
@app.post("/api/v1/auth")
@cross_origin()
def get_auth_token():
    #print(request.json)
    body = {
        'client_id': request.json['id'],
        'client_secret': request.json['secret'],
        'redirect_uri': "http://localhost:3001/auth",
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
    return jsonify({
        'account': verify,
        'token': auth['access_token']
    })

#fetch user account data
@app.get("/api/v1/accounts/<id>")
@cross_origin()
def get_profile(id):
    res1 = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}")
    account = json.loads(res1.text)
    res2 = requests.get(f"https://{request.args['instance']}/api/v1/accounts/{id}/statuses")
    statuses = json.loads(res2.text)
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
    body = {
        'display_name': request.json['display_name'],
        'note': request.json['note'],
    }
    headers = {
        'Authorization': f"Bearer {request.json['token']}"
    }
    response = requests.patch(f"https://{request.json['instance']}/api/v1/accounts/update_credentials", headers=headers, json=body)
    edit_profile = json.loads(response.text)
    print(edit_profile)
    return edit_profile
    
#search
@app.get("/api/v1/search")
@cross_origin()
def search():
    headers = {
        "Authorization": f"Bearer {request.args['token']}"
    }
    params = {
        'q': request.args['q']
    }
    response = requests.get(f"https://{request.args['instance']}/api/v2/search", params=params, headers=headers)
    results = json.loads(response.text)
    #print(results)
    data = {
        'accounts': results['accounts'],
        'statuses': results['statuses'],
        'hashtags': results['hashtags']
    }
    return data

#follow a user
@app.post("/api/v1/accounts/<id>/follow")
@cross_origin()
def follow_user(id):
    headers = {
        "Authorization": f"Bearer {request.json['token']}"
    }
    response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/follow", headers=headers)
    follow = json.loads(response.text)
    return follow

#follow a tag
@app.post("/api/v1/tags/<name>/follow")
@cross_origin()
def follow_tag(name):
    headers = {
        "Authorization": f"Bearer {request.json['token']}"
    }
    response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/follow", headers=headers)
    follow = json.loads(response.text)
    return follow

# //unfollow a user
# app.post("/api/v1/accounts/:id/unfollow", async (req, res) => {
#     try {
#         const response = await axios.post(`https://${req.body.instance}/api/v1/accounts/${req.params.id}/unfollow`, {}, {
#             headers: {
#                 Authorization: `Bearer ${req.body.token}`,
#             },
#         });
#         res.status(200).json(response.data);

# //unfollow a tag
# app.post("/api/v1/tags/:name/unfollow", async (req, res) => {
#     try {
#         const response = await axios.post(`https://${req.body.instance}/api/v1/tags/${req.params.name}/unfollow`, {}, {
#             headers: {
#                 Authorization: `Bearer ${req.body.token}`,
#             },
#         });
#         res.status(200).json(response.data);

#follow a user
@app.post("/api/v1/accounts/<id>/unfollow")
@cross_origin()
def unfollow_user(id):
    headers = {
        "Authorization": f"Bearer {request.json['token']}"
    }
    response = requests.post(f"https://{request.json['instance']}/api/v1/accounts/{id}/unfollow", headers=headers)
    follow = json.loads(response.text)
    return follow

#follow a tag
@app.post("/api/v1/tags/<name>/unfollow")
@cross_origin()
def unfollow_tag(name):
    headers = {
        "Authorization": f"Bearer {request.json['token']}"
    }
    response = requests.post(f"https://{request.json['instance']}/api/v1/tags/{name}/unfollow", headers=headers)
    follow = json.loads(response.text)
    return follow

#post a status
@app.post("/api/v1/statuses")
@cross_origin()
def post_status():
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
    return post_status

#edit a status
#favorite or unfavourite a status
#boost or unboost a status
#fetch a status
#fetch tag timeline

#fetch home timeline
@app.get("/api/v1/timelines/home")
@cross_origin()
def get_timeline():
    #print(request.args)
    headers = {
        "Authorization": f"Bearer {request.args['token']}"
    }
    params = {
        'max_id': request.args['max_id']
    }
    response = requests.get(f"https://{request.args['instance']}/api/v1/timelines/home?limit=30", headers=headers, params=params)
    timeline = json.loads(response.text)
    #sent = sentiment_anal(timeline)
    data = {
        'data': timeline,
        'max_id': timeline[-1]['id']
    }
    #print(data)
    return data

if __name__ == '__main__':
    app.run(debug=True, port=3000)
