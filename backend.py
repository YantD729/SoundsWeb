from geopy import distance
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

# 定义一个全局的字典变量，作为数据库
database = {}

@app.route('/upload', methods=['POST'])
def upload_sound():
    # 获取上传的声音文件及相关信息
    sound_file = request.files['sound_file']
    sound_name = request.form['sound_name']
    sound_description = request.form['sound_description']

    # 将声音文件及相关信息保存到数据库中
    database[sound_name] = {
        'file': sound_file.read(),
        'description': sound_description
    }

    return 'Upload successful'

@app.route('/play/<sound_name>', methods=['GET'])
def play_sound(sound_name):
    # 从数据库中获取声音文件及相关信息
    sound_data = database.get(sound_name)

    if sound_data:
        # 返回声音文件及相关信息
        return jsonify(sound_data)
    else:
        return 'Sound not found'
    
@app.route('/api/sound_data')
def get_sound_data():
    # 从文件中读取音乐数据并解析为 Python 对象
    with open('sound_data.json', 'r') as f:
        sound_data = json.load(f)

    return jsonify(sound_data)

@app.route('/api/find_nearest_sound', methods=['POST'])
def find_nearest_sound():
    user_location = request.json['location']  # 用户的地理位置信息
    with open('sound_data.json', 'r') as f:
        sound_data = json.load(f)

    nearest_sound = None
    nearest_distance = float('inf')
    for sound in sound_data:
        sound_location = sound['location']
        d = distance.distance(user_location, sound_location).km  # 计算距离
        if d < nearest_distance:
            nearest_sound = sound
            nearest_distance = d

    return jsonify(nearest_sound)