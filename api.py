from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests
import time
import os
import traceback
import json

app = Flask(__name__)

token_ubidots = os.getenv('UBIDOTS_TOKEN', 'BBUS-TAWAdWpGJcSRtzKQgr29A75LBGRtTI')
label_perangkat = os.getenv('DEVICE_LABEL', 'esp32-sic6')
url_ubidots = f'https://industrial.api.ubidots.com/api/v1.6/devices/{label_perangkat}'
uri_mongodb = os.getenv('MONGODB_URI', 'mongodb+srv://rectoversorpl:QJhW0ZxrBTlfIa5U@hsc478rectoverso.qluoc.mongodb.net/?retryWrites=true&w=majority&appName=HSC478Rectoverso')
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
    try:
        data = request.get_json()
        if not data or 'suhu' not in data or 'kelembapan' not in data or 'gerakan_terdeteksi' not in data:
            return jsonify({'error': 'data tidak lengkap'}), 400

        suhu = float(data['suhu'])
        kelembapan = float(data['kelembapan'])
        gerakan_terdeteksi = int(data['gerakan_terdeteksi'])

        if gerakan_terdeteksi not in [0, 1]:
            return jsonify({'error': 'nilai gerakan_terdeteksi harus 0 atau 1'}), 400

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
            response = requests.post(url_ubidots, headers=headers, json=payload_ubidots, timeout=10)
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    print(f"data berhasil dikirim ke ubidots: {response_data}")
                except ValueError:
                    print("gagal memparsing respons dari ubidots")
            else:
                print(f"gagal mengirim ke ubidots. status code: {response.status_code}, pesan: {response.text}")
        except requests.RequestException as e:
            print(f"error mengirim ke ubidots: {str(e)}")
            traceback.print_exc()

        return jsonify({'message': 'data diterima', 'data': data}), 200

    except Exception as e:
        print(f"error umum: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'terjadi kesalahan server', 'detail': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
