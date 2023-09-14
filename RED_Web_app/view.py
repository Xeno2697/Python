from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# cors_allowed_originは本来適切に設定するべき
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')

# ユーザーが新しく接続すると実行
@socketio.on('connect')
def connect(auth):
    print("Connecting")

# ユーザーの接続が切断すると実行
@socketio.on('disconnect')
def disconnect():
    print("disconnected")

"""
# テキストエリアが変更されたときに実行
@socketio.on('text_update_request')
def text_update_request(json):
    global text
    text = json["text"]
    # 変更をリクエストした人以外に向けて送信する
    # 全員向けに送信すると入力の途中でテキストエリアが変更されて日本語入力がうまくできない
    emit('text_update', {'text': text}, broadcast=True, include_self=False)
"""
@socketio.on('move_request')
def move_request(json):
    #モーター変動
    print(json["x"],json["y"])
    return 

if __name__ == '__main__':
    # 本番環境ではeventletやgeventを使うらしいが簡単のためデフォルトの開発用サーバーを使う
    socketio.run(app, debug=True)