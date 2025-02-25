import time
import machine
import dht
import requests

dht_pin = machine.Pin(4, machine.Pin.IN)
pir_pin = machine.Pin(15, machine.Pin.IN)

dht_sensor = dht.DHT11(dht_pin)

import network
ssid_wifi = 'Xiaomi 13T'
#kata_sandi_wifi = 'your_wifi_password'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('menghubungkan ke wifi...')
    wlan.connect(ssid_wifi)
    while not wlan.isconnected():
        pass
print('terhubung ke wifi:', wlan.ifconfig())

url_flask = 'http://128.199.101.121:5000/data'

def baca_dht11():
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembapan = dht_sensor.humidity()
        return suhu, kelembapan
    except:
        return None, None

def kirim_data(suhu, kelembapan, gerakan):
    if suhu is not None and kelembapan is not None:
        data = {
            'suhu': suhu,
            'kelembapan': kelembapan,
            'gerakan_terdeteksi': gerakan
        }
        try:
            response = requests.post(url_flask, json=data)  # Mengganti urequests dengan requests
            print(f"data dikirim ke flask: {response.text}")
            response.close()
        except Exception as e:
            print(f"error mengirim data ke flask: {e}")

while True:
    gerakan = pir_pin.value()
    
    if gerakan == 1:
        print("gerakan terdeteksi! mengirim data...")
        suhu, kelembapan = baca_dht11()
        kirim_data(suhu, kelembapan, gerakan == 1)
    else:
        print("tidak ada gerakan, tidak mengirim data.")
    
    time.sleep(5)
