from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
import time
import os
import traceback

app = Flask(__name__)

token_ubidots = os.getenv('UBIDOTS_TOKEN', 'BBUS-7c27136034b6495162e6989a04b46627163')
label_perangkat = os.getenv('DEVICE_LABEL', 'ESP32-SIC6')
url_ubidots = f'https://industrial.api.ubidots.com/api/v1.6/devices/{label_perangkat}'
uri_mongodb = os.getenv('MONGODB_URI', 'mongodb+srv://rectoversorpl:j6abIXJ0NpfuVhw@hsc478rectoverso.qluoc.mongodb.net/?retryWrites=true&w=majority&appName=HSC478Rectoverso')
nama_database = 'Rectoverso'
nama_koleksi = 'Data'

mongo_client = MongoClient(uri_mongodb, server_api=ServerApi('1'))
db = mongo_client[nama_database]
koleksi = db[nama_koleksi]
koleksi.create_index([("waktu", 1)])

headers = {
    'x-auth-token': token_ubidots,
    'content-type': 'application/json'
}

@app.route('/data', methods=['POST'])
def terima_data():
    data = request.get_json()

    if not data or 'suhu' not in data or 'kelembapan' not in data or 'gerakan_terdeteksi' not in data:
        return jsonify({'error': 'data tidak lengkap'}), 400

    suhu = data['suhu']
    kelembapan = data['kelembapan']
    gerakan_terdeteksi = data['gerakan_terdeteksi']

    data_mongo = {
        'waktu': time.strftime('%Y-%m-%d %H:%M:%S'),
        'suhu': suhu,
        'kelembapan': kelembapan,
        'gerakan_terdeteksi': gerakan_terdeteksi
    }
    result = koleksi.insert_one(data_mongo)
    print(f"data disimpan ke mongodb dengan id: {result.inserted_id}")

    payload_ubidots = {
        'suhu': suhu,
        'kelembapan': kelembapan,
        'gerakan': gerakan_terdeteksi
    }
    try:
        response = requests.post(url_ubidots, headers=headers, json=payload_ubidots)
        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                print(f"data berhasil dikirim ke ubidots: {response_data}")
            except ValueError:
                print("gagal memparsing respons dari ubidots")
        else:
            print(f"gagal mengirim ke ubidots. status code: {response.status_code}, pesan: {response.text}")
    except Exception as e:
        print(f"error mengirim ke ubidots: {str(e)}")
        traceback.print_exc()

    return jsonify({'message': 'data diterima', 'data': data}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)