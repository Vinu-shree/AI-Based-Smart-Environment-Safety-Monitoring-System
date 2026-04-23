import network
import urequests
import time
import dht
from machine import Pin, ADC

ssid = "your_ssid"
password = "your_password"

aio_username = "your_username"
aio_key = "your_Aoudafruit_key"

dht_sensor = dht.DHT11(Pin(12))
pir = Pin(15, Pin.IN)

ldr = ADC(26)
gas = ADC(27)

red = Pin(16, Pin.OUT)
orange = Pin(17, Pin.OUT)
blue = Pin(18, Pin.OUT)

buzzer = Pin(14, Pin.OUT)
buzzer.off()

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

print("Connecting WiFi...")
while not wifi.isconnected():
    time.sleep(1)

print("WiFi Connected")
print(wifi.ifconfig())

def send(feed, value):
    url = "https://io.adafruit.com/api/v2/{}/feeds/{}/data".format(aio_username, feed)

    headers = {
        "X-AIO-Key": aio_key,
        "Content-Type": "application/json"
    }

    data = '{"value":"%s"}' % value

    try:
        r = urequests.post(url, headers=headers, data=data)
        r.close()
    except:
        print(feed, "send failed")

def led_safe():
    red.on()
    orange.on()
    blue.off()

def led_warning():
    red.on()
    orange.off()
    blue.on()

def led_danger():
    red.off()
    orange.on()
    blue.on()

while True:

    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
    except:
        temp = 35
        hum = 50

    motion = pir.value()
    light = ldr.read_u16()
    gas_val = gas.read_u16()

    if light < 20000:
        light_status = "BRIGHT"
    elif light < 32000:
        light_status = "MEDIUM"
    else:
        light_status = "DARK"

    if gas_val < 14000:
        gas_status = "SAFE"
    elif gas_val < 20000:
        gas_status = "WARNING"
    else:
        gas_status = "DANGER"

    if temp < 38:
        temp_status = "SAFE"
    elif temp < 45:
        temp_status = "WARNING"
    else:
        temp_status = "DANGER"

    buzzer.off()

    if gas_status == "DANGER" or temp_status == "DANGER":
        status = "DANGER"
        risk = 90
        led_danger()
        buzzer.on()

    elif motion == 1 and light_status == "DARK":
        status = "DANGER"
        risk = 80
        led_danger()
        buzzer.on()

    elif gas_status == "WARNING" or temp_status == "WARNING" or motion == 1 or light_status == "MEDIUM":
        status = "WARNING"
        risk = 60
        led_warning()

    else:
        status = "SAFE"
        risk = 20
        led_safe()

    if status == "DANGER":
        alert = "Critical unsafe environment detected"
    elif status == "WARNING":
        alert = "Warning! Check system conditions"
    else:
        alert = "Environment Safe"

    print("--------------------------------")
    print("Temp:", temp, "C")
    print("Humidity:", hum, "%")
    print("Gas:", gas_val)
    print("Light:", light)
    print("Motion:", motion)
    print("Risk:", risk)
    print("Status:", status)

    send("temperature", temp)
    send("gas", gas_val)
    send("light", light)
    send("motion", motion)
    send("status", status)
    send("risk-score", risk)
    send("alerts", alert)

    time.sleep(1)

