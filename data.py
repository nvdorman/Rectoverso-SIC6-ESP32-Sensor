import time
import machine
import dht
import urequests

dht_pin = machine.pin(4, machine.pin.in)
pir_pin = machine.pin(15, machine.pin.in)

dht_sensor = dht.dht11(dht_pin)

import network
ssid_wifi = 'Xiaomi 13T'
#kata_sandi_wifi = 'your_wifi_password'

wlan = network.wlan(network.sta_if)
wlan.active(true)
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
        return none, none

def kirim_data(suhu, kelembapan, gerakan):
    if suhu is not none and kelembapan is not none:
        data = {
            'suhu': suhu,
            'kelembapan': kelembapan,
            'gerakan_terdeteksi': gerakan
        }
        try:
            response = urequests.post(url_flask, json=data)
            print(f"data dikirim ke flask: {response.text}")
            response.close()
        except:
            print("error mengirim data ke flask:")

while true:
    gerakan = pir_pin.value()
    
    if gerakan == 1:
        print("gerakan terdeteksi! mengirim data...")
        suhu, kelembapan = baca_dht11()
        kirim_data(suhu, kelembapan, gerakan == 1)
    else:
        print("tidak ada gerakan, tidak mengirim data.")
    
    time.sleep(5)