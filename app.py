from flask import Flask
import requests
import psycopg2
import base64
from io import BytesIO
# import redis
import json
import re
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from matplotlib import style
style.use("ggplot")
from wordcloud import WordCloud

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Amatek"

@app.route('/most')
def mostTweet():
    conn = psycopg2.connect(
        database="postgres", user='postgres', password='amatek123', host='dev.amatek.co.id', port='5433'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute('''SELECT text from tweetbysearch''')
    result = cursor.fetchall()
    nltk.download('stopwords')
    stop_words = set(stopwords.words('indonesian'))
    additional_stopwords = ['_', 'lihat', 'lbh', 'thd', 'sesuai', 'rakyat', 'pimpinan', 'kpk', 'bangsa', 'negara',
                            'wa rajiun', 'berbuat', 'berhasil', 'indonesia', 'ttg', 'diduga', 'pimp kpk', 'kemarin',
                            'innalillahi', 'lakukan', 'bicara', 'aamiin', 'pribadi', 'upaya', 'hasil', 'terbaik',
                            'sehat', 'proses', 'kau', 'almarhum', 'pimp ', 'masuk', 'maaf', 'mohon', 'insya',
                            'menerima', 'banget', 'biar', 'kali', 'pd', 'anak', 'cinta', 'apapun', 'doa', 'aja',
                            'langsung', 'bhw', 'gimana', 'anak2', 'adl', 'gua', 'rumah', 'ambil', 'istri', 'kerja',
                            'jalan', 'jg', 'gak', 'inna', 'ilaihi', 'spt', 'mari', 'wa ', 'malam', 'guru', 'jgn', 'mrk',
                            'nama', 'berduka', 'cita', 'sahabat', 'orang2', 'suka', 'org', 'skrg', 'pagi', 'semangat',
                            'keluarga', 'selamat', 'swt', 'allah', 'sdh', 'dr', 'tp', 'dlm', 'ya', 'ga', 'yg', 'amp',
                            'tdk', 'sbg', 'dng', '_', 'dng', 'semoga', 'utk', 'orang', 'dgn', 'krn', 'terima', 'kasih',
                            'kalo', 'sy', 'jd', 'alhamdulillah', 'dg', 'salah', 'beliau', 'minggu', 'senin', 'gacoan']
    stop_words.update(additional_stopwords)
    def remove_stopwords(text):
        words = text.lower().split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        return ' '.join(filtered_words)
    tweets = []
    tweets_data = result
    for tweet in tweets_data:
        full_text = tweet[0]
        full_text = re.sub(r'http\S+', '', full_text)
        full_text = re.sub('[^a-zA-Z0-9\s]', '', full_text)
        tweets.append(remove_stopwords(full_text))
    text = ' '.join([word for word in tweets])
    plt.figure(figsize=(20, 15), facecolor='white')
    wordcloud = WordCloud(max_words=500, width=1600, height=800).generate(text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    buf = BytesIO()
    plt.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    conn.commit()
    conn.close()
    return f"<html><head><title>MOST</title></head><body><img width='100%' src='data:image/png;base64,{data}'/></body></html>"


@app.route('/recent')
def recentTweet():
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAABqfpgEAAAAAYoKwPE%2BDp23feyjRGcX5eUatCXA%3DLbMIrjQjCKe5w2F0JhPnItX7p012QFQCgCmWPkeUof9hE2mTYG'
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
