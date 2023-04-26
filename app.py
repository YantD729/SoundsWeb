from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from geopy import distance
from flask import Flask, request, jsonify

# 用一个简单的字典作为数据库来存储声音信息
sound_dict = {}

app = Flask(__name__)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print("do post")
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        sound_data = json.loads(body.decode('utf-8'))

        if self.path == '/upload':
            return upload_sound()
        elif self.path == '/play':
            return play_sound()
        elif self.path == '/sounds':
            return get_all_sounds()
        else:
            self.send_error(404)
    
    def do_GET(self):
        print("do get")
        if self.path.startswith('/sounds/'):
            return get_all_sounds()
        elif self.path == ('/locations'):
            print(get_sound_locations())
            return get_sound_locations()
        else:
            self.send_error(404)
            
def start_server():
    # 创建 HTTP 服务器
    server = HTTPServer(('localhost', 5500), SimpleHTTPRequestHandler)

    # 启动服务器并监听请求
    server.serve_forever()

@app.after_request
def set_response_headers(response):
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route('/upload', methods=['POST'])
def upload_sound():
    app.logger.info("uploading sounds!")
    # 获取上传的声音文件和位置信息
    sound_file = request.files['sound_file']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    # 将声音文件保存到本地特定的文件夹中
    filename = secure_filename(sound_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    sound_file.save(filepath)

    # 将声音信息添加到字典中
    sound_dict[filename] = {
        'location': {'latitude': latitude, 'longitude': longitude},
        'file_path': filepath
    }

    # 返回成功上传的响应
    response = {'status': 'success'}
    return jsonify(response)

@app.route('/sounds', methods=['GET'])
def get_all_sounds():
    # 遍历所有声音，获取所有声音的文件名
    sound_filenames = [f"{location}.mp3" for location in sound_dict.keys()]
    print(sound_filenames)
    # 返回所有声音文件名
    return jsonify("sounds")

@app.route('/locations', methods=['GET'])
def get_sound_locations():
    # 获取所有声音的位置信息
    sound_locations = list(sound_dict.keys())

    # 返回所有声音位置信息
    response = {'locations': sound_locations}
    app.logger.info(response)
    return jsonify(response)


@app.route('/play', methods=['POST'])
def play_sound():
    # 获取用户的实时位置信息
    user_location = request.json['location']

    # 遍历所有声音，找到最接近用户的声音
    min_dist = float('inf')
    min_sound = None
    for sound_location in sound_dict.keys():
        # 计算用户位置和声音位置之间的距离
        dist = distance.distance(user_location, sound_location).km

        # 如果这个声音比之前最接近用户的声音更接近，更新最接近的声音
        if dist < min_dist:
            min_dist = dist
            min_sound = sound_dict[sound_location]

    # 返回最接近用户的声音
    response = {'file': min_sound}
    return jsonify(response)

if __name__ == '__main__':
    HOST = '5500'
    app.run(host=HOST, debug=True)
    # start_server()
    # 启动服务器前先从 JSON 文件中加载声音信息
    with open('sound_data.json', 'r') as f:
        sound_dict = json
