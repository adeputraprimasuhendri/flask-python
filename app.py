from flask import Flask
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Amatek"


@app.route('/recent-tweet')
def recentTweet():
    bearer_token = 'TOKEN_HERE'
    search_url = "https://api.twitter.com/2/tweets/search/recent"
    query_params = {
        'query': '(from:aniesbaswedan -is:retweet) '
                 'OR (from:prabowo -is:retweet) '
                 'OR (from:ganjarpranowo -is:retweet) '
                 'OR (from:AgusYudhoyono -is:retweet)',
        'tweet.fields': 'author_id,created_at', 'max_results': 100}

    def bearer_oauth(r):
        r.headers["Authorization"] = f"Bearer {bearer_token}"
        r.headers["User-Agent"] = "v2RecentSearchPython"
        return r

    def connect_to_endpoint(url, params):
        response = requests.get(url, auth=bearer_oauth, params=params)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    json_response = connect_to_endpoint(search_url, query_params)
    tweet = json.loads(json.dumps(json_response, indent=4, sort_keys=True))
    return tweet

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
